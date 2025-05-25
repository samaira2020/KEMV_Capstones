from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.errors import ConnectionFailure
import pandas as pd
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MongoDBHandler:
    def __init__(self, connection_string='mongodb://localhost:27017/'):
        """Initialize MongoDB connection."""
        try:
            self.client = MongoClient(connection_string)
            self.db = self.client['Capstones']
            logger.info("Successfully connected to MongoDB")
        except ConnectionFailure as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise

    def get_collection(self, collection_name):
        """Get a specific collection from the database."""
        return self.db[collection_name]

    # Helper to build match query from filters
    def _build_filter_match(self, genres=None, platforms=None, year_range=None):
        match_conditions = []
        # Ensure the 'Title' and 'Rating' fields exist and Rating is a number
        # Only keep the base conditions here
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

    # === Analytics Queries ===
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

    # === Dashboard Analytics Queries (based on available data) ===
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
            #              '$gte': year_range[0],
            #              '$lte': year_range[1],
            #              '$exists': True,
            #              '$ne': None,
            #              '$type': 'number'
            #          }
            #      })

            # 4. Unwind the PlatformsArray
            pipeline.append({'$unwind': '$PlatformsArray'})

            # Add a match stage to filter out empty platform strings after unwinding
            pipeline.append({'$match': {'PlatformsArray': {'$ne': '', '$exists': True, '$ne': None}}})

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
        """Get the number of games released per year without extracting year, for range determination."""
        collection = self.get_collection(collection_name)
        pipeline = [
             # Only include documents with a valid Release_Date_IGDB for year extraction
             {'$match': {'Release_Date_IGDB': {'$exists': True, '$ne': None, '$type': 'string'}}},
             {'$project': {'_id': 0, 'year': {'$toInt': {'$arrayElemAt': [{'$split': ['$Release_Date_IGDB', '/']}, 2]}}}}
        ]
        logger.info(f"Executing aggregation pipeline for get_games_per_year_raw: {pipeline}")
        # Use allowDiskUse=True for potentially large aggregations
        return list(collection.aggregate(pipeline, allowDiskUse=True))

    def get_games_per_year(self, collection_name='enriched_games', genres=None, platforms=None, year_range=None):
        """Get the number of games released per year, with filters."""
        collection = self.get_collection(collection_name)
        pipeline = []

        # 1. Add fields for PlatformsArray, GenresArray, and extractedYear
        pipeline.append({
            '$addFields': {
                'PlatformsArray': {'$split': [{'$ifNull': ['$Platform', '']}, ', ']},
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

        # 3. Apply year range filter on the extracted year
        if year_range and len(year_range) == 2:
             pipeline.append({
                 '$match': {
                     'extractedYear': {
                         '$gte': year_range[0],
                         '$lte': year_range[1],
                         '$exists': True,
                         '$ne': None,
                         '$type': 'number'
                     }
                 }
             })

        # 4. Apply genre filter
        if genres:
            pipeline.append({'$match': {'GenresArray': {'$in': genres}}})

        # 5. Apply platform filter
        if platforms:
            pipeline.append({'$match': {'PlatformsArray': {'$in': platforms}}})

        # Log count after filtering
        # This requires a separate stage or $facet which is complex. Logging pipeline stages instead.
        print(f"Pipeline after filtering in get_games_per_year: {pipeline}")

        # 6. Group by extracted year and count
        # Only group if extractedYear is a valid number
        pipeline.append({
            '$match': {
                'extractedYear': {
                    '$exists': True,
                    '$ne': None,
                    '$type': 'number'
                }
            }
        }) # Ensure extractedYear is valid before grouping
        pipeline.append({
            '$group': {
                '_id': '$extractedYear',
                'count': {'$sum': 1}
            }
        })

        # 7. Sort by year
        pipeline.append({'$sort': {'_id': 1}})

        print(f"Executing aggregation pipeline for get_games_per_year: {pipeline}")
        result = list(collection.aggregate(pipeline, allowDiskUse=True))
        print(f"Result from get_games_per_year: {result}")
        return result

    def get_games_count_by_publisher(self, collection_name='enriched_games', genres=None, platforms=None, year_range=None):
        """Get the count of games per publisher, with filters."""
        collection = self.get_collection(collection_name)
        pipeline = []

        # 1. Add fields for PlatformsArray, GenresArray, and extractedYear
        pipeline.append({
            '$addFields': {
                'PlatformsArray': {'$split': [{'$ifNull': ['$Platform', '']}, ', ']},
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

        # 3. Apply year range filter
        if year_range and len(year_range) == 2:
             pipeline.append({
                 '$match': {
                     'extractedYear': {
                         '$gte': year_range[0],
                         '$lte': year_range[1],
                         '$exists': True,
                         '$ne': None,
                         '$type': 'number'
                     }
                 }
             })

        # 4. Apply genre filter
        if genres:
            pipeline.append({'$match': {'GenresArray': {'$in': genres}}})

        # 5. Apply platform filter
        if platforms:
            pipeline.append({'$match': {'PlatformsArray': {'$in': platforms}}})

        # Log count after filtering
        print(f"Pipeline after filtering in get_games_count_by_publisher: {pipeline}")

        # 6. Group by publisher and count
        pipeline.append({
            '$group': {
                '_id': '$Publisher',
                'count': {'$sum': 1}
            }
        })

        # 7. Sort by count
        pipeline.append({'$sort': {'count': -1}})

        print(f"Executing aggregation pipeline for get_games_count_by_publisher: {pipeline}")
        result = list(collection.aggregate(pipeline, allowDiskUse=True))
        print(f"Result from get_games_count_by_publisher: {result}")
        return result

    def get_avg_rating_by_platform(self, collection_name='enriched_games', genres=None, platforms=None, year_range=None):
        """Get the average rating per platform, with filters."""
        collection = self.get_collection(collection_name)
        pipeline = []

        # 1. Add fields for PlatformsArray, GenresArray, and extractedYear
        pipeline.append({
            '$addFields': {
                'PlatformsArray': {'$split': [{'$ifNull': ['$Platform', '']}, ', ']},
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

        # 3. Apply year range filter
        if year_range and len(year_range) == 2:
             pipeline.append({
                 '$match': {
                     'extractedYear': {
                         '$gte': year_range[0],
                         '$lte': year_range[1],
                         '$exists': True,
                         '$ne': None,
                         '$type': 'number'
                     }
                 }
             })

        # 4. Unwind the PlatformsArray
        pipeline.append({'$unwind': '$PlatformsArray'})

        # 5. Apply genre filter
        if genres:
            pipeline.append({'$match': {'GenresArray': {'$in': genres}}})

        # 6. Apply platform filter after unwinding
        if platforms:
            pipeline.append({'$match': {'PlatformsArray': {'$in': platforms}}})

        # Log pipeline stages before grouping
        print(f"Pipeline stages before grouping in get_avg_rating_by_platform: {pipeline}")

        # 7. Group by platform and calculate average rating
        pipeline.append({
            '$group': {
                '_id': '$PlatformsArray',
                'avg_rating': {'$avg': '$Rating'}
            }
        })

        # 8. Filter out documents where avg_rating is null
        pipeline.append({'$match': {'avg_rating': {'$ne': None}}})

        # 9. Sort by average rating
        pipeline.append({'$sort': {'avg_rating': -1}})

        print(f"Executing aggregation pipeline for get_avg_rating_by_platform: {pipeline}")
        result = list(collection.aggregate(pipeline, allowDiskUse=True))
        print(f"Result from get_avg_rating_by_platform: {result}")
        return result

    def get_avg_rating_by_developer(self, collection_name='enriched_games', genres=None, platforms=None, year_range=None):
        """Get the average rating per developer, with filters."""
        collection = self.get_collection(collection_name)
        pipeline = []

        # 1. Add fields for PlatformsArray, GenresArray, and extractedYear
        pipeline.append({
            '$addFields': {
                'PlatformsArray': {'$split': [{'$ifNull': ['$Platform', '']}, ', ']},
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

        # 3. Apply year range filter
        if year_range and len(year_range) == 2:
             pipeline.append({
                 '$match': {
                     'extractedYear': {
                         '$gte': year_range[0],
                         '$lte': year_range[1],
                         '$exists': True,
                         '$ne': None,
                         '$type': 'number'
                     }
                 }
             })

        # 4. Apply genre filter
        if genres:
            pipeline.append({'$match': {'GenresArray': {'$in': genres}}})

        # 5. Apply platform filter
        if platforms:
            pipeline.append({'$match': {'PlatformsArray': {'$in': platforms}}})

        # Log pipeline stages before grouping
        print(f"Pipeline stages before grouping in get_avg_rating_by_developer: {pipeline}")

        # 6. Group by developer and calculate average rating
        pipeline.append({
            '$group': {
                '_id': '$Developer',
                'avg_rating': {'$avg': '$Rating'}
            }
        })

        # 7. Filter out documents where avg_rating is null
        pipeline.append({'$match': {'avg_rating': {'$ne': None}}})

        # 8. Sort by average rating
        pipeline.append({'$sort': {'avg_rating': -1}})

        print(f"Executing aggregation pipeline for get_avg_rating_by_developer: {pipeline}")
        result = list(collection.aggregate(pipeline, allowDiskUse=True))
        print(f"Result from get_avg_rating_by_developer: {result}")
        return result

    def get_games(self, limit=20):
        """Fetches a list of game documents from the enriched_games collection."""
        try:
            print(f"Fetching {limit} games from the enriched_games collection.")
            # Define the aggregation pipeline
            pipeline = [
                # Optionally add stages for filtering, sorting, etc. here later
                { '$limit': limit } # Limit the number of results
            ]
            
            print(f"Executing aggregation pipeline for get_games: {pipeline}")
            games = list(self.db.enriched_games.aggregate(pipeline, allowDiskUse=True))
            print(f"Fetched {len(games)} games from get_games.")
            return games
        except Exception as e:
            print(f"Error in get_games: {e}")
            return []
