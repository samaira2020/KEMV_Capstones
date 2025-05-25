import pandas as pd
import asyncio
import aiohttp
from typing import Dict, Optional
import logging
from tqdm import tqdm
import time

# === Setup Logging ===
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# === IGDB Credentials ===
CLIENT_ID = "m2xosg9wqd16iydmaj1wbhujb3d5co"
CLIENT_SECRET = "aebkgaob1uw8bwyqu17d7yz8uktcbu"

# === Load Dataset ===
try:
    df = pd.read_csv("imdb_video_game_rating.csv")
    df['votes'] = df['votes'].str.replace(',', '', regex=True).astype(int)
    df['year'] = df['year'].astype(str).str.extract(r'(\\d{4})')
    df['year'] = pd.to_numeric(df['year'], errors='coerce')
    df = df.rename(columns={
        'title': 'Title',
        'year': 'Release_Year',
        'genre': 'Genre',
        'rating': 'Rating',
        'votes': 'Number_of_Votes',
        'directors': 'Directors',
        'plot': 'Description'
    })
except Exception as e:
    logger.error(f"Error loading dataset: {str(e)}")
    raise

# === Add New Columns ===
df["Developer"] = ""
df["Publisher"] = ""
df["Platform"] = ""
df["Game_Type"] = ""
df["Genres_IGDB"] = ""

# === Authenticate with IGDB ===
import requests

def get_igdb_token() -> str:
    """Get IGDB API token with retry mechanism."""
    auth_url = "https://id.twitch.tv/oauth2/token"
    params = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'grant_type': 'client_credentials'
    }
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = requests.post(auth_url, params=params)
            response.raise_for_status()
            return response.json().get('access_token')
        except requests.exceptions.RequestException as e:
            if attempt == max_retries - 1:
                logger.error(f"Failed to get IGDB token after {max_retries} attempts: {str(e)}")
                raise
            time.sleep(2 ** attempt)  # Exponential backoff

TOKEN = get_igdb_token()
HEADERS = {
    'Client-ID': CLIENT_ID,
    'Authorization': f'Bearer {TOKEN}'
}

# === Async IGDB Query ===
async def fetch_game_details_with_index(session: aiohttp.ClientSession, semaphore: asyncio.Semaphore, index: int, title: str) -> Optional[Dict[str, str]]:
    url = "https://api.igdb.com/v4/games"
    query = f'''
    search "{title}";
    fields name, platforms.name, genres.name,
           involved_companies.company.name, involved_companies.developer,
           involved_companies.publisher, game_modes.name, summary, release_dates.date;
    limit 1;
    '''
    logger.debug(f"Index {index}: Fetching details for \"{title}\" with query: {query}")

    max_retries = 5 # Maximum number of retries
    for attempt in range(max_retries):
        async with semaphore:
            try:
                async with session.post(url, headers=HEADERS, data=query, ssl=False) as response:
                    logger.debug(f"Index {index} (\"{title}\"): API response status: {response.status}")

                    if response.status == 200:
                        data = await response.json()
                        logger.debug(f"Index {index} (\"{title}\"): API response data (first 200 chars): {str(data)[:200]}")
                        if not data:
                            logger.warning(f"Index {index} (\"{title}\"): No data returned from API.")
                            return None # Return None if no data
                        game = data[0]
                        developers = []
                        publishers = []
                        for company in game.get('involved_companies', []):
                            company_name = company.get('company', {}).get('name', '')
                            if company.get('developer'):
                                developers.append(company_name)
                            if company.get('publisher'):
                                publishers.append(company_name)

                        release_date = ''
                        if 'release_dates' in game and game['release_dates']:
                            # Find the earliest release date
                            valid_dates = [rd for rd in game['release_dates'] if rd.get('date') is not None]
                            if valid_dates:
                                earliest_date = min(valid_dates, key=lambda x: x['date'])
                                if isinstance(earliest_date['date'], (int, float)):
                                    release_date = time.strftime('%m/%d/%Y', time.gmtime(earliest_date['date']))

                        return {
                            "index": index,
                            "data": {
                                "Developer": ", ".join(developers) if developers else "",
                                "Publisher": ", ".join(publishers) if publishers else "",
                                "Platform": ", ".join(p['name'] for p in game.get('platforms', [])) if game.get('platforms') else "",
                                "Game_Type": ", ".join(gm['name'] for gm in game.get('game_modes', [])) if game.get('game_modes') else "",
                                "Genres_IGDB": ", ".join(g['name'] for g in game.get('genres', [])) if game.get('genres') else "",
                                "Description": game.get('summary', '') if 'summary' in game else '',
                                "Release_Date_IGDB": release_date
                            }
                        }

                    elif response.status == 429:
                        logger.warning(f"Index {index} (\"{title}\"): Received 429 (Too Many Requests). Retrying in {2 ** attempt} seconds (Attempt {attempt + 1}/{max_retries}).")
                        await asyncio.sleep(2 ** attempt) # Exponential backoff
                    else:
                        logger.warning(f"Index {index} (\"{title}\"): Non-200 response status: {response.status}. Not retrying.")
                        return None # Return None for other non-200 errors

            except aiohttp.ClientError as e:
                logger.warning(f"Index {index} (\"{title}\"): Aiohttp client error during API request: {e}. Retrying in {2 ** attempt} seconds (Attempt {attempt + 1}/{max_retries}).")
                await asyncio.sleep(2 ** attempt) # Exponential backoff on client errors
            except Exception as e:
                logger.error(f"Index {index} (\"{title}\"): Unexpected error during API request: {e}. Not retrying.")
                return None # Return None for unexpected errors

    # If loop finishes without returning, all retries failed
    logger.error(f"Index {index} (\"{title}\"): Failed to fetch data after {max_retries} attempts.")
    return None

async def enrich_all_games(df: pd.DataFrame) -> pd.DataFrame:
    semaphore = asyncio.Semaphore(2)  # Reduced from 3 to 2 to further avoid hitting rate limit
    async with aiohttp.ClientSession() as session:
        tasks = []
        # Ensure the new column exists before populating
        if 'Release_Date_IGDB' not in df.columns:
            df['Release_Date_IGDB'] = ''

        for idx, row in df.iterrows():
            title = row["Title"]
            tasks.append(fetch_game_details_with_index(session, semaphore, idx, title))

        results = []
        # Use tqdm with asyncio.as_completed to show progress as tasks finish
        for future in tqdm(asyncio.as_completed(tasks), total=len(tasks), desc="Enriching dataset"):
            result = await future
            if result:
                results.append(result)

        # Update DataFrame using collected results
        for result in results:
            idx = result["index"]
            data = result["data"]
            for key, value in data.items():
                # Check if the column exists before assigning (skip 'index' key) and is not 'index'
                if key != 'index' and key in df.columns:
                     df.at[idx, key] = value
    return df

# === Main Async Entry ===
if __name__ == "__main__":
    logger.info("Starting async data enrichment process...")
    TOKEN = get_igdb_token()
    HEADERS = {
        'Client-ID': CLIENT_ID,
        'Authorization': f'Bearer {TOKEN}'
    }

    enriched_df = asyncio.run(enrich_all_games(df))

    # === Save Full Enriched Dataset ===
    try:
        enriched_df.to_csv("enriched_video_game_dataset.csv", index=False)
        logger.info("✅ Full enrichment complete. Saved to enriched_video_game_dataset.csv")
    except Exception as e:
        logger.error(f"Error saving full enriched dataset: {str(e)}")
        # Don't raise here, continue to filtering

    # === Filtering rows with too many missing IGDB data ===
    igdb_enriched_columns = [
        "Developer",
        "Publisher",
        "Platform",
        "Game_Type",
        "Genres_IGDB",
        "Description",
        "Release_Date_IGDB"
    ]

    # Replace empty strings with NaN for proper counting (operate on a copy for filtering)
    temp_df_for_filtering = enriched_df[igdb_enriched_columns].replace('', pd.NA)

    # Count missing values in IGDB columns for each row
    missing_igdb_data_count = temp_df_for_filtering.isna().sum(axis=1)

    # Keep rows with 3 or fewer missing IGDB values
    filtered_df = enriched_df[missing_igdb_data_count <= 3].copy()

    logger.info(f"Original rows: {len(enriched_df)}")
    logger.info(f"Rows after filtering (<= 3 empty IGDB fields): {len(filtered_df)}")

    # === Save Filtered Dataset ===
    try:
        # Saving the filtered DataFrame
        filtered_df.to_csv("filtered_enriched_video_game_dataset.csv", index=False)
        logger.info("✅ Filtering complete. Saved filtered data to filtered_enriched_video_game_dataset.csv")
    except Exception as e:
        logger.error(f"Error saving filtered dataset: {str(e)}")
        raise # Raise if saving filtered fails, as this was the user's primary goal for the filtered data
