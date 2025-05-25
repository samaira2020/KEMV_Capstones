import pandas as pd
import os
from pymongo import MongoClient

# MongoDB connection setup
def get_mongo_database():
    """Creates a connection to MongoDB and returns the database."""
    try:
        # Connect to MongoDB (replace with your connection string if different)
        client = MongoClient('mongodb://localhost:27017/')
        # Specify your database name
        db = client['Capstones'] # Use the database name from your screenshot
        print("Connected to MongoDB successfully!")
        return db
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")
        return None

db = get_mongo_database()

files = {
    "filtered_enriched_video_game_dataset.csv": "enriched_games",
    "developer_mapping.csv": "developer_mapping",
    "directors_mapping.csv": "directors_mapping",
    "game_mapping.csv": "game_mapping",
    "game_type_mapping.csv": "game_type_mapping",
    "genre_mapping.csv": "genre_mapping",
    "genres_igdb_mapping.csv": "genres_igdb_mapping",
    "platform_mapping.csv": "platform_mapping",
    "publisher_mapping.csv": "publisher_mapping"
}

mapping_csv_directory = "/Users/samairahassan/Documents/KEMV_Capstone3/mappings"

root_csv_directory = "/Users/samairahassan/Documents/KEMV_Capstone3"

if db is not None:
    for file, collection_name in files.items():
        print(f"Importing {file} → {collection_name}...")

        if file == "filtered_enriched_video_game_dataset.csv":
            csv_directory = root_csv_directory
        else:
            csv_directory = mapping_csv_directory

        # Construct the full path to the CSV file
        file_path = os.path.join(csv_directory, file)

        try:
            # Read the CSV into a pandas DataFrame
            df = pd.read_csv(file_path)

            # Select the MongoDB collection
            collection = db[collection_name]

            # Convert DataFrame to a list of dictionaries
            # Use .where(pd.notnull, None) to replace NaN with None for MongoDB compatibility
            data_to_insert = df.where(pd.notnull(df), None).to_dict(orient='records')

            # Insert data into MongoDB collection
            if data_to_insert:
                # Clear the collection before inserting to avoid duplicate data on reruns
                collection.delete_many({})
                insert_result = collection.insert_many(data_to_insert)
                print(f"✅ {len(insert_result.inserted_ids)} documents inserted into {collection_name}.")
            else:
                print(f"Skipping {file}: No data to insert after reading CSV.")

        except FileNotFoundError:
            print(f"Skipping {file}: File not found at {file_path}")
        except Exception as e:
            print(f"Error importing {file} into {collection_name}: {e}")

    print("🎉 All specified files processed for import into MongoDB!")
else:
    print("❌ MongoDB connection failed. Cannot proceed with import.") 