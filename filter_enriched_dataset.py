import pandas as pd
import logging
import numpy as np
import os

# === Setup Logging ===
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# === Load the existing enriched dataset ===
try:
    logger.info("Loading enriched_video_game_dataset.csv...")
    df = pd.read_csv("enriched_video_game_dataset.csv")
    logger.info(f"Loaded {len(df)} rows from enriched_video_game_dataset.csv")
    logger.info(f"Available columns: {df.columns.tolist()}")
except Exception as e:
    logger.error(f"Error loading dataset: {str(e)}")
    raise

# === Define columns to check for empty values ===
# First, let's check which columns actually exist in the dataset
available_columns = df.columns.tolist()
igdb_enriched_columns = [
    col for col in [
        "Developer",
        "Publisher",
        "Platform",
        "Game_Type",
        "Genres_IGDB",
        "Description",
        "Release_Date"
    ] if col in available_columns
]

logger.info(f"Using columns for filtering: {igdb_enriched_columns}")

# === Filter rows with too many missing values ===
# Replace empty strings with NaN for proper counting
df[igdb_enriched_columns] = df[igdb_enriched_columns].replace('', pd.NA)

# Count missing values in IGDB columns for each row
missing_igdb_data_count = df[igdb_enriched_columns].isna().sum(axis=1)

# Keep rows with 3 or fewer missing IGDB values
filtered_df = df[missing_igdb_data_count <= 3].copy()

# Remove Release_Year column if it exists
if 'Release_Year' in filtered_df.columns:
    filtered_df = filtered_df.drop(columns=['Release_Year'])
    logger.info("Removed 'Release_Year' column from the filtered dataset")

logger.info(f"Original rows: {len(df)}")
logger.info(f"Rows after filtering (<= 3 empty IGDB fields): {len(filtered_df)}")

# === Create ID mappings for each category ===
def create_id_mapping(series, is_title=False):
    # For title, we don't split by comma
    if is_title:
        unique_values = set(series.dropna())
    else:
        # Split strings by comma and create a set of unique values
        unique_values = set()
        for value in series.dropna():
            if isinstance(value, str):
                unique_values.update([v.strip() for v in value.split(',')])
    
    # Create DataFrame with IDs
    if unique_values:
        mapping_df = pd.DataFrame({
            'ID': range(1, len(unique_values) + 1),
            'Name': sorted(list(unique_values))
        })
        return mapping_df
    return pd.DataFrame(columns=['ID', 'Name'])

# Create mappings for each category (only for columns that exist)
mappings = {}
# Add Title mapping first (as GameID)
if 'Title' in filtered_df.columns:
    # Create the mapping
    game_mapping = create_id_mapping(filtered_df['Title'], is_title=True)
    mappings['Game'] = game_mapping
    logger.info(f"Created mapping for Game with {len(mappings['Game'])} unique values")
    
    # Create a dictionary for quick lookup
    title_to_id = dict(zip(game_mapping['Name'], game_mapping['ID']))
    
    # Add GameID column to the filtered dataset
    filtered_df['GameID'] = filtered_df['Title'].map(title_to_id)
    logger.info("Added GameID column to the dataset")

# Add other category mappings
for col in ['Genre', 'Directors', 'Developer', 'Publisher', 'Platform', 'Game_Type', 'Genres_IGDB']:
    if col in filtered_df.columns:
        mappings[col] = create_id_mapping(filtered_df[col])
        logger.info(f"Created mapping for {col} with {len(mappings[col])} unique values")

# === Save filtered dataset and mappings ===
try:
    # Create a directory for mappings if it doesn't exist
    os.makedirs('mappings', exist_ok=True)
    
    # Save the filtered dataset
    filtered_df.to_csv("filtered_enriched_video_game_dataset.csv", index=False)
    logger.info("✅ Filtering complete. Saved filtered data to filtered_enriched_video_game_dataset.csv")
    
    # Save each mapping as a separate CSV file
    for col, mapping_df in mappings.items():
        filename = f"mappings/{col.lower()}_mapping.csv"
        mapping_df.to_csv(filename, index=False)
        logger.info(f"✅ Saved {col} mapping to {filename}")
    
except Exception as e:
    logger.error(f"Error saving files: {str(e)}")
    raise 