from flask import Flask, render_template
from pymongo import MongoClient
import pandas as pd

app = Flask(__name__)

# === MongoDB Connection ===
def get_mongo_collection(database_name, collection_name):
    """Creates a connection to MongoDB and returns the specified collection."""
    try:
        # Connect to MongoDB (replace with your connection string if different)
        client = MongoClient('mongodb://localhost:27017/')
        db = client[database_name]
        collection = db[collection_name]
        print(f"Connected to MongoDB: {database_name}.{collection_name}")
        return collection
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")
        return None

# === Flask Routes ===
@app.route('/')
def index():
    # Load data from MongoDB
    database_name = 'Capstones'
    collection_name = 'enriched_games' # Assuming the main game data is here
    
    collection = get_mongo_collection(database_name, collection_name)
    data = []
    if collection is not None:
        try:
            # Fetch all documents from the collection
            # Limit for now to avoid overwhelming the page with too much data initially
            data = list(collection.find().limit(100)) # Fetch first 100 documents as an example
            # You might want to convert this to a pandas DataFrame for easier manipulation
            # df = pd.DataFrame(data)
            # print(df.head())
        except Exception as e:
            print(f"Error fetching data from MongoDB: {e}")

    # Pass the data to the HTML template
    return render_template('index.html', data=data)

if __name__ == '__main__':
    # To run in debug mode:
    app.run(debug=True)
    # To run in production:
    # app.run() 