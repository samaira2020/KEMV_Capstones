from flask import Flask, render_template_string, request
from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.errors import ConnectionFailure
import pandas as pd
from datetime import datetime
import logging
import json # Needed for jsonify equivalent and embedding data

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- MongoDB Handler Class (Copied from db.py) ---
class MongoDBHandler:
    def __init__(self, connection_string='mongodb://localhost:27017/'):
        """Initialize MongoDB connection."""
        try:
            self.client = MongoClient(connection_string)
            self.db = self.client['Capstones']
            # The ismaster command is cheap and does not require auth.
            self.client.admin.command('ismaster')
            logger.info("Successfully connected to MongoDB")
        except ConnectionFailure as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise
        except Exception as e:
            logger.error(f"An unexpected error occurred during MongoDB connection: {e}")
            raise


    def get_collection(self, collection_name):
        """Get a specific collection from the database."""
        return self.db[collection_name]

    # Helper to build match query from filters
    def _build_filter_match(self):
        match_conditions = []
        # Ensure the 'Title' and 'Rating' fields exist and Rating is a number
        # Only keep the base conditions here as filtering is commented out in pipelines for now
        base_conditions = [
            {'Title': {'$exists': True, '$ne': None}},
            {'Rating': {'$exists': True, '$ne': None, '$type': 'number'}}
        ]
        match_conditions.extend(base_conditions)

        # Ignore genre, platform, and year range filtering in this helper for now

        # Combine all conditions with $and
        if match_conditions:
            return {'$and': match_conditions}
        else:
            return {}

    # === Basic CRUD Operations ===
    # (Included for completeness, though not all are used by the dashboard route)
    def insert_one(self, collection_name, document):
        """Insert a single document into the collection."""
        try:
            collection = self.get_collection(collection_name)
            return collection.insert_one(document)
        except Exception as e:
            print(f"Error in insert_one: {e}")
            return None

    def insert_many(self, collection_name, documents):
        """Insert multiple documents into the collection."""
        try:
            collection = self.get_collection(collection_name)
            return collection.insert_many(documents)
        except Exception as e:
            print(f"Error in insert_many: {e}")
            return None

    def find_one(self, collection_name, query):
        """Find a single document matching the query."""
        try:
            collection = self.get_collection(collection_name)
            return collection.find_one(query)
        except Exception as e:
            print(f"Error in find_one: {e}")
            return None

    def find_many(self, collection_name, query=None, limit=0, sort_field=None, sort_order=ASCENDING):
        """Find multiple documents matching the query."""
        try:
            collection = self.get_collection(collection_name)
            cursor = collection.find(query or {})

            if sort_field:
                cursor = cursor.sort(sort_field, sort_order)
            if limit > 0:
                cursor = cursor.limit(limit)

            return list(cursor)
        except Exception as e:
            print(f"Error in find_many: {e}")
            return []

    def update_one(self, collection_name, query, update):
        """Update a single document matching the query."""
        try:
            collection = self.get_collection(collection_name)
            return collection.update_one(query, update)
        except Exception as e:
            print(f"Error in update_one: {e}")
            return None

    def delete_one(self, collection_name, query):
        """Delete a single document matching the query."""
        try:
            collection = self.get_collection(collection_name)
            return collection.delete_one(query)
        except Exception as e:
            print(f"Error in delete_one: {e}")
            return None

    # === Analytics Queries (Updated based on previous steps, filtering commented) ===
    def get_game_statistics(self, year_range=None):
        """Calculates general game statistics (e.g., total count) with optional year filtering."""
        try:
            print(f"Fetching general statistics.")
            collection = self.db.enriched_games
            pipeline = []

            # Apply base filters (existence and type checks) using _build_filter_match
            match_query = self._build_filter_match() # Use base conditions only
            if match_query:
                 pipeline.append({'$match': match_query})

            # Add stage to count total documents (games)
            pipeline.append({'$count': 'total_games'})

            print(f"Executing aggregation pipeline for get_game_statistics: {pipeline}")
            # Execute the aggregation pipeline
            stats = list(collection.aggregate(pipeline, allowDiskUse=True))
            print(f"Stats result from get_game_statistics: {stats}")

            # The result is a list of documents, typically with one document like [{'total_games': count}]
            # Return the count, or 0 if no documents were returned
            if stats:
                return stats[0]
            else:
                return {'total_games': 0}

        except Exception as e:
            print(f"Error in get_game_statistics: {e}")
            return {}


    def get_top_rated_games(self, collection_name='enriched_games', limit=10, genres=None, platforms=None, year_range=None):
        """Get top rated games, with filters (ignoring filters for now)."""
        try:
            print(f"Fetching top {limit} highly rated games (ignoring filters and array fields).")
            collection = self.get_collection(collection_name)
            pipeline = []

            # 1. Apply base filters (existence and type checks) using _build_filter_match
            #    Also add checks for Title and Rating types here
            match_query = self._build_filter_match() # Use base conditions only
            base_match = {
                '$and': [
                    {'Title': {'$exists': True, '$ne': None, '$type': 'string'}},
                    {'Rating': {'$exists': True, '$ne': None, '$type': 'number'}}
                ]
            }
            if match_query:
                # Combine base match with any other base filters from _build_filter_match
                pipeline.append({'$match': {'$and': [base_match, match_query]}})
            else:
                pipeline.append({'$match': base_match})

            # Ignore genre, platform, and year range filtering for now (already commented out sections remain commented)

            # 2. Sort by Rating (descending) and limit
            pipeline.append({'$sort': {'Rating': -1}})
            pipeline.append({'$limit': limit})

            # 3. Project to rename fields for frontend and ensure correct types
            pipeline.append({
                '$project': {
                    '_id': 0, # Exclude default _id
                    'name': {'$toString': '$Title'}, # Ensure name is string
                    'rating': {'$round': [{'$convert': {'input': '$Rating', 'to': 'double', 'onError': 0.0, 'onNull': 0.0}}, 1]}, # Ensure rating is number and round
                    'category': {'$toString': {'$ifNull': ['$Genre', '']}} # Ensure category is string
                }
            })

            print(f"Executing aggregation pipeline for get_top_rated_games: {pipeline}")

            result = list(collection.aggregate(pipeline, allowDiskUse=True))
            print(f"Result from get_top_rated_games: {result}")
            return result

        except Exception as e:
            print(f"Error in get_top_rated_games: {e}")
            return []

    # Renamed from get_category_distribution for clarity with counts
    def get_games_count_by_genre(self, collection_name='enriched_games', genres=None, platforms=None, year_range=None):
        """Counts games per genre, with optional filters (ignoring filters for now)."""
        try:
            print(f"Fetching game counts by genre (ignoring filters).")
            collection = self.get_collection(collection_name)
            pipeline = []

            # 1. Add fields for GenresArray and extractedYear
            pipeline.append({
                '$addFields': {
                    'GenresArray': {'$split': [{'$ifNull': ['$Genre', '']}, ', ']},
                    'extractedYear': {
                        '$toInt': {
                            '$arrayElemAt': [{'$split': [{'$ifNull': ['$Release_Date_IGDB', '']}, '/']}, 2] # Get the last part (YYYY)
                        }
                    }
                }
            })

            # 2. Apply base filters (existence and type checks) using _build_filter_match
            match_query = self._build_filter_match() # Use base conditions only
            if match_query:
                 pipeline.append({'$match': match_query})

            # Ignore genre, platform, and year range filters for now
            # 3. Apply year range filter
            # if year_range and len(year_range) == 2:
            #      pipeline.append({
            #          '$match': {
            #              'extractedYear': {
            #                  '$gte': year_range[0],
            #                  '$lte': year_range[1],
            #                  '$exists': True,
            #                  '$ne': None,
            #                  '$type': 'number'
            #              }
            #          }
            #      })

            # 4. Apply platform filter
            # if platforms:
            #      pipeline.append({'$match': {'PlatformsArray': {'$in': platforms}}})

            # 5. Unwind the GenresArray
            pipeline.append({'$unwind': '$GenresArray'})

            # 6. Apply genre filter after unwinding
            # if genres:
            #     pipeline.append({'$match': {'GenresArray': {'$in': genres}}})

            # 7. Group by genre and count
            pipeline.append({
                '$group': {
                    '_id': '$GenresArray',
                    'count': {'$sum': 1}
                }
            })

            # 8. Sort by count
            # pipeline.append({'$sort': {'count': -1}})

            print(f"Executing aggregation pipeline for get_games_count_by_genre: {pipeline}")
            result = list(collection.aggregate(pipeline, allowDiskUse=True))
            print(f"Result from get_games_count_by_genre: {result}")
            return result

        except Exception as e:
            print(f"Error in get_games_count_by_genre: {e}")
            return []


    def get_price_range_distribution(self, collection_name='enriched_games'):
        """Get distribution of games across price ranges."""
        # This function is not applicable without price data
        return []


    # === Search and Filter Functions ===
    # (Included for completeness, though not all are used by the dashboard route)
    def search_games(self, collection_name='enriched_games', search_term=None,
                    min_rating=None, max_rating=None, category=None):
        """Search games with multiple filter criteria."""
        try:
            collection = self.get_collection(collection_name)
            query = {}

            # Ensure Title and Rating exist and Rating is a number
            query['Title'] = {'$exists': True, '$ne': None}
            query['Rating'] = {'$exists': True, '$ne': None, '$type': 'number'}

            if search_term:
                query['Title'] = {'$regex': search_term, '$options': 'i'} # Search on 'Title'

            if min_rating is not None:
                query['Rating'] = {'$gte': min_rating}
            if max_rating is not None:
                query['Rating'] = {'$lte': max_rating}

            if category:
                # Use regex to find the category as a whole word in the comma-separated string
                query['Genre'] = {'$regex': f'(^|,\\s*){category}(\\,|\\s*$)', '$options': 'i'}

            print(f"Executing find query for search_games: {query}")
            result = list(collection.find(query))
            print(f"Result from search_games: {result}")
            return result
        except Exception as e:
            print(f"Error in search_games: {e}")
            return []


    # === Data Transformation Functions ===
    # (Included for completeness, though not all are used by the dashboard route)
    def to_dataframe(self, collection_name, query=None, limit=0):
        """Convert MongoDB query results to pandas DataFrame."""
        try:
            collection = self.get_collection(collection_name)
            cursor = collection.find(query or {})
            if limit > 0:
                cursor = cursor.limit(limit)
            result = list(cursor)
            print(f"Result from to_dataframe: {result}")
            return pd.DataFrame(result)
        except Exception as e:
            print(f"Error in to_dataframe: {e}")
            return pd.DataFrame()

    def export_to_csv(self, collection_name, query=None, filename=None):
        """Export collection data to a CSV file."""
        try:
            df = self.to_dataframe(collection_name, query=query)
            if not df.empty:
                df.to_csv(filename or f'{collection_name}.csv', index=False)
                print(f"Data from {collection_name} exported to {filename or f'{collection_name}.csv'}")
        except Exception as e:
            print(f"Error in export_to_csv: {e}")


    # === Index Management ===
    # (Included for completeness)
    def create_index(self, collection_name, field, unique=False):
        """Create an index on a specified field."""
        try:
            collection = self.get_collection(collection_name)
            collection.create_index([(field, ASCENDING)], unique=unique)
            print(f"Index created on '{field}' in '{collection_name}'")
        except Exception as e:
            print(f"Error in create_index: {e}")

    def list_indexes(self, collection_name):
        """List all indexes for a collection."""
        try:
            collection = self.get_collection(collection_name)
            indexes = list(collection.list_indexes())
            print(f"Indexes for '{collection_name}': {indexes}")
            return indexes
        except Exception as e:
            print(f"Error in list_indexes: {e}")
            return []

    # === Connection Management ===
    def close(self):
        """Close the MongoDB connection."""
        try:
            self.client.close()
            print("MongoDB connection closed.")
        except Exception as e:
            print(f"Error in close: {e}")

    # === Mapping Data Retrieval ===
    def get_mapping_data(self, collection_name):
        """Retrieve all documents from a mapping collection."""
        try:
            print(f"Fetching mapping data for collection: {collection_name}")
            collection = self.db[collection_name]
            result = list(collection.find({}))
            print(f"Result from get_mapping_data for {collection_name}: {result}")
            return result
        except Exception as e:
            print(f"Error in get_mapping_data for {collection_name}: {e}")
            return []

    # === Dashboard Analytics Queries (based on available data, filtering commented) ===
    def get_games_count_by_platform(self, collection_name='enriched_games', genres=None, platforms=None, year_range=None):
        """Counts games per platform, with optional filters (ignoring filters for now)."""
        try:
            print(f"Fetching game counts by platform (ignoring filters).")
            collection = self.get_collection(collection_name)

            # Define the pipeline as a list
            pipeline = [
                # 1. Add fields for PlatformsArray and extractedYear
                {
                    '$addFields': {
                        'PlatformsArray': {'$split': [{'$ifNull': ['$Platform', '']}, ', ']},
                        'extractedYear': {
                            '$toInt': {
                                '$arrayElemAt': [{'$split': [{'$ifNull': ['$Release_Date_IGDB', '']}, '/']}, 2] # Get the last part (YYYY)
                            }
                        }
                    }
                }
            ]

            # 2. Apply base filters (existence and type checks) using _build_filter_match
            match_query = self._build_filter_match() # Use base conditions only
            if match_query:
                pipeline.append({'$match': match_query})

            # Ignore genre, platform, and year range filters for now
            # 3. Apply year range filter
            # if year_range and len(year_range) == 2:
            #      pipeline.append({
            #          '$match': {
            #              'extractedYear': {
            #                  '$gte': year_range[0],
            #                  '$lte': year_range[1],
            #                  '$exists': True,
            #                  '$ne': None,
            #                  '$type': 'number'
            #              }
            #          }
            #      })

            # 4. Unwind the PlatformsArray
            pipeline.append({'$unwind': '$PlatformsArray'}) # Unwind always

            # Add a match stage to filter out empty platform strings after unwinding
            pipeline.append({'$match': {'PlatformsArray': {'$ne': '', '$exists': True, '$ne': None}}})


            # 5. Apply platform filter after unwinding (commented out)
            # if platforms:
            #      pipeline.append({'$match': {'PlatformsArray': {'$in': platforms}}})

            # Log pipeline stages before grouping
            print(f"Pipeline stages before grouping in get_games_count_by_platform: {pipeline}")

            # 6. Group by platform and count
            pipeline.append({
                '$group': {
                    '_id': '$PlatformsArray', # Use the unwound string
                    'count': {'$sum': 1}
                }
            })

            # 7. Sort by count
            # pipeline.append({'$sort': {'count': -1}}) # Comment out sorting for now


            print(f"Executing final aggregation pipeline for get_games_count_by_platform: {pipeline}")
            result = list(collection.aggregate(pipeline, allowDiskUse=True))
            print(f"Result from get_games_count_by_platform: {result}")
            return result

        except Exception as e:
            print(f"Error in get_games_count_by_platform: {e}")
            return []


    def get_games_per_year_raw(self, collection_name='enriched_games'):
        """Fetches raw year data from games with valid Release_Date_IGDB."""
        try:
            print(f"Executing aggregation pipeline for get_games_per_year_raw")
            collection = self.get_collection(collection_name)
            pipeline = [
                {'$match': {'Release_Date_IGDB': {'$exists': True, '$ne': None, '$type': 'string'}}},
                {'$project': {'_id': 0, 'extractedYear': {'$toInt': {'$arrayElemAt': [{'$split': ['$Release_Date_IGDB', '/']}, 2]}}}} # Get the last part (YYYY)
            ]
            print(f"Pipeline for get_games_per_year_raw: {pipeline}")
            result = list(collection.aggregate(pipeline, allowDiskUse=True))
            print(f"Raw years from get_games_per_year_raw: {result}")
            return result
        except Exception as e:
            print(f"Error in get_games_per_year_raw: {e}")
            return []


    def get_games_per_year(self, collection_name='enriched_games', genres=None, platforms=None, year_range=None):
        """Counts games per year, with optional filters (ignoring filters for now)."""
        try:
            print(f"Fetching game counts per year (ignoring filters).")
            collection = self.get_collection(collection_name)

            # Define the pipeline as a list
            pipeline = [
                # 1. Add fields for GenresArray, PlatformsArray, and extractedYear
                {
                    '$addFields': {
                        'GenresArray': {'$split': [{'$ifNull': ['$Genre', '']}, ', ']},
                        'PlatformsArray': {'$split': [{'$ifNull': ['$Platform', '']}, ', ']},
                        'extractedYear': {
                            '$toInt': {
                                '$arrayElemAt': [{'$split': [{'$ifNull': ['$Release_Date_IGDB', '']}, '/']}, 2] # Get the last part (YYYY)
                            }
                        }
                    }
                }
            ]

            # 2. Apply base filters (existence and type checks) using _build_filter_match
            match_query = self._build_filter_match() # Use base conditions only
            if match_query:
                 pipeline.append({'$match': match_query})

            # Ignore genre, platform, and year range filters for now
            # 3. Apply year range filter
            # if year_range and len(year_range) == 2:
            #      pipeline.append({
            #          '$match': {
            #              'extractedYear': {
            #                  '$gte': year_range[0],
            #                  '$lte': year_range[1],
            #                  '$exists': True,
            #                  '$ne': None,
            #                  '$type': 'number'
            #              }
            #          }
            #      })

            # 4. Unwind GenresArray and PlatformsArray
            pipeline.append({'$unwind': '$GenresArray'}) # Unwind always
            pipeline.append({'$unwind': '$PlatformsArray'}) # Unwind always

            # 5. Apply genre and platform filters after unwinding
            # if genres:
            #     pipeline.append({'$match': {'GenresArray': {'$in': genres}}}) # Comment out genre filter
            # if platforms:
            #      pipeline.append({'$match': {'PlatformsArray': {'$in': platforms}}}) # Comment out platform filter

            # 6. Group by year and count, ensuring year is a number
            # Only group if extractedYear is a valid number
            pipeline.append({
                '$group': {
                    '_id': '$extractedYear',
                    'count': {'$sum': 1}
                }
            })

            # 7. Match stage to filter out documents where _id (year) is null after grouping
            pipeline.append({'$match': {'_id': {'$ne': None}}})

            # 8. Project to rename _id to year and ensure count is numeric
            pipeline.append({
                '$project': {
                    'year': '$_id',
                    'count': {'$sum': ['$count']}
                }
            })

            # 9. Sort by year
            pipeline.append({'$sort': {'year': 1}})

            print(f"Executing aggregation pipeline for get_games_per_year: {pipeline}")
            result = list(collection.aggregate(pipeline, allowDiskUse=True))
            print(f"Result from get_games_per_year: {result}")
            return result

        except Exception as e:
            print(f"Error fetching games per year: {e}")
            return []


    def get_games_count_by_publisher(self, collection_name='enriched_games', genres=None, platforms=None, year_range=None):
        """Counts games per publisher, with optional filters (ignoring filters for now)."""
        try:
            print(f"Fetching publisher counts (ignoring filters).")
            collection = self.get_collection(collection_name)

            # Define the pipeline as a list
            pipeline = [
                # 1. Add fields for GenresArray, PlatformsArray, and extractedYear
                {
                    '$addFields': {
                        'GenresArray': {'$split': [{'$ifNull': ['$Genre', '']}, ', ']},
                        'PlatformsArray': {'$split': [{'$ifNull': ['$Platform', '']}, ', ']},
                        'extractedYear': {
                            '$toInt': {
                                '$arrayElemAt': [{'$split': [{'$ifNull': ['$Release_Date_IGDB', '']}, '/']}, 2] # Get the last part (YYYY)
                            }
                        }
                    }
                }
            ]

            # 2. Apply base filters (existence and type checks) using _build_filter_match
            match_query = self._build_filter_match() # Use base conditions only
            if match_query:
                 pipeline.append({'$match': match_query})

            # Ignore genre, platform, and year range filters for now
            # 3. Apply year range filter
            # if year_range and len(year_range) == 2:
            #      pipeline.append({
            #          '$match': {
            #              'extractedYear': {
            #                  '$gte': year_range[0],
            #                  '$lte': year_range[1],
            #                  '$exists': True,
            #                  '$ne': None,
            #                  '$type': 'number'
            #              }
            #          }
            #      })

            # 4. Unwind GenresArray and PlatformsArray
            pipeline.append({'$unwind': '$GenresArray'}) # Unwind always
            pipeline.append({'$unwind': '$PlatformsArray'}) # Unwind always

            # 5. Apply genre and platform filters after unwinding
            # if genres:
            #     pipeline.append({'$match': {'GenresArray': {'$in': genres}}}) # Comment out genre filter
            # if platforms:
            #      pipeline.append({'$match': {'PlatformsArray': {'$in': platforms}}}) # Comment out platform filter

            # 6. Group by publisher and count, ensuring publisher is not null
            pipeline.append({
                '$group': {
                    '_id': '$Publisher',
                    'count': {'$sum': 1}
                }
            })

            # 7. Match stage to filter out documents where _id (publisher) is null after grouping
            pipeline.append({'$match': {'_id': {'$ne': None}}})

            # 8. Sort by count (descending)
            pipeline.append({'$sort': {'count': -1}})

            print(f"Executing aggregation pipeline for get_games_count_by_publisher: {pipeline}")
            result = list(collection.aggregate(pipeline, allowDiskUse=True))
            print(f"Result from get_games_count_by_publisher: {result}")
            return result

        except Exception as e:
            print(f"Error fetching publisher counts: {e}")
            return []

    def get_avg_rating_by_platform(self, collection_name='enriched_games', genres=None, platforms=None, year_range=None):
        """Calculates average rating per platform, with optional filters (ignoring filters for now)."""
        try:
            print(f"Fetching average rating by platform (ignoring filters).")
            collection = self.get_collection(collection_name)

            # Define the pipeline as a list
            pipeline = [
                # 1. Add fields for GenresArray, PlatformsArray, and extractedYear
                {
                    '$addFields': {
                        'GenresArray': {'$split': [{'$ifNull': ['$Genre', '']}, ', ']},
                        'PlatformsArray': {'$split': [{'$ifNull': ['$Platform', '']}, ', ']},
                        'extractedYear': {
                            '$toInt': {
                                '$arrayElemAt': [{'$split': [{'$ifNull': ['$Release_Date_IGDB', '']}, '/']}, 2] # Get the last part (YYYY)
                            }
                        }
                    }
                }
            ]

            # 2. Apply base filters (existence and type checks) using _build_filter_match
            match_query = self._build_filter_match() # Use base conditions only
            if match_query:
                 pipeline.append({'$match': match_query})

            # Ignore genre, platform, and year range filters for now
            # 3. Apply year range filter
            # if year_range and len(year_range) == 2:
            #      pipeline.append({
            #          '$match': {
            #              'extractedYear': {
            #                  '$gte': year_range[0],
            #                  '$lte': year_range[1],
            #                  '$exists': True,
            #                  '$ne': None,
            #                  '$type': 'number'
            #              }
            #          }
            #      })

            # 4. Unwind GenresArray and PlatformsArray
            pipeline.append({'$unwind': '$GenresArray'}) # Unwind always
            pipeline.append({'$unwind': '$PlatformsArray'}) # Unwind always

            # 5. Apply genre and platform filters after unwinding
            # if genres:
            #     pipeline.append({'$match': {'GenresArray': {'$in': genres}}}) # Comment out genre filter
            # if platforms:
            #      pipeline.append({'$match': {'PlatformsArray': {'$in': platforms}}}) # Comment out platform filter

            # 6. Add a project stage to ensure Rating is a number, handling potential errors
            pipeline.append({
                '$project': {
                    '_id': 1,
                    'PlatformsArray': 1,
                    'Rating': {'$convert': {'input': '$Rating', 'to': 'double', 'onError': None, 'onNull': None}},
                }
            })

            # 7. Match stage to filter out documents where Rating conversion failed
            pipeline.append({'$match': {'Rating': {'$ne': None}}})

            # 8. Group by platform and calculate average rating, ensuring platform is not null
            pipeline.append({
                '$group': {
                    '_id': '$PlatformsArray',
                    'average_rating': {'$avg': '$Rating'}
                }
            })

            # 9. Match stage to filter out documents where _id (platform) is null after grouping
            pipeline.append({'$match': {'_id': {'$ne': None}}})

            # 10. Sort by average rating (descending)
            pipeline.append({'$sort': {'average_rating': -1}})

            print(f"Executing aggregation pipeline for get_avg_rating_by_platform: {pipeline}")
            result = list(collection.aggregate(pipeline, allowDiskUse=True))
            print(f"Result from get_avg_rating_by_platform: {result}")
            return result

        except Exception as e:
            print(f"Error fetching average rating by platform: {e}")
            return []


    def get_avg_rating_by_developer(self, collection_name='enriched_games', genres=None, platforms=None, year_range=None):
        """Calculates average rating per developer, with optional filters (ignoring filters for now)."""
        try:
            print(f"Fetching average rating by developer (ignoring filters).")
            collection = self.get_collection(collection_name)

            # Define the pipeline as a list
            pipeline = [
                # 1. Add fields for GenresArray, PlatformsArray, and extractedYear
                {
                    '$addFields': {
                        'GenresArray': {'$split': [{'$ifNull': ['$Genre', '']}, ', ']},
                        'PlatformsArray': {'$split': [{'$ifNull': ['$Platform', '']}, ', ']},
                        'extractedYear': {
                            '$toInt': {
                                '$arrayElemAt': [{'$split': [{'$ifNull': ['$Release_Date_IGDB', '']}, '/']}, 2] # Get the last part (YYYY)
                            }
                        }
                    }
                }
            ]

            # 2. Apply base filters (existence and type checks) using _build_filter_match
            match_query = self._build_filter_match() # Use base conditions only
            if match_query:
                 pipeline.append({'$match': match_query})

            # Ignore genre, platform, and year range filters for now
            # 3. Apply year range filter
            # if year_range and len(year_range) == 2:
            #      pipeline.append({
            #          '$match': {
            #              'extractedYear': {
            #                  '$gte': year_range[0],
            #                  '$lte': year_range[1],
            #                  '$exists': True,
            #                  '$ne': None,
            #                  '$type': 'number'
            #              }
            #          }
            #      })

            # 4. Unwind GenresArray and PlatformsArray
            pipeline.append({'$unwind': '$GenresArray'}) # Unwind always
            pipeline.append({'$unwind': '$PlatformsArray'}) # Unwind always

            # 5. Apply genre and platform filters after unwinding
            # if genres:
            #     pipeline.append({'$match': {'GenresArray': {'$in': genres}}}) # Comment out genre filter
            # if platforms:
            #      pipeline.append({'$match': {'PlatformsArray': {'$in': platforms}}}) # Comment out platform filter

            # 6. Add a project stage to ensure Rating is a number, handling potential errors
            pipeline.append({
                '$project': {
                    '_id': 1,
                    'Developer': 1,
                    'Rating': {'$convert': {'input': '$Rating', 'to': 'double', 'onError': None, 'onNull': None}},
                }
            })

            # 7. Match stage to filter out documents where Rating conversion failed
            pipeline.append({'$match': {'Rating': {'$ne': None}}})

            # 8. Group by developer and calculate average rating, ensuring developer is not null
            pipeline.append({
                '$group': {
                    '_id': '$Developer',
                    'average_rating': {'$avg': '$Rating'}
                }
            })

            # 9. Match stage to filter out documents where _id (developer) is null after grouping
            pipeline.append({'$match': {'_id': {'$ne': None}}})

            # 10. Sort by average rating (descending)
            pipeline.append({'$sort': {'average_rating': -1}})

            print(f"Executing aggregation pipeline for get_avg_rating_by_developer: {pipeline}")
            result = list(collection.aggregate(pipeline, allowDiskUse=True))
            print(f"Result from get_avg_rating_by_developer: {result}")
            return result

        except Exception as e:
            print(f"Error fetching average rating by developer: {e}")
            return []

    def get_games(self, limit=20):
        """Fetches a limited number of games."""
        try:
            print(f"Fetching {limit} games from the enriched_games collection.")
            collection = self.get_collection('enriched_games')
            pipeline = [
                {'$limit': limit}
            ]
            print(f"Executing aggregation pipeline for get_games: {pipeline}")
            result = list(collection.aggregate(pipeline, allowDiskUse=True))
            print(f"Fetched {len(result)} games from get_games.")
            return result
        except Exception as e:
            print(f"Error fetching games: {e}")
            return []

    # Endpoint to get filter options dynamically (optional, for more complex filtering)
    def get_filter_options(self):
        try:
            genre_mapping_data = self.get_mapping_data('genre_mapping')
            all_genres = [item['Name'] for item in genre_mapping_data]

            platform_mapping_data = self.get_mapping_data('platform_mapping')
            all_platforms = [item['Name'] for item in platform_mapping_data]

            return {
                'genres': all_genres,
                'platforms': all_platforms
            }
        except Exception as e:
            return {'error': str(e)}


# --- Flask App and Route ---
app = Flask(__name__)

# Initialize MongoDB handler
db_handler = MongoDBHandler()


@app.route('/')
def index():
    # Initialize variables
    stats_data = {}
    top_games = []
    platform_counts = []
    genre_counts = []
    games_per_year = []
    publisher_counts = []
    avg_rating_platform = []
    avg_rating_developer = []
    all_genres = []
    all_platforms = []
    min_year = 1980 # Default min year
    max_year = datetime.now().year # Default max year

    # Initialize year_range with a default value before the try block
    year_range = [min_year, max_year]

    error = None

    try:
        # Get selected genres, platforms, and year range from request or set defaults
        # (Keep request args processing even if filtering is commented out in db.py for now)
        selected_genres = request.args.getlist('genre')
        selected_platforms = request.args.getlist('platform')
        year_start = request.args.get('year_start', type=int)
        year_end = request.args.get('year_end', type=int)


        # Determine min and max year based on data
        # Fetch games_per_year_raw first to determine the year range from data
        games_per_year_raw = db_handler.get_games_per_year_raw()
        valid_years = [item.get('extractedYear') for item in games_per_year_raw if item.get('extractedYear') is not None and isinstance(item.get('extractedYear'), (int, float))]

        if valid_years:
            min_year_data = min(valid_years)
            max_year_data = max(valid_years)
        else:
            # Default or handle cases with no valid year data
            min_year_data = 1980  # Or another appropriate default
            max_year_data = datetime.now().year  # Use current year as a default

        # Set default year range for filters if not provided in request
        year_start = year_start if year_start is not None else min_year_data
        year_end = year_end if year_end is not None else max_year_data
        year_range = [year_start, year_end]


        print(f"Selected Genres: {selected_genres}")
        print(f"Selected Platforms: {selected_platforms}")
        print(f"Selected Year Range: {year_range}")

        # Fetch filter options data
        # Use get_mapping_data to get genres and platforms for the filters
        genre_mapping_data = db_handler.get_mapping_data('genre_mapping')
        all_genres = [item['Name'] for item in genre_mapping_data]

        platform_mapping_data = db_handler.get_mapping_data('platform_mapping')
        all_platforms = [item['Name'] for item in platform_mapping_data]


        # Fetch dashboard data using the determined year range (filtering within db.py methods is commented out for now)
        try:
            stats_raw = list(db_handler.get_game_statistics(year_range))
            if stats_raw:
                stats_data = stats_raw[0]
            else:
                stats_data = {'total_games': 0}
        except Exception as e:
            print(f"Error fetching stats: {e}")
            stats_data = {}

        try:
            # Pass selected filters to top_rated_games, even though filtering is commented out internally for now
            top_games = list(db_handler.get_top_rated_games(genres=selected_genres, platforms=selected_platforms, year_range=year_range))
        except Exception as e:
            print(f"Error fetching top games: {e}")
            top_games = []

        try:
            # Pass selected filters, even though filtering is commented out internally for now
            platform_counts = list(db_handler.get_games_count_by_platform(genres=selected_genres, platforms=selected_platforms, year_range=year_range))
        except Exception as e:
            print(f"Error fetching platform counts: {e}")
            platform_counts = []

        try:
            # Pass selected filters, even though filtering is commented out internally for now
            genre_counts = list(db_handler.get_games_count_by_genre(genres=selected_genres, platforms=selected_platforms, year_range=year_range))
        except Exception as e:
            print(f"Error fetching genre counts: {e}")
            genre_counts = []

        try:
             # Pass selected filters, even though filtering is commented out internally for now
            games_per_year = list(db_handler.get_games_per_year(genres=selected_genres, platforms=selected_platforms, year_range=year_range))
        except Exception as e:
            print(f"Error fetching games per year: {e}")
            games_per_year = []

        try:
            # Pass selected filters, even though filtering is commented out internally for now
            publisher_counts = list(db_handler.get_games_count_by_publisher(genres=selected_genres, platforms=selected_platforms, year_range=year_range))
        except Exception as e:
            print(f"Error fetching publisher counts: {e}")
            publisher_counts = []

        try:
            # Pass selected filters, even though filtering is commented out internally for now
            avg_rating_platform = list(db_handler.get_avg_rating_by_platform(genres=selected_genres, platforms=selected_platforms, year_range=year_range))
        except Exception as e:
            print(f"Error fetching average rating by platform: {e}")
            avg_rating_platform = []

        try:
            # Pass selected filters, even though filtering is commented out internally for now
            avg_rating_developer = list(db_handler.get_avg_rating_by_developer(genres=selected_genres, platforms=selected_platforms, year_range=year_range))
        except Exception as e:
            print(f"Error fetching average rating by developer: {e}")
            avg_rating_developer = []

        # Fetch a list of games (if needed, otherwise remove)
        try:
            games_list = list(db_handler.get_games(limit=50)) # Fetching up to 50 games for now
        except Exception as e:
            print(f"Error fetching games list: {e}")
            games_list = []


        # Log the fetched data (optional, but good for debugging)
        print("--- Dashboard Data Fetched (Detailed) ---")
        print(f"Stats: {stats_data} (type: {type(stats_data)})")
        print(f"Top Games: {top_games} (type: {type(top_games)})\nContent: {top_games[:5]}...") # Print first 5
        print(f"Platform Counts: {platform_counts} (type: {type(platform_counts)})\nContent: {platform_counts[:5]}...") # Print first 5
        print(f"Genre Counts: {genre_counts} (type: {type(genre_counts)})\nContent: {genre_counts[:5]}...") # Print first 5
        print(f"Games Per Year: {games_per_year} (type: {type(games_per_year)})\nContent: {games_per_year[:5]}...") # Print first 5
        print(f"Publisher Counts: {publisher_counts} (type: {type(publisher_counts)})\nContent: {publisher_counts[:5]}...") # Print first 5
        print(f"Avg Rating Platform: {avg_rating_platform} (type: {type(avg_rating_platform)})\nContent: {avg_rating_platform[:5]}...") # Print first 5
        print(f"Avg Rating Developer: {avg_rating_developer} (type: {type(avg_rating_developer)})\nContent: {avg_rating_developer[:5]}...") # Print first 5
        print(f"All Genres: {all_genres} (type: {type(all_genres)})")
        print(f"All Platforms: {all_platforms} (type: {type(all_platforms)})")
        print(f"Min Year Data: {min_year_data} (type: {type(min_year_data)})")
        print(f"Max Year Data: {max_year_data} (type: {type(max_year_data)})")
        print(f"Year Range: {year_range} (type: {type(year_range)})")
        print(f"Games List: {games_list} (type: {type(games_list)})\nContent: {games_list[:5]}...") # Print first 5
        print("-----------------------------------------\n")


    except Exception as e:
        error = f"An error occurred during data fetching: {e}"
        print(f"An error occurred during data fetching: {e}")
        # Initialize empty data structures in case of error
        stats_data = {}
        top_games = []
        platform_counts = []
        genre_counts = []
        games_per_year = []
        publisher_counts = []
        avg_rating_platform = []
        avg_rating_developer = []
        all_genres = []
        all_platforms = []
        min_year_data = 1980
        max_year_data = datetime.now().year
        year_range = [min_year_data, max_year_data]
        games_list = []


    # --- Embedded HTML Template (Based on index.html, charts commented out) ---
    # Pass data as JSON strings to be read by embedded JavaScript
    html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Video Game Dashboard</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-T3c6CoIi6uLrA9TneNEoa7RxnatzjcDSCmG1MXxSR1GAsXEV/Dwwykc2MPK8M2HN" crossorigin="anonymous">
    <script src="https://cdn.jsdelivr.net/npm/chart.js@3.9.1/dist/chart.min.js"></script>
    {% raw %}
    <style>
        body {{
            background-color: #1e1e1e;
            color: #ffffff;
            font-family: 'Arial', sans-serif;
            padding: 0;
            margin: 0;
        }}
        .container-fluid {{
            padding: 20px;
        }}
        .sidebar {{
            background-color: #2d2d2d;
            padding: 20px;
            border-radius: 10px;
            color: #ffffff;
        }}
        .main-content {{
            padding: 20px;
        }}
        .card {{
            background-color: #2d2d2d;
            border: none;
            border-radius: 10px;
            margin-bottom: 20px;
            padding: 20px;
        }}
        .card-title {{
            color: #ffffff;
            font-size: 1.5rem;
            margin-bottom: 15px;
        }}
        .big-number {{
            font-size: 3rem;
            font-weight: bold;
            color: #00aaff; /* Highlight color */
            text-align: center;
        }}
        canvas {{
            background-color: #2d2d2d;
            border-radius: 10px;
            padding: 10px;
        }}
        /* Add some spacing between rows */
        .row + .row {{
            margin-top: 20px;
        }}
         /* Style for filter dropdowns */
        .form-select {{
            background-color: #1e1e1e;
            color: #ffffff;
            border: 1px solid #444;
        }}
        .form-select option {{
            background-color: #1e1e1e;
            color: #ffffff;
        }}
         /* Style for slider */
         .slider-container {{
             margin-bottom: 20px;
         }}
         .slider-container label {{
             display: block;
             margin-bottom: 10px;
         }}

    </style>
    {% endraw %}
</head>
<body>
    <div class="container-fluid">
        <div class="row">
            <!-- Sidebar for Filters -->
            <div class="col-md-3">
        <div class="sidebar">
            <h3>Filter Data</h3>
                    <form id="filter-form" method="GET" action="/">
                         <div class="mb-3">
                            <label for="genre-filter" class="form-label">Select Genre(s)</label>
                            <select class="form-select" id="genre-filter" name="genre" multiple>
                    {% for genre in all_genres %}
                                    <option value="{{ genre }}" {% if genre in selected_genres %}selected{% endif %}>{{ genre }}</option>
                    {% endfor %}
                </select>
            </div>

                        <div class="mb-3">
                            <label for="platform-filter" class="form-label">Select Platform(s)</label>
                            <select class="form-select" id="platform-filter" name="platform" multiple>
                    {% for platform in all_platforms %}
                                    <option value="{{ platform }}" {% if platform in selected_platforms %}selected{% endif %}>{{ platform }}</option>
                    {% endfor %}
                </select>
            </div>

                         <div class="slider-container">
                             <label for="year-range" class="form-label">Select Release Year Range: <span id="year-range-display">{{ year_range[0] | default(min_year) }} - {{ year_range[1] | default(max_year) }}</span></label>
                              <input type="range" class="form-range" id="year-start" name="year_start" min="{{ min_year }}" max="{{ max_year }}" value="{{ year_range[0] | default(min_year) }}">
                              <input type="range" class="form-range" id="year-end" name="year_end" min="{{ min_year }}" max="{{ max_year }}" value="{{ year_range[1] | default(max_year) }}">
                         </div>

                        <button type="submit" class="btn btn-primary">Apply Filters</button>
                    </form>
                </div>
        </div>

            <!-- Main Content Area -->
            <div class="col-md-9">
        <div class="main-content">
                    <h1 class="text-center my-4">Video Game Data Analysis Dashboard</h1>

                    {% if error %}
                        <div class="alert alert-danger" role="alert">
                            Error: {{ error }}
                        </div>
                    {% endif %}

                    <!-- Key Insights Row -->
                    <div class="row">
                        <!-- Total Games Card -->
                        <div class="col-md-4">
                            <div class="card">
                                <h5 class="card-title">Total Games Analyzed</h5>
                                <div class="big-number">{{ stats.total_games | default(0) }}</div>
                            </div>
                    </div>

                        <!-- Top Publisher Card -->
                         <div class="col-md-4">
                            <div class="card">
                                <h5 class="card-title">Top Publisher</h5>
                                 {% if publisher_counts and publisher_counts[0] %}
                                     <div class="big-number">{{ publisher_counts[0]._id }}</div>
                                     <p class="text-center text-muted">{{ publisher_counts[0].count }} games</p>
                                 {% else %}
                                     <p class="text-center text-muted">No publisher data available.</p>
                                 {% endif %}
                    </div>
                </div>

                         <!-- Most Highly Rated Games List -->
                         <div class="col-md-4">
                             <div class="card">
                                 <h5 class="card-title">Most Highly Rated Games</h5>
                                 <ul class="list-unstyled">
                                     {% for game in top_games %}
                                         <li><strong>{{ loop.index }}.</strong> {{ game.name | default('Unknown Game') }} (Rating: {{ game.rating | default(0.0) | round(1) }})</li>
                        {% else %}
                                         <li>No highly rated games found.</li>
                        {% endfor %}
                    </ul>
                             </div>
                         </div>
                    </div>

                    <hr style="border-top: 1px solid #444;">

                    <!-- General Visualizations Row 1 (Commented out) -->
                    {#
                    <div class="row">
                        <!-- Games Per Year Chart -->
                        <div class="col-md-6">
                            <div class="card">
                                <h5 class="card-title">Games Released Per Year</h5>
                                <canvas id="gamesPerYearChart"></canvas>
                            </div>
                        </div>

                        <!-- Game Share by Publisher Chart -->
                        <div class="col-md-6">
                            <div class="card">
                                <h5 class="card-title">Game Share by Publisher (Top 10)</h5>
                                <canvas id="publisherShareChart"></canvas>
                            </div>
                </div>
            </div>
                    #}

                    <!-- General Visualizations Row 2 (Commented out) -->
                    {#
                    <div class="row">
                         <!-- Game Counts by Platform Chart -->
                        <div class="col-md-6">
                            <div class="card">
                                <h5 class="card-title">Game Distribution by Platform</h5>
                                <canvas id="platformChart"></canvas>
                            </div>
                        </div>

                        <!-- Game Counts by Genre Chart -->
                        <div class="col-md-6">
                            <div class="card">
                                <h5 class="card-title">Game Distribution by Genre</h5>
                                <canvas id="genreChart"></canvas>
                </div>
                </div>
            </div>
                    #}

                     <!-- Deep Dive Analysis Row (Commented out) -->
                     {#
                     <div class="row">
                          <!-- Average Rating by Platform Chart -->
                        <div class="col-md-6">
                            <div class="card">
                                <h5 class="card-title">Average Rating by Platform (Top 10)</h5>
                                <canvas id="avgRatingPlatformChart"></canvas>
                            </div>
                        </div>

                        <!-- Average Rating by Developer Chart -->
                        <div class="col-md-6">
                            <div class="card">
                                <h5 class="card-title">Average Rating by Developer (Top 10)</h5>
                                <canvas id="avgRatingDeveloperChart"></canvas>
                            </div>
                        </div>
            </div>
                     #}\

                    <!-- You can add sections here for mapping data if needed -->
                    {#
                    <div class="row">
                        <div class="col-md-12">
                            <div class="card">
                                <h5 class="card-title">Publisher Mapping (Example)</h5>
                                <pre>{{ publisher_mapping | tojson(indent=2) }}</pre>
                            </div>
                        </div>
                    </div>
                    #}\

                </div>
            </div>
        </div>
    </div>

    <script>
        // Data passed from Flask backend as JSON strings
        const stats = {{ stats_data | tojson | safe }};
        const topGames = {{ top_games | tojson | safe }};
        const platformCounts = {{ platform_counts | tojson | safe }};
        const genreCounts = {{ genre_counts | tojson | safe }};
        const gamesPerYear = {{ games_per_year | tojson | safe }};
        const publisherCounts = {{ publisher_counts | tojson | safe }};
        const avgRatingPlatform = {{ avg_rating_platform | tojson | safe }};
        const avgRatingDeveloper = {{ avg_rating_developer | tojson | safe }};
        const allGenres = {{ all_genres | tojson | safe }};
        const allPlatforms = {{ all_platforms | tojson | safe }};
        const minYearData = {{ min_year_data | tojson | safe }};
        const maxYearData = {{ max_year_data | tojson | safe }};
        const yearRange = {{ year_range | tojson | safe }};


        // --- Chart Rendering Functions using Chart.js (Copied from static/js/DS.js) ---
        document.addEventListener('DOMContentLoaded', function() {
            // Filter form elements
            const genreFilter = document.getElementById('genre-filter');
            const platformFilter = document.getElementById('platform-filter');
            const yearStartInput = document.getElementById('year-start');
            const yearEndInput = document.getElementById('year-end');
            const filterForm = document.getElementById('filter-form');
            const yearRangeDisplay = document.getElementById('year-range-display');

             // Function to update year range display
             function updateYearRangeDisplay() {{
                 if (yearStartInput && yearEndInput && yearRangeDisplay) {{
                      yearRangeDisplay.textContent = `${{yearStartInput.value}} - ${{yearEndInput.value}}`;
                 }}
             }}

            // Initial update of year range display on page load
            if (yearStartInput && yearEndInput && yearRangeDisplay) {{
                yearStartInput.addEventListener('input', updateYearRangeDisplay);
                yearEndInput.addEventListener('input', updateYearRangeDisplay);
                updateYearRangeDisplay(); // Call on load to set initial value
            }}


            // Note: Chart rendering functions are defined here but called later.
            // Uncomment these sections and the corresponding HTML canvas elements
            // when you are ready to display the charts.

            // Function to render Games Per Year Chart
            function renderGamesPerYearChart(data) {{
                const ctx = document.getElementById('gamesPerYearChart');
                 if (!ctx) {{ console.warn("Canvas element 'gamesPerYearChart' not found."); return; }}
                const myChart = new Chart(ctx, {{
                    type: 'line',
                    data: {{
                        labels: data.map(item => item._id).sort(), // Assuming _id is the year
                        datasets: [{{
                            label: 'Number of Games',
                            data: data.map(item => item.count),
                            borderColor: 'rgba(75, 192, 192, 1)',
                            backgroundColor: 'rgba(75, 192, 192, 0.2)',
                            fill: true,
                        }}]
                    }},
                    options: {{
                        responsive: true,
                        scales: {{
                            x: {{
                                title: {{
                                    display: true,
                                    text: 'Year'
                                }}
                            }},
                            y: {{
                                title: {{
                                    display: true,
                                    text: 'Number of Games'
                                }},
                                beginAtZero: true
                            }}
                        }},
                        plugins: {{
                            title: {{
                                display: true,
                                text: 'Games Released Per Year'
                            }}
                        }}
                    }}
                }});
            }}

            // Function to render Game Share by Publisher Chart (Pie Chart)
            function renderPublisherShareChart(data) {{
                // Take top 10 publishers
                const top10Data = data.slice(0, 10);

                const ctx = document.getElementById('publisherShareChart');
                 if (!ctx) {{ console.warn("Canvas element 'publisherShareChart' not found."); return; }}
                const myChart = new Chart(ctx, {{
                    type: 'pie',
                    data: {{
                        labels: top10Data.map(item => item._id),
                        datasets: [{{
                            label: 'Game Count',
                            data: top10Data.map(item => item.count),
                             backgroundColor: [
                                '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966CC', '#FF9F40',
                                '#FFCD56', '#4CC0C0', '#9666CC', '#FF9940'
                            ],
                            hoverOffset: 4
                        }}]
                    }},
                    options: {{
                        responsive: true,
                        plugins: {{
                            title: {{
                                display: true,
                                text: 'Game Share by Publisher (Top 10)'
                            }}
                        }}
                    }}
                }});
            }}

             // Function to render Game Distribution by Platform Chart (Bar Chart)
             function renderPlatformChart(data) {{
                // Sort by count descending
                 const sortedData = data.sort((a, b) => b.count - a.count);

                 const ctx = document.getElementById('platformChart');
                  if (!ctx) {{ console.warn("Canvas element 'platformChart' not found."); return; }}
                 const myChart = new Chart(ctx, {{
                     type: 'bar',
                     data: {{
                         labels: sortedData.map(item => item._id),
                         datasets: [{{
                             label: 'Number of Games',
                             data: sortedData.map(item => item.count),
                             backgroundColor: 'rgba(54, 162, 235, 0.6)',
                             borderColor: 'rgba(54, 162, 235, 1)',
                             borderWidth: 1
                         }}]
                     }},
                     options: {{
                         responsive: true,
                         scales: {{
                             y: {{
                                 beginAtZero: true,
                                 title: {{
                                     display: true,
                                     text: 'Number of Games'
                                 }}
                             }},
                             x: {{
                                 title: {{
                                     display: true,
                                     text: 'Platform'
                                 }}
                             }}
                         }},
                         plugins: {{
                             title: {{
                                 display: true,
                                 text: 'Game Distribution by Platform'
                             }},
                              legend: {{
                                 display: false // Hide legend for single dataset bar chart
                             }}
                         }}
                     }}
                 }});
             }}

             // Function to render Game Distribution by Genre Chart (Bar Chart)
             function renderGenreChart(data) {{
                 // Sort by count descending
                 const sortedData = data.sort((a, b) => b.count - a.count);

                 const ctx = document.getElementById('genreChart');
                  if (!ctx) {{ console.warn("Canvas element 'genreChart' not found."); return; }}
                 const myChart = new Chart(ctx, {{
                     type: 'bar',
                     data: {{
                         labels: sortedData.map(item => item._id),
                         datasets: [{{
                             label: 'Number of Games',
                             data: sortedData.map(item => item.count),
                             backgroundColor: 'rgba(255, 99, 132, 0.6)',
                             borderColor: 'rgba(255, 99, 132, 1)',
                             borderWidth: 1
                         }}]
                     }},
                     options: {{
                         responsive: true,
                         scales: {{
                             y: {{
                                 beginAtZero: true,
                                 title: {{
                                     display: true,
                                     text: 'Number of Games'
                                 }}
                             }},
                             x: {{
                                 title: {{
                                     display: true,
                                     text: 'Genre'
                                 }}
                             }}
                         }},
                         plugins: {{
                             title: {{
                                 display: true,
                                 text: 'Game Distribution by Genre'
                             }},
                             legend: {{
                                 display: false // Hide legend for single dataset bar chart
                             }}
                         }}
                     }}
                 }});
             }}

             // Function to render Average Rating by Platform Chart (Bar Chart)
             function renderAvgRatingPlatformChart(data) {{
                 // Sort by average rating descending and take top 10
                 const top10Data = data.sort((a, b) => b.average_rating - a.average_rating).slice(0, 10);

                 const ctx = document.getElementById('avgRatingPlatformChart');
                  if (!ctx) {{ console.warn("Canvas element 'avgRatingPlatformChart' not found."); return; }}
                 const myChart = new Chart(ctx, {{
                     type: 'bar',
                     data: {{
                         labels: top10Data.map(item => item._id),
                         datasets: [{{
                             label: 'Average Rating',
                             data: top10Data.map(item => item.average_rating),
                             backgroundColor: 'rgba(153, 102, 255, 0.6)',
                             borderColor: 'rgba(153, 102, 255, 1)',
                             borderWidth: 1
                         }}]
                     }},
                     options: {{
                         responsive: true,
                         scales: {{
                             y: {{
                                 beginAtZero: true,
                                 title: {{
                                     display: true,
                                     text: 'Average Rating'
                                 }}
                             }},
                             x: {{
                                 title: {{
                                     display: true,
                                     text: 'Platform'
                                 }}
                             }}
                         }},
                         plugins: {{
                             title: {{
                                 display: true,
                                 text: 'Average Rating by Platform (Top 10)'
                             }},
                             legend: {{
                                 display: false // Hide legend
                             }}
                         }}
                     }}
                 }});
             }}

             // Function to render Average Rating by Developer Chart (Bar Chart)
             function renderAvgRatingDeveloperChart(data) {{
                 // Sort by average rating descending and take top 10
                 const top10Data = data.sort((a, b) => b.average_rating - a.average_rating).slice(0, 10);

                 const ctx = document.getElementById('avgRatingDeveloperChart');
                 if (!ctx) {{ console.warn("Canvas element 'avgRatingDeveloperChart' not found."); return; }}
                 const myChart = new Chart(ctx, {{
                     type: 'bar',
                     data: {{
                         labels: top10Data.map(item => item._id),
                         datasets: [{{
                             label: 'Average Rating',
                             data: top10Data.map(item => item.average_rating),
                             backgroundColor: 'rgba(255, 159, 64, 0.6)',
                             borderColor: 'rgba(255, 159, 64, 1)',
                             borderWidth: 1
                         }}]
                     }},
                     options: {{
                         responsive: true,
                         scales: {{
                             y: {{
                                 beginAtZero: true,
                                 title: {{
                                     display: true,
                                     text: 'Average Rating'
                                 }}
                             }},
                             x: {{
                                 title: {{
                                     display: true,
                                     text: 'Developer'
                                 }}
                             }}
                         }},
                         plugins: {{
                             title: {{
                                 display: true,
                                 text: 'Average Rating by Developer (Top 10)'
                             }},
                              legend: {{
                                 display: false // Hide legend
                              }}
                         }}
                     }}
                 }});
             }}


            // Function to render all charts using the global data variables
            // Note: Chart canvases are commented out in HTML for now.
            // Uncomment the chart HTML sections when ready to display charts.
            function renderAllCharts() {{
                console.log("Attempting to render charts...");
                 // Check if global data variables exist and are not empty before rendering
                 if (typeof gamesPerYear !== 'undefined' && gamesPerYear && gamesPerYear.length > 0) {{
                      console.log("Rendering Games Per Year chart with data:", gamesPerYear);
                      renderGamesPerYearChart(gamesPerYear);
                  }} else {{
                      console.warn("No data available or data is empty for Games Per Year chart.");
                  }}

                  if (typeof publisherCounts !== 'undefined' && publisherCounts && publisherCounts.length > 0) {{
                       console.log("Rendering Publisher Share chart with data:", publisherCounts);
                       renderPublisherShareChart(publisherCounts);
                   }} else {{
                       console.warn("No data available or data is empty for Publisher Share chart.");
                   }}

                  if (typeof platformCounts !== 'undefined' && platformCounts && platformCounts.length > 0) {{
                      console.log("Rendering Platform Distribution chart with data:", platformCounts);
                      renderPlatformChart(platformCounts);
                   }} else {{
                       console.warn("No data available or data is empty for Platform Distribution chart.");
                   }}

                   if (typeof genreCounts !== 'undefined' && genreCounts && genreCounts.length > 0) {{
                       console.log("Rendering Genre Distribution chart with data:", genreCounts);
                       renderGenreChart(genreCounts);
                   }} else {{
                        console.warn("No data available or data is empty for Genre Distribution chart.");
                   }}

                   if (typeof avgRatingPlatform !== 'undefined' && avgRatingPlatform && avgRatingPlatform.length > 0) {{
                       console.log("Rendering Average Rating by Platform chart with data:", avgRatingPlatform);
                       renderAvgRatingPlatformChart(avgRatingPlatform);
                    }} else {{
                        console.warn("No data available or data is empty for Average Rating by Platform chart.");
                    }}

                   if (typeof avgRatingDeveloper !== 'undefined' && avgRatingDeveloper && avgRatingDeveloper.length > 0) {{
                       console.log("Rendering Average Rating by Developer chart with data:", avgRatingDeveloper);
                       renderAvgRatingDeveloperChart(avgRatingDeveloper);
                   }} else {{
                       console.warn("No data available or data is empty for Average Rating by Developer chart.");
                   }}
            }}

            // --- Filter Form Submission ---
            if (filterForm) {{
                filterForm.addEventListener('submit', function(event) {{
                    event.preventDefault(); // Prevent default form submission
                    const formData = new FormData(filterForm);
                    const queryParams = new URLSearchParams(formData).toString();
                    window.location.href = '/' + (queryParams ? '?' + queryParams : ''); // Redirect with query params
                }});
            }}

            // Call renderAllCharts initially and potentially after filter apply (currently page redirects)
            // renderAllCharts(); // Commented out because chart canvases are commented out in HTML
        });

    </script>
    {% endraw %}
</body>
</html>
"""
    # --- End Embedded HTML Template ---


    # Render the HTML string
    return render_template_string(html_template,
                                  stats=stats_data,
                                  top_games=top_games,
                                  platform_counts=platform_counts,
                                  genre_counts=genre_counts,
                                  games_per_year=games_per_year,
                                  publisher_counts=publisher_counts,
                                  avg_rating_platform=avg_rating_platform,
                                  avg_rating_developer=avg_rating_developer,
                                  all_genres=all_genres,
                                  all_platforms=all_platforms,
                                  min_year=min_year_data,
                                  max_year=max_year_data,
                                  year_range=year_range,
                                  selected_genres=selected_genres, # Pass back selected filters for dropdowns
                                  selected_platforms=selected_platforms,
                                  min_year_for_filter=min_year_data, # Pass min/max for filter display
                                  max_year_for_filter=max_year_data,
                                  error=error)


if __name__ == '__main__':
    # To run in debug mode:
    # Use a different port if 5000 is already in use
    app.run(debug=True, port=5001)
    # To run in production:
    # app.run() 