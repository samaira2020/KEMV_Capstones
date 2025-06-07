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

# Updated files dictionary with enriched developer mapping
files = {
    "filtered_enriched_video_game_dataset.csv": "enriched_games",
    "developer_mapping.csv": "developer_mapping",  # This now contains enriched metadata
    "directors_mapping.csv": "directors_mapping",
    "game_mapping.csv": "game_mapping",
    "game_type_mapping.csv": "game_type_mapping",
    "genre_mapping.csv": "genre_mapping",
    "genres_igdb_mapping.csv": "genres_igdb_mapping",
    "platform_mapping.csv": "platform_mapping",
    "publisher_mapping.csv": "publisher_mapping"
}

# Updated paths to match current directory structure
mapping_csv_directory = "./mappings"  # Relative path to mappings folder
root_csv_directory = "."  # Current directory

if db is not None:
    print("🚀 Starting MongoDB import process...")
    print(f"📁 Mapping files directory: {os.path.abspath(mapping_csv_directory)}")
    print(f"📁 Root files directory: {os.path.abspath(root_csv_directory)}")
    print("-" * 60)
    
    for file, collection_name in files.items():
        print(f"📥 Importing {file} → {collection_name}...")

        if file == "filtered_enriched_video_game_dataset.csv":
            csv_directory = root_csv_directory
        else:
            csv_directory = mapping_csv_directory

        # Construct the full path to the CSV file
        file_path = os.path.join(csv_directory, file)

        try:
            # Check if file exists
            if not os.path.exists(file_path):
                print(f"❌ File not found: {file_path}")
                continue
                
            # Read the CSV into a pandas DataFrame
            print(f"   📖 Reading CSV file...")
            df = pd.read_csv(file_path)
            print(f"   📊 Found {len(df)} rows and {len(df.columns)} columns")
            
            # For developer_mapping, show the enriched columns
            if file == "developer_mapping.csv":
                print(f"   🔍 Developer mapping columns: {list(df.columns)}")
                print(f"   📈 Sample data preview:")
                print(f"      - Studio Types: {df['Studio_Type'].value_counts().to_dict()}")
                print(f"      - Countries: {len(df['Country'].unique())} unique countries")
                print(f"      - Maturity Levels: {df['Maturity_Level'].value_counts().to_dict()}")

            # Select the MongoDB collection
            collection = db[collection_name]

            # Convert DataFrame to a list of dictionaries
            # Use .where(pd.notnull, None) to replace NaN with None for MongoDB compatibility
            data_to_insert = df.where(pd.notnull(df), None).to_dict(orient='records')

            # Insert data into MongoDB collection
            if data_to_insert:
                # Clear the collection before inserting to avoid duplicate data on reruns
                print(f"   🗑️  Clearing existing data in {collection_name}...")
                delete_result = collection.delete_many({})
                print(f"   🗑️  Deleted {delete_result.deleted_count} existing documents")
                
                print(f"   💾 Inserting {len(data_to_insert)} documents...")
                insert_result = collection.insert_many(data_to_insert)
                print(f"   ✅ Successfully inserted {len(insert_result.inserted_ids)} documents into {collection_name}")
                
                # Verify the insertion
                doc_count = collection.count_documents({})
                print(f"   🔍 Verification: {doc_count} documents now in {collection_name}")
                
            else:
                print(f"   ⚠️  No data to insert after reading CSV.")

        except FileNotFoundError:
            print(f"   ❌ File not found: {file_path}")
        except pd.errors.EmptyDataError:
            print(f"   ❌ Empty CSV file: {file_path}")
        except Exception as e:
            print(f"   ❌ Error importing {file}: {e}")
            
        print("-" * 60)

    print("🎉 All specified files processed for import into MongoDB!")
    
    # Final verification - show collection statistics
    print("\n📊 Final Collection Statistics:")
    for file, collection_name in files.items():
        try:
            collection = db[collection_name]
            count = collection.count_documents({})
            print(f"   {collection_name}: {count:,} documents")
        except Exception as e:
            print(f"   {collection_name}: Error getting count - {e}")
            
else:
    print("❌ MongoDB connection failed. Cannot proceed with import.") 