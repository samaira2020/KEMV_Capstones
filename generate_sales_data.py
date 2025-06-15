import csv
import random
from datetime import datetime, timedelta
from pymongo import MongoClient

# --- CONFIG ---
MONGO_URI = 'mongodb://localhost:27017/'
DB_NAME = 'Capstones'  # Make sure this matches your actual DB name
ENRICHED_COLLECTION = 'enriched_games'
SALES_COLLECTION = 'game_sales'
CSV_FILE = 'game_sales_data.csv'

# --- PARAMETERS ---
REGIONS = ['North America', 'Europe', 'Asia', 'South America', 'Oceania', 'Africa']
START_DATE = datetime(2021, 1, 1)
END_DATE = datetime(2023, 12, 31)

# --- CONNECT TO MONGODB ---
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
enriched_games = db[ENRICHED_COLLECTION]
game_sales = db[SALES_COLLECTION]

# --- FETCH ALL GAMES ---
games = list(enriched_games.find({}))
print(f"Found {len(games)} games in enriched_games.")

sales_records = []

for game in games:
    game_id = game.get('game_id') or game.get('id') or game.get('_id')
    game_name = game.get('game_name') or game.get('Title')
    platform = game.get('platform') or game.get('Platform')
    genre = game.get('genre') or game.get('Genre')
    release_date = game.get('release_date') or game.get('ReleaseDate')
    if isinstance(release_date, str):
        try:
            release_date = datetime.strptime(release_date, '%Y-%m-%d')
        except Exception:
            release_date = START_DATE
    elif not isinstance(release_date, datetime):
        release_date = START_DATE

    # Generate 3-8 sales records per game
    for _ in range(random.randint(3, 8)):
        region = random.choice(REGIONS)
        sales_date = release_date + timedelta(days=random.randint(0, (END_DATE - release_date).days))
        units_sold = random.randint(100, 10000)
        price_per_unit = round(random.uniform(10, 70), 2)
        revenue = round(units_sold * price_per_unit, 2)
        record = {
            'game_id': str(game_id),
            'game_name': game_name,
            'platform': platform,
            'genre': genre,
            'release_date': release_date.strftime('%Y-%m-%d'),
            'sales_date': sales_date.strftime('%Y-%m-%d'),
            'region': region,
            'units_sold': units_sold,
            'price_per_unit': price_per_unit,
            'revenue': revenue
        }
        sales_records.append(record)

print(f"Generated {len(sales_records)} sales records.")

# --- WRITE TO CSV ---
with open(CSV_FILE, 'w', newline='') as csvfile:
    fieldnames = ['game_id', 'game_name', 'platform', 'genre', 'release_date', 'sales_date', 'region', 'units_sold', 'price_per_unit', 'revenue']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for row in sales_records:
        writer.writerow(row)
print(f"Saved sales data to {CSV_FILE}")

# --- IMPORT TO MONGODB ---
game_sales.delete_many({})  # Clear old data
result = game_sales.insert_many(sales_records)
print(f"Inserted {len(result.inserted_ids)} records into {SALES_COLLECTION}.") 