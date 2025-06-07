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
        # Temporarily return empty to match all documents for debugging
        # return {}

        # Reverted to include base filtering logic
        match_query = {
            '$and': [
                {'Title': {'$exists': True, '$ne': None, '$type': 'string'}},
                {'Rating': {'$exists': True, '$ne': None, '$type': 'number'}},
                {'Platform': {'$exists': True, '$ne': None, '$type': 'string'}},
                {'Genre': {'$exists': True, '$ne': None, '$type': 'string'}},
                {'Publisher': {'$exists': True, '$ne': None, '$type': 'string'}}
            ]
        }
        # Note: Genre, Platform, and Year filters will be applied later in specific pipelines
        return match_query

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

            # 1. Add field for extractedYear
            pipeline.append({
                '$addFields': {
                    'extractedYear': {
                        '$toInt': {
                            '$arrayElemAt': [{'$split': [{'$ifNull': ['$Release_Date_IGDB', '']}, '/']}, 2] # Get the last part (YYYY)
                        }
                    }
                }
            })

            # 2. Apply base filters (existence and type checks) using _build_filter_match
            # Temporarily commented out to see total count without strict base filters
            # match_query = self._build_filter_match() # Use base conditions only
            # if match_query:
            #      pipeline.append({'$match': match_query})

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

            # Add stage to count total documents (games)
            # Ensure Title exists - redundant if _build_filter_match is used
            # pipeline.append({'$match': {'Title': {'$exists': True, '$ne': None}}})
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

            # 1. Add field for extractedYear and arrays for filtering
            pipeline.append({
                '$addFields': {
                    'extractedYear': {
                        '$toInt': {
                            '$arrayElemAt': [{'$split': [{'$ifNull': ['$Release_Date_IGDB', '']}, '/']}, 2] # Get the last part (YYYY)
                        }
                    },
                    'PlatformsArray': {'$split': [{'$ifNull': ['$Platform', '']}, ', ']}, # Add PlatformsArray
                    'GenresArray': {'$split': [{'$ifNull': ['$Genre', '']}, ', ']} # Add GenresArray
                }
            })

            # 2. Apply base filters (existence and type checks)
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

            # 6. Sort by Rating (descending) and limit
            pipeline.append({'$sort': {'Rating': -1}})
            pipeline.append({'$limit': limit})

            # 7. Project to rename fields for frontend and ensure correct types
            pipeline.append({
                '$project': {
                    '_id': 0, # Exclude default _id
                    'name': {'$toString': {'$ifNull': ['$Title', '']}}, # Ensure name is string
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
        """Counts games per genre, with optional filters."""
        try:
            print(f"Fetching game counts by genre.")
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

            # 2. Filter to ensure Genre exists
            pipeline.append({
                '$match': {
                    'Genre': {'$exists': True, '$ne': None, '$ne': ''}
                }
            })

            # 3. Apply year range filter if provided
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

            # 4. Unwind the GenresArray
            pipeline.append({'$unwind': '$GenresArray'})

            # 5. Add a match stage to filter out empty genre strings after unwinding
            pipeline.append({'$match': {'GenresArray': {'$ne': '', '$exists': True, '$ne': None}}})

            # 6. Group by genre and count
            pipeline.append({
                '$group': {
                    '_id': '$GenresArray',
                    'count': {'$sum': 1}
                }
            })

            # 7. Filter out documents where _id is null or empty after grouping
            pipeline.append({'$match': {'_id': {'$ne': None, '$ne': '', '$exists': True}}})

            # 8. Sort by count (descending)
            pipeline.append({'$sort': {'count': -1}})

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
                },

                # 2. Unwind the PlatformsArray
                {'$unwind': '$PlatformsArray'},

                # 3. Add a match stage to filter out empty platform strings after unwinding
                {'$match': {'PlatformsArray': {'$ne': '', '$exists': True, '$ne': None}}},

                # 4. Group by platform and count
                {
                    '$group': {
                        '_id': '$PlatformsArray',
                        'count': {'$sum': 1}
                    }
                },

                # 5. Filter out documents where _id is null or empty after grouping
                {'$match': {'_id': {'$ne': None, '$ne': '', '$exists': True}}},

                # 6. Sort by count (descending)
                {'$sort': {'count': -1}}
            ]

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
            {'$project': {'_id': 0, 'extractedYear': {'$toInt': {'$arrayElemAt': [{'$split': [{'$ifNull': ['$Release_Date_IGDB', '']}, '/']}, 2]}}}}
            # Add a match stage to ensure extractedYear is a valid number after projection
            ,{'$match': {'extractedYear': {'$exists': True, '$ne': None, '$type': 'number'}}}
        ]
        logger.info(f"Executing aggregation pipeline for get_games_per_year_raw: {pipeline}")
        # Use allowDiskUse=True for potentially large aggregations
        return list(collection.aggregate(pipeline, allowDiskUse=True))

    def get_games_per_year(self, collection_name='enriched_games', genres=None, platforms=None, year_range=None):
        """Get the number of games released per year, with filters."""
        collection = self.get_collection(collection_name)
        pipeline = []

        # 1. Add field for extractedYear
        pipeline.append({
            '$addFields': {
                'extractedYear': {
                    '$toInt': {
                        '$arrayElemAt': [{'$split': [{'$ifNull': ['$Release_Date_IGDB', '']}, '/']}, 2] # Get the last part (YYYY)
                    }
                }
            }
        })

        # 2. Filter out documents where extractedYear is not a valid number
        pipeline.append({
            '$match': {
                'extractedYear': {
                    '$exists': True,
                    '$ne': None,
                    '$type': 'number'
                }
            }
        })

        # 3. Apply year range filter if provided
        if year_range and len(year_range) == 2:
             pipeline.append({
                 '$match': {
                     'extractedYear': {
                         '$gte': year_range[0],
                         '$lte': year_range[1]
                     }
                 }
             })

        # 4. Group by extractedYear and count
        pipeline.append({
            '$group': {
                '_id': '$extractedYear',
                'count': {'$sum': 1}
            }
        })

        # 5. Sort by year
        pipeline.append({'$sort': {'_id': 1}})

        # 6. Project to rename _id to year for frontend compatibility
        pipeline.append({
            '$project': {
                '_id': 0,
                'year': '$_id',
                'count': 1
            }
        })

        print(f"Executing aggregation pipeline for get_games_per_year: {pipeline}")
        result = list(collection.aggregate(pipeline, allowDiskUse=True))
        print(f"Result from get_games_per_year: {result}")
        return result

    def get_games_count_by_publisher(self, collection_name='enriched_games', genres=None, platforms=None, year_range=None):
        """Get the count of games per publisher, with filters."""
        collection = self.get_collection(collection_name)
        pipeline = []

        # 1. Add field for extractedYear
        pipeline.append({
            '$addFields': {
                'extractedYear': {
                    '$toInt': {
                        '$arrayElemAt': [{'$split': [{'$ifNull': ['$Release_Date_IGDB', '']}, '/']}, 2] # Get the last part (YYYY)
                    }
                }
            }
        })

        # 2. Filter to ensure Publisher exists and is not null
        pipeline.append({
            '$match': {
                'Publisher': {'$exists': True, '$ne': None, '$ne': ''}
            }
        })

        # 3. Apply year range filter if provided
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

        # 4. Group by Publisher and count
        pipeline.append({
            '$group': {
                '_id': '$Publisher',
                'count': {'$sum': 1}
            }
        })

        # 5. Filter out null or empty publishers after grouping
        pipeline.append({'$match': {'_id': {'$ne': None, '$ne': '', '$exists': True}}})

        # 6. Sort by count (descending)
        pipeline.append({'$sort': {'count': -1}})

        print(f"Executing aggregation pipeline for get_games_count_by_publisher: {pipeline}")
        result = list(collection.aggregate(pipeline, allowDiskUse=True))
        print(f"Result from get_games_count_by_publisher: {result}")
        return result

    def get_avg_rating_by_platform(self, collection_name='enriched_games', genres=None, platforms=None, year_range=None):
        """Get the average rating per platform, with filters."""
        collection = self.get_collection(collection_name)
        pipeline = []

        # 1. Add fields for PlatformsArray and extractedYear
        pipeline.append({
            '$addFields': {
                'PlatformsArray': {'$split': [{'$ifNull': ['$Platform', '']}, ', ']},
                'extractedYear': {
                    '$toInt': {
                        '$arrayElemAt': [{'$split': [{'$ifNull': ['$Release_Date_IGDB', '']}, '/']}, 2] # Get the last part (YYYY)
                    }
                }
            }
        })

        # 2. Filter to ensure Rating exists and is a number
        pipeline.append({
            '$match': {
                'Rating': {'$exists': True, '$ne': None, '$type': 'number'},
                'Platform': {'$exists': True, '$ne': None, '$ne': ''}
            }
        })

        # 3. Apply year range filter if provided
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

        # 4. Unwind PlatformsArray
        pipeline.append({'$unwind': '$PlatformsArray'})

        # 5. Filter out empty platforms after unwinding
        pipeline.append({'$match': {'PlatformsArray': {'$ne': '', '$exists': True, '$ne': None}}})

        # 6. Group by platform and calculate average rating
        pipeline.append({
            '$group': {
                '_id': '$PlatformsArray',
                'avg_rating': {'$avg': '$Rating'}
            }
        })

        # 7. Filter out documents where avg_rating is null
        pipeline.append({'$match': {'avg_rating': {'$ne': None}}})

        # 8. Sort by average rating (descending)
        pipeline.append({'$sort': {'avg_rating': -1}})

        # 9. Project to rename _id to platform for frontend compatibility
        pipeline.append({
            '$project': {
                '_id': 0,
                'platform': '$_id',
                'avg_rating': {'$round': ['$avg_rating', 2]}
            }
        })

        print(f"Executing aggregation pipeline for get_avg_rating_by_platform: {pipeline}")
        result = list(collection.aggregate(pipeline, allowDiskUse=True))
        print(f"Result from get_avg_rating_by_platform: {result}")
        return result

    def get_avg_rating_by_developer(self, collection_name='enriched_games', genres=None, platforms=None, year_range=None):
        """Get the average rating per developer, with filters."""
        collection = self.get_collection(collection_name)
        pipeline = []

        # 1. Add field for extractedYear
        pipeline.append({
            '$addFields': {
                'extractedYear': {
                    '$toInt': {
                        '$arrayElemAt': [{'$split': [{'$ifNull': ['$Release_Date_IGDB', '']}, '/']}, 2] # Get the last part (YYYY)
                    }
                }
            }
        })

        # 2. Filter to ensure Rating and Developer exist
        pipeline.append({
            '$match': {
                'Rating': {'$exists': True, '$ne': None, '$type': 'number'},
                'Developer': {'$exists': True, '$ne': None, '$ne': ''}
            }
        })

        # 3. Apply year range filter if provided
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

        # 4. Group by developer and calculate average rating
        pipeline.append({
            '$group': {
                '_id': '$Developer',
                'avg_rating': {'$avg': '$Rating'}
            }
        })

        # 5. Filter out documents where avg_rating is null
        pipeline.append({'$match': {'avg_rating': {'$ne': None}}})

        # 6. Sort by average rating (descending)
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

    # === Enhanced Analytics Methods Using All Collections ===
    
    def get_director_analytics(self, year_range=None, limit=10, months=None, min_rating=None):
        """Get analytics for directors including average rating, game count, and total votes with optional filters."""
        try:
            print(f"Fetching director analytics.")
            collection = self.db.enriched_games
            pipeline = []

            # 1. Add field for extractedYear and month with proper error handling
            pipeline.append({
                '$addFields': {
                    'extractedYear': {
                        '$convert': {
                            'input': {'$arrayElemAt': [{'$split': [{'$ifNull': ['$Release_Date_IGDB', '']}, '/']}, 2]},
                            'to': 'int',
                            'onError': None,
                            'onNull': None
                        }
                    },
                    'extractedMonth': {
                        '$convert': {
                            'input': {'$arrayElemAt': [{'$split': [{'$ifNull': ['$Release_Date_IGDB', '']}, '/']}, 0]},
                            'to': 'int',
                            'onError': None,
                            'onNull': None
                        }
                    }
                }
            })

            # 2. Filter for valid data - using 'Directors' field (plural)
            match_conditions = {
                'Directors': {'$exists': True, '$ne': None, '$ne': ''},
                'Rating': {'$exists': True, '$ne': None, '$type': 'number'}
            }

            # Add month filter if provided
            if months:
                match_conditions['extractedMonth'] = {'$in': months, '$ne': None, '$type': 'number'}

            # Add rating filter if provided
            if min_rating:
                match_conditions['Rating'] = {'$gte': float(min_rating)}

            pipeline.append({'$match': match_conditions})

            # 3. Apply year range filter if provided
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

            # 4. Group by director - using 'Directors' field (plural)
            pipeline.append({
                '$group': {
                    '_id': '$Directors',
                    'avg_rating': {'$avg': '$Rating'},
                    'game_count': {'$sum': 1},
                    'total_votes': {'$sum': '$Number_of_Votes'},
                    'max_rating': {'$max': '$Rating'},
                    'min_rating': {'$min': '$Rating'}
                }
            })

            # 5. Filter directors with at least 2 games
            pipeline.append({'$match': {'game_count': {'$gte': 2}}})

            # 6. Sort by average rating descending
            pipeline.append({'$sort': {'avg_rating': -1}})

            # 7. Limit results
            pipeline.append({'$limit': limit})

            # 8. Project for frontend
            pipeline.append({
                '$project': {
                    '_id': 0,
                    'director': '$_id',
                    'avg_rating': {'$round': ['$avg_rating', 2]},
                    'game_count': 1,
                    'total_votes': 1,
                    'max_rating': {'$round': ['$max_rating', 1]},
                    'min_rating': {'$round': ['$min_rating', 1]}
                }
            })

            result = list(collection.aggregate(pipeline, allowDiskUse=True))
            print(f"Director analytics result: {len(result)} directors")
            return result

        except Exception as e:
            print(f"Error in get_director_analytics: {e}")
            return []

    def get_game_type_distribution(self, year_range=None, months=None, min_rating=None):
        """Get distribution of games by type with optional filters."""
        try:
            print(f"Fetching game type distribution.")
            collection = self.db.enriched_games
            pipeline = []

            # 1. Add field for extractedYear and month with proper error handling
            pipeline.append({
                '$addFields': {
                    'extractedYear': {
                        '$convert': {
                            'input': {'$arrayElemAt': [{'$split': [{'$ifNull': ['$Release_Date_IGDB', '']}, '/']}, 2]},
                            'to': 'int',
                            'onError': None,
                            'onNull': None
                        }
                    },
                    'extractedMonth': {
                        '$convert': {
                            'input': {'$arrayElemAt': [{'$split': [{'$ifNull': ['$Release_Date_IGDB', '']}, '/']}, 0]},
                            'to': 'int',
                            'onError': None,
                            'onNull': None
                        }
                    }
                }
            })

            # 2. Filter for valid data
            match_conditions = {
                'Game_Type': {'$exists': True, '$ne': None, '$ne': ''}
            }

            # Add month filter if provided
            if months:
                match_conditions['extractedMonth'] = {'$in': months, '$ne': None, '$type': 'number'}

            # Add rating filter if provided
            if min_rating:
                match_conditions['Rating'] = {'$gte': float(min_rating)}

            pipeline.append({'$match': match_conditions})

            # 3. Apply year range filter if provided
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

            # 4. Group by game type
            pipeline.append({
                '$group': {
                    '_id': '$Game_Type',
                    'count': {'$sum': 1}
                }
            })

            # 5. Sort by count descending
            pipeline.append({'$sort': {'count': -1}})

            # 6. Project for frontend
            pipeline.append({
                '$project': {
                    '_id': 0,
                    'game_type': '$_id',
                    'count': 1
                }
            })

            result = list(collection.aggregate(pipeline, allowDiskUse=True))
            print(f"Game type distribution result: {len(result)} types")
            return result

        except Exception as e:
            print(f"Error in get_game_type_distribution: {e}")
            return []

    def get_rating_distribution(self, year_range=None, months=None, min_rating=None):
        """Get distribution of games by rating ranges with optional filters."""
        try:
            print(f"Fetching rating distribution.")
            collection = self.db.enriched_games
            pipeline = []

            # 1. Add field for extractedYear and month with proper error handling
            pipeline.append({
                '$addFields': {
                    'extractedYear': {
                        '$convert': {
                            'input': {'$arrayElemAt': [{'$split': [{'$ifNull': ['$Release_Date_IGDB', '']}, '/']}, 2]},
                            'to': 'int',
                            'onError': None,
                            'onNull': None
                        }
                    },
                    'extractedMonth': {
                        '$convert': {
                            'input': {'$arrayElemAt': [{'$split': [{'$ifNull': ['$Release_Date_IGDB', '']}, '/']}, 0]},
                            'to': 'int',
                            'onError': None,
                            'onNull': None
                        }
                    }
                }
            })

            # 2. Filter for valid data
            match_conditions = {
                'Rating': {'$exists': True, '$ne': None, '$type': 'number'}
            }

            # Add month filter if provided
            if months:
                match_conditions['extractedMonth'] = {'$in': months, '$ne': None, '$type': 'number'}

            # Add rating filter if provided
            if min_rating:
                match_conditions['Rating'] = {'$gte': float(min_rating)}

            pipeline.append({'$match': match_conditions})

            # 3. Apply year range filter if provided
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

            # 4. Add rating range categorization
            pipeline.append({
                '$addFields': {
                    'rating_range': {
                        '$switch': {
                            'branches': [
                                {'case': {'$lt': ['$Rating', 3]}, 'then': 'Poor (0-3)'},
                                {'case': {'$lt': ['$Rating', 5]}, 'then': 'Below Average (3-5)'},
                                {'case': {'$lt': ['$Rating', 6.5]}, 'then': 'Average (5-6.5)'},
                                {'case': {'$lt': ['$Rating', 8]}, 'then': 'Good (6.5-8)'},
                                {'case': {'$lt': ['$Rating', 9]}, 'then': 'Great (8-9)'},
                                {'case': {'$gte': ['$Rating', 9]}, 'then': 'Excellent (9-10)'}
                            ],
                            'default': 'Unknown'
                        }
                    }
                }
            })

            # 5. Group by rating range
            pipeline.append({
                '$group': {
                    '_id': '$rating_range',
                    'count': {'$sum': 1},
                    'avg_rating': {'$avg': '$Rating'}
                }
            })

            # 6. Sort by average rating
            pipeline.append({'$sort': {'avg_rating': 1}})

            # 7. Project for frontend
            pipeline.append({
                '$project': {
                    '_id': 0,
                    'rating_range': '$_id',
                    'count': 1,
                    'avg_rating': {'$round': ['$avg_rating', 2]}
                }
            })

            result = list(collection.aggregate(pipeline, allowDiskUse=True))
            print(f"Rating distribution result: {len(result)} ranges")
            return result

        except Exception as e:
            print(f"Error in get_rating_distribution: {e}")
            return []

    def get_votes_analytics(self, year_range=None, months=None, min_rating=None):
        """Get voting analytics including total votes, average votes per game, etc. with optional filters."""
        try:
            print(f"Fetching votes analytics.")
            collection = self.db.enriched_games
            pipeline = []

            # 1. Add field for extractedYear and month with proper error handling
            pipeline.append({
                '$addFields': {
                    'extractedYear': {
                        '$convert': {
                            'input': {'$arrayElemAt': [{'$split': [{'$ifNull': ['$Release_Date_IGDB', '']}, '/']}, 2]},
                            'to': 'int',
                            'onError': None,
                            'onNull': None
                        }
                    },
                    'extractedMonth': {
                        '$convert': {
                            'input': {'$arrayElemAt': [{'$split': [{'$ifNull': ['$Release_Date_IGDB', '']}, '/']}, 0]},
                            'to': 'int',
                            'onError': None,
                            'onNull': None
                        }
                    }
                }
            })

            # 2. Filter for valid data
            match_conditions = {
                'Number_of_Votes': {'$exists': True, '$ne': None, '$type': 'number', '$gt': 0}
            }

            # Add month filter if provided
            if months:
                match_conditions['extractedMonth'] = {'$in': months, '$ne': None, '$type': 'number'}

            # Add rating filter if provided
            if min_rating:
                match_conditions['Rating'] = {'$gte': float(min_rating)}

            pipeline.append({'$match': match_conditions})

            # 3. Apply year range filter if provided
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

            # 4. Calculate analytics
            pipeline.append({
                '$group': {
                    '_id': None,
                    'total_votes': {'$sum': '$Number_of_Votes'},
                    'avg_votes_per_game': {'$avg': '$Number_of_Votes'},
                    'max_votes': {'$max': '$Number_of_Votes'},
                    'min_votes': {'$min': '$Number_of_Votes'},
                    'total_games_with_votes': {'$sum': 1}
                }
            })

            # 5. Project for frontend
            pipeline.append({
                '$project': {
                    '_id': 0,
                    'total_votes': 1,
                    'avg_votes_per_game': {'$round': ['$avg_votes_per_game', 0]},
                    'max_votes': 1,
                    'min_votes': 1,
                    'total_games_with_votes': 1
                }
            })

            result = list(collection.aggregate(pipeline, allowDiskUse=True))
            print(f"Votes analytics result: {result}")
            return result[0] if result else {}

        except Exception as e:
            print(f"Error in get_votes_analytics: {e}")
            return {}

    def get_most_voted_games(self, year_range=None, limit=10, months=None, min_rating=None):
        """Get games with the most votes with optional filters."""
        try:
            print(f"Fetching most voted games.")
            collection = self.db.enriched_games
            pipeline = []

            # 1. Add field for extractedYear and month with proper error handling
            pipeline.append({
                '$addFields': {
                    'extractedYear': {
                        '$convert': {
                            'input': {'$arrayElemAt': [{'$split': [{'$ifNull': ['$Release_Date_IGDB', '']}, '/']}, 2]},
                            'to': 'int',
                            'onError': None,
                            'onNull': None
                        }
                    },
                    'extractedMonth': {
                        '$convert': {
                            'input': {'$arrayElemAt': [{'$split': [{'$ifNull': ['$Release_Date_IGDB', '']}, '/']}, 0]},
                            'to': 'int',
                            'onError': None,
                            'onNull': None
                        }
                    }
                }
            })

            # 2. Filter for valid data
            match_conditions = {
                'Title': {'$exists': True, '$ne': None, '$ne': ''},
                'Number_of_Votes': {'$exists': True, '$ne': None, '$type': 'number', '$gt': 0},
                'Rating': {'$exists': True, '$ne': None, '$type': 'number'}
            }

            # Add month filter if provided
            if months:
                match_conditions['extractedMonth'] = {'$in': months, '$ne': None, '$type': 'number'}

            # Add rating filter if provided
            if min_rating:
                match_conditions['Rating'] = {'$gte': float(min_rating)}

            pipeline.append({'$match': match_conditions})

            # 3. Apply year range filter if provided
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

            # 4. Sort by votes descending
            pipeline.append({'$sort': {'Number_of_Votes': -1}})

            # 5. Limit results
            pipeline.append({'$limit': limit})

            # 6. Project for frontend
            pipeline.append({
                '$project': {
                    '_id': 0,
                    'name': '$Title',
                    'votes': '$Number_of_Votes',
                    'rating': {'$round': ['$Rating', 1]},
                    'genre': '$Genre',
                    'platform': '$Platform',
                    'publisher': '$Publisher'
                }
            })

            result = list(collection.aggregate(pipeline, allowDiskUse=True))
            print(f"Most voted games result: {len(result)} games")
            return result

        except Exception as e:
            print(f"Error in get_most_voted_games: {e}")
            return []

    def get_collection_summary(self):
        """Get summary statistics for all collections."""
        try:
            print(f"Fetching collection summary.")
            summary = {}
            
            collections = [
                'enriched_games', 'directors_mapping', 'platform_mapping', 
                'genre_mapping', 'game_type_mapping', 'genres_igdb_mapping', 
                'developer_mapping', 'publisher_mapping', 'game_mapping'
            ]
            
            for collection_name in collections:
                try:
                    count = self.db[collection_name].count_documents({})
                    summary[collection_name] = count
                except Exception as e:
                    print(f"Error counting {collection_name}: {e}")
                    summary[collection_name] = 0
            
            return summary
            
        except Exception as e:
            print(f"Error in get_collection_summary: {e}")
            return {}

    # === Operational Dashboard Queries ===
    
    def get_recent_releases(self, days=30, limit=20, months=None, min_rating=None, year_range=None):
        """Get recently released games within specified days, with optional month and rating filters."""
        try:
            print(f"Fetching recent releases within {days} days.")
            collection = self.db.enriched_games
            pipeline = []

            # 1. Add field for extractedYear and month with proper error handling
            pipeline.append({
                '$addFields': {
                    'extractedYear': {
                        '$convert': {
                            'input': {'$arrayElemAt': [{'$split': [{'$ifNull': ['$Release_Date_IGDB', '']}, '/']}, 2]},
                            'to': 'int',
                            'onError': None,
                            'onNull': None
                        }
                    },
                    'extractedMonth': {
                        '$convert': {
                            'input': {'$arrayElemAt': [{'$split': [{'$ifNull': ['$Release_Date_IGDB', '']}, '/']}, 0]},
                            'to': 'int',
                            'onError': None,
                            'onNull': None
                        }
                    },
                    'extractedDay': {
                        '$convert': {
                            'input': {'$arrayElemAt': [{'$split': [{'$ifNull': ['$Release_Date_IGDB', '']}, '/']}, 1]},
                            'to': 'int',
                            'onError': None,
                            'onNull': None
                        }
                    }
                }
            })

            # 2. Filter for releases based on year range or default to recent
            current_year = datetime.now().year
            match_conditions = {
                'Title': {'$exists': True, '$ne': None, '$ne': ''},
                'Rating': {'$exists': True, '$ne': None, '$type': 'number'}
            }

            # Use provided year_range if available, otherwise default to last 2 years
            if year_range and len(year_range) == 2:
                match_conditions['extractedYear'] = {
                    '$gte': year_range[0], 
                    '$lte': year_range[1], 
                    '$ne': None, 
                    '$type': 'number'
                }
                # When specific year range is provided, don't limit to 20 for counting purposes
                actual_limit = None  # Return all matching releases for accurate count
            else:
                match_conditions['extractedYear'] = {
                    '$gte': current_year - 2, 
                    '$lte': current_year, 
                    '$ne': None, 
                    '$type': 'number'
                }
                actual_limit = limit  # Use the provided limit for default recent releases

            # Add month filter if provided
            if months:
                match_conditions['extractedMonth'] = {'$in': months, '$ne': None, '$type': 'number'}

            # Add rating filter if provided
            if min_rating:
                match_conditions['Rating'] = {'$gte': float(min_rating)}

            pipeline.append({'$match': match_conditions})

            # 3. Sort by year and month descending
            pipeline.append({'$sort': {'extractedYear': -1, 'extractedMonth': -1}})

            # 4. Limit results only if we have an actual limit
            if actual_limit:
                pipeline.append({'$limit': actual_limit})

            # 5. Project for frontend
            pipeline.append({
                '$project': {
                    '_id': 0,
                    'name': '$Title',
                    'rating': {'$round': ['$Rating', 1]},
                    'genre': '$Genre',
                    'platform': '$Platform',
                    'publisher': '$Publisher',
                    'release_date': '$Release_Date_IGDB',
                    'votes': '$Number_of_Votes'
                }
            })

            result = list(collection.aggregate(pipeline, allowDiskUse=True))
            print(f"Recent releases result: {len(result)} games")
            return result

        except Exception as e:
            print(f"Error in get_recent_releases: {e}")
            return []

    def get_rating_trends_by_month(self, year_range=None, months=None):
        """Get average rating trends by month with optional month filter."""
        try:
            print(f"Fetching rating trends by month.")
            collection = self.db.enriched_games
            pipeline = []

            # 1. Add fields for date extraction with proper error handling
            pipeline.append({
                '$addFields': {
                    'extractedYear': {
                        '$convert': {
                            'input': {'$arrayElemAt': [{'$split': [{'$ifNull': ['$Release_Date_IGDB', '']}, '/']}, 2]},
                            'to': 'int',
                            'onError': None,
                            'onNull': None
                        }
                    },
                    'extractedMonth': {
                        '$convert': {
                            'input': {'$arrayElemAt': [{'$split': [{'$ifNull': ['$Release_Date_IGDB', '']}, '/']}, 0]},
                            'to': 'int',
                            'onError': None,
                            'onNull': None
                        }
                    }
                }
            })

            # 2. Filter for valid data
            match_conditions = {
                'extractedYear': {'$exists': True, '$ne': None, '$type': 'number'},
                'extractedMonth': {'$exists': True, '$ne': None, '$type': 'number', '$gte': 1, '$lte': 12},
                'Rating': {'$exists': True, '$ne': None, '$type': 'number'}
            }

            # Add month filter if provided
            if months:
                match_conditions['extractedMonth'] = {'$in': months}

            pipeline.append({'$match': match_conditions})

            # 3. Apply year range filter if provided
            if year_range and len(year_range) == 2:
                pipeline.append({
                    '$match': {
                        'extractedYear': {
                            '$gte': year_range[0],
                            '$lte': year_range[1]
                        }
                    }
                })

            # 4. Group by year and month
            pipeline.append({
                '$group': {
                    '_id': {
                        'year': '$extractedYear',
                        'month': '$extractedMonth'
                    },
                    'avg_rating': {'$avg': '$Rating'},
                    'game_count': {'$sum': 1}
                }
            })

            # 5. Sort by year and month
            pipeline.append({'$sort': {'_id.year': 1, '_id.month': 1}})

            # 6. Project for frontend
            pipeline.append({
                '$project': {
                    '_id': 0,
                    'year': '$_id.year',
                    'month': '$_id.month',
                    'avg_rating': {'$round': ['$avg_rating', 2]},
                    'game_count': 1,
                    'period': {
                        '$concat': [
                            {'$toString': '$_id.year'},
                            '-',
                            {'$cond': [
                                {'$lt': ['$_id.month', 10]},
                                {'$concat': ['0', {'$toString': '$_id.month'}]},
                                {'$toString': '$_id.month'}
                            ]}
                        ]
                    }
                }
            })

            result = list(collection.aggregate(pipeline, allowDiskUse=True))
            print(f"Rating trends result: {len(result)} periods")
            return result

        except Exception as e:
            print(f"Error in get_rating_trends_by_month: {e}")
            return []

    def get_monthly_release_activity(self, year_range=None, months=None):
        """Get monthly game release activity with optional month filter."""
        try:
            print(f"Fetching monthly release activity.")
            collection = self.db.enriched_games
            pipeline = []

            # 1. Add fields for date extraction with proper error handling
            pipeline.append({
                '$addFields': {
                    'extractedYear': {
                        '$convert': {
                            'input': {'$arrayElemAt': [{'$split': [{'$ifNull': ['$Release_Date_IGDB', '']}, '/']}, 2]},
                            'to': 'int',
                            'onError': None,
                            'onNull': None
                        }
                    },
                    'extractedMonth': {
                        '$convert': {
                            'input': {'$arrayElemAt': [{'$split': [{'$ifNull': ['$Release_Date_IGDB', '']}, '/']}, 0]},
                            'to': 'int',
                            'onError': None,
                            'onNull': None
                        }
                    }
                }
            })

            # 2. Filter for valid data
            match_conditions = {
                'extractedYear': {'$exists': True, '$ne': None, '$type': 'number'},
                'extractedMonth': {'$exists': True, '$ne': None, '$type': 'number', '$gte': 1, '$lte': 12},
                'Title': {'$exists': True, '$ne': None, '$ne': ''}
            }

            # Add month filter if provided
            if months:
                match_conditions['extractedMonth'] = {'$in': months}

            pipeline.append({'$match': match_conditions})

            # 3. Apply year range filter if provided
            if year_range and len(year_range) == 2:
                pipeline.append({
                    '$match': {
                        'extractedYear': {
                            '$gte': year_range[0],
                            '$lte': year_range[1]
                        }
                    }
                })

            # 4. Group by month (across all years)
            pipeline.append({
                '$group': {
                    '_id': '$extractedMonth',
                    'total_releases': {'$sum': 1},
                    'avg_rating': {'$avg': '$Rating'}
                }
            })

            # 5. Sort by month
            pipeline.append({'$sort': {'_id': 1}})

            # 6. Project for frontend
            pipeline.append({
                '$project': {
                    '_id': 0,
                    'month': '$_id',
                    'month_name': {
                        '$switch': {
                            'branches': [
                                {'case': {'$eq': ['$_id', 1]}, 'then': 'January'},
                                {'case': {'$eq': ['$_id', 2]}, 'then': 'February'},
                                {'case': {'$eq': ['$_id', 3]}, 'then': 'March'},
                                {'case': {'$eq': ['$_id', 4]}, 'then': 'April'},
                                {'case': {'$eq': ['$_id', 5]}, 'then': 'May'},
                                {'case': {'$eq': ['$_id', 6]}, 'then': 'June'},
                                {'case': {'$eq': ['$_id', 7]}, 'then': 'July'},
                                {'case': {'$eq': ['$_id', 8]}, 'then': 'August'},
                                {'case': {'$eq': ['$_id', 9]}, 'then': 'September'},
                                {'case': {'$eq': ['$_id', 10]}, 'then': 'October'},
                                {'case': {'$eq': ['$_id', 11]}, 'then': 'November'},
                                {'case': {'$eq': ['$_id', 12]}, 'then': 'December'}
                            ],
                            'default': 'Unknown'
                        }
                    },
                    'total_releases': 1,
                    'avg_rating': {'$round': ['$avg_rating', 2]}
                }
            })

            result = list(collection.aggregate(pipeline, allowDiskUse=True))
            print(f"Monthly activity result: {len(result)} months")
            return result

        except Exception as e:
            print(f"Error in get_monthly_release_activity: {e}")
            return []

    def get_platform_performance_metrics(self, year_range=None, months=None, min_rating=None):
        """Get comprehensive platform performance metrics with optional month and rating filters."""
        try:
            print(f"Fetching platform performance metrics.")
            collection = self.db.enriched_games
            pipeline = []

            # 1. Add fields for processing with proper error handling
            pipeline.append({
                '$addFields': {
                    'PlatformsArray': {'$split': [{'$ifNull': ['$Platform', '']}, ', ']},
                    'extractedYear': {
                        '$convert': {
                            'input': {'$arrayElemAt': [{'$split': [{'$ifNull': ['$Release_Date_IGDB', '']}, '/']}, 2]},
                            'to': 'int',
                            'onError': None,
                            'onNull': None
                        }
                    },
                    'extractedMonth': {
                        '$convert': {
                            'input': {'$arrayElemAt': [{'$split': [{'$ifNull': ['$Release_Date_IGDB', '']}, '/']}, 0]},
                            'to': 'int',
                            'onError': None,
                            'onNull': None
                        }
                    }
                }
            })

            # 2. Filter for valid data
            match_conditions = {
                'Platform': {'$exists': True, '$ne': None, '$ne': ''},
                'Rating': {'$exists': True, '$ne': None, '$type': 'number'}
            }

            # Add month filter if provided
            if months:
                match_conditions['extractedMonth'] = {'$in': months, '$ne': None, '$type': 'number'}

            # Add rating filter if provided
            if min_rating:
                match_conditions['Rating'] = {'$gte': float(min_rating)}

            pipeline.append({'$match': match_conditions})

            # 3. Apply year range filter if provided
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

            # 4. Unwind platforms
            pipeline.append({'$unwind': '$PlatformsArray'})

            # 5. Filter out empty platforms
            pipeline.append({'$match': {'PlatformsArray': {'$ne': '', '$exists': True, '$ne': None}}})

            # 6. Group by platform
            pipeline.append({
                '$group': {
                    '_id': '$PlatformsArray',
                    'total_games': {'$sum': 1},
                    'avg_rating': {'$avg': '$Rating'},
                    'total_votes': {'$sum': '$Number_of_Votes'},
                    'max_rating': {'$max': '$Rating'},
                    'min_rating': {'$min': '$Rating'}
                }
            })

            # 7. Filter out platforms with less than 5 games
            pipeline.append({'$match': {'total_games': {'$gte': 5}}})

            # 8. Sort by total games descending
            pipeline.append({'$sort': {'total_games': -1}})

            # 9. Project for frontend
            pipeline.append({
                '$project': {
                    '_id': 0,
                    'platform': '$_id',
                    'total_games': 1,
                    'avg_rating': {'$round': ['$avg_rating', 2]},
                    'total_votes': 1,
                    'max_rating': {'$round': ['$max_rating', 1]},
                    'min_rating': {'$round': ['$min_rating', 1]},
                    'rating_range': {
                        '$round': [{'$subtract': ['$max_rating', '$min_rating']}, 1]
                    }
                }
            })

            result = list(collection.aggregate(pipeline, allowDiskUse=True))
            print(f"Platform performance result: {len(result)} platforms")
            return result

        except Exception as e:
            print(f"Error in get_platform_performance_metrics: {e}")
            return []

    def get_top_rated_recent_games(self, year_range=None, limit=15, months=None, min_rating=None):
        """Get top rated games from specified years with optional month and rating filters."""
        try:
            print(f"Fetching top rated recent games.")
            collection = self.db.enriched_games
            pipeline = []

            # 1. Add field for extractedYear and month with proper error handling
            pipeline.append({
                '$addFields': {
                    'extractedYear': {
                        '$convert': {
                            'input': {'$arrayElemAt': [{'$split': [{'$ifNull': ['$Release_Date_IGDB', '']}, '/']}, 2]},
                            'to': 'int',
                            'onError': None,
                            'onNull': None
                        }
                    },
                    'extractedMonth': {
                        '$convert': {
                            'input': {'$arrayElemAt': [{'$split': [{'$ifNull': ['$Release_Date_IGDB', '']}, '/']}, 0]},
                            'to': 'int',
                            'onError': None,
                            'onNull': None
                        }
                    }
                }
            })

            # 2. Filter for valid data
            current_year = datetime.now().year
            match_conditions = {
                'Title': {'$exists': True, '$ne': None, '$ne': ''},
                'Rating': {'$exists': True, '$ne': None, '$type': 'number'},
                'Number_of_Votes': {'$exists': True, '$ne': None, '$type': 'number', '$gte': 5}
            }

            # If year_range is provided, use it; otherwise default to recent years
            if year_range and len(year_range) == 2:
                match_conditions['extractedYear'] = {
                    '$gte': year_range[0], 
                    '$lte': year_range[1], 
                    '$ne': None, 
                    '$type': 'number'
                }
                # Use a lower minimum rating when specific years are selected
                if not min_rating:
                    match_conditions['Rating']['$gte'] = 6.0
            else:
                # Default to recent years if no year range specified
                match_conditions['extractedYear'] = {
                    '$gte': current_year - 5, 
                    '$lte': current_year, 
                    '$ne': None, 
                    '$type': 'number'
                }
                # Use higher minimum rating for recent games
                if not min_rating:
                    match_conditions['Rating']['$gte'] = 7.0

            # Add month filter if provided
            if months:
                match_conditions['extractedMonth'] = {'$in': months, '$ne': None, '$type': 'number'}

            # Add rating filter if provided (this will override the default minimum)
            if min_rating:
                match_conditions['Rating'] = {'$gte': float(min_rating)}

            pipeline.append({'$match': match_conditions})

            # 3. Sort by rating and votes
            pipeline.append({'$sort': {'Rating': -1, 'Number_of_Votes': -1}})

            # 4. Limit results
            pipeline.append({'$limit': limit})

            # 5. Project for frontend
            pipeline.append({
                '$project': {
                    '_id': 0,
                    'name': '$Title',
                    'rating': {'$round': ['$Rating', 1]},
                    'votes': '$Number_of_Votes',
                    'genre': '$Genre',
                    'platform': '$Platform',
                    'publisher': '$Publisher',
                    'release_year': '$extractedYear'
                }
            })

            result = list(collection.aggregate(pipeline, allowDiskUse=True))
            print(f"Top rated recent games result: {len(result)} games")
            return result

        except Exception as e:
            print(f"Error in get_top_rated_recent_games: {e}")
            return []

    # === TACTICAL DASHBOARD METHODS ===
    
    def get_tactical_sankey_data(self, year_range=None, platforms=None, genres=None):
        """Get data for Sankey diagram: Genre → Platform → Publisher flow."""
        try:
            print(f"Fetching tactical Sankey data with filters - platforms: {platforms}, genres: {genres}")
            collection = self.db.enriched_games
            pipeline = []

            # Add year extraction
            pipeline.append({
                '$addFields': {
                    'extractedYear': {
                        '$convert': {
                            'input': {'$arrayElemAt': [{'$split': [{'$ifNull': ['$Release_Date_IGDB', '']}, '/']}, 2]},
                            'to': 'int',
                            'onError': None,
                            'onNull': None
                        }
                    }
                }
            })

            # Filter for valid data
            match_conditions = {
                'Genre': {'$exists': True, '$ne': None, '$ne': ''},
                'Platform': {'$exists': True, '$ne': None, '$ne': ''},
                'Publisher': {'$exists': True, '$ne': None, '$ne': ''}
            }

            # Apply platform filter
            if platforms:
                platform_regex = '|'.join([platform.replace('(', '\\(').replace(')', '\\)') for platform in platforms])
                match_conditions['Platform'] = {'$regex': platform_regex, '$options': 'i'}

            # Apply genre filter
            if genres:
                genre_regex = '|'.join([genre.replace('(', '\\(').replace(')', '\\)') for genre in genres])
                match_conditions['Genre'] = {'$regex': genre_regex, '$options': 'i'}

            pipeline.append({'$match': match_conditions})

            # Apply year range filter
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

            # Group by Genre → Platform → Publisher
            pipeline.append({
                '$group': {
                    '_id': {
                        'genre': '$Genre',
                        'platform': '$Platform',
                        'publisher': '$Publisher'
                    },
                    'count': {'$sum': 1}
                }
            })

            # Project for frontend with correct structure
            pipeline.append({
                '$project': {
                    '_id': 0,
                    'genre': '$_id.genre',
                    'platform': '$_id.platform',
                    'publisher': '$_id.publisher',
                    'count': '$count'
                }
            })

            # Sort by count descending
            pipeline.append({'$sort': {'count': -1}})

            result = list(collection.aggregate(pipeline, allowDiskUse=True))
            print(f"Tactical Sankey data result: {len(result)} flows")
            return result

        except Exception as e:
            print(f"Error in get_tactical_sankey_data: {e}")
            return []

    def get_tactical_venn_data(self, year_range=None, platforms=None):
        """Get data for Venn diagram: Games available across multiple platforms."""
        try:
            print(f"Fetching tactical Venn data with platform filter: {platforms}")
            collection = self.db.enriched_games
            pipeline = []

            # Add year extraction and platform array
            pipeline.append({
                '$addFields': {
                    'extractedYear': {
                        '$convert': {
                            'input': {'$arrayElemAt': [{'$split': [{'$ifNull': ['$Release_Date_IGDB', '']}, '/']}, 2]},
                            'to': 'int',
                            'onError': None,
                            'onNull': None
                        }
                    },
                    'PlatformsArray': {'$split': [{'$ifNull': ['$Platform', '']}, ', ']}
                }
            })

            # Filter for valid data
            match_conditions = {
                'Title': {'$exists': True, '$ne': None, '$ne': ''},
                'Platform': {'$exists': True, '$ne': None, '$ne': ''}
            }

            # Apply platform filter if specified
            if platforms:
                platform_regex = '|'.join([platform.replace('(', '\\(').replace(')', '\\)') for platform in platforms])
                match_conditions['Platform'] = {'$regex': platform_regex, '$options': 'i'}

            pipeline.append({'$match': match_conditions})

            # Apply year range filter
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

            # Add platform count
            pipeline.append({
                '$addFields': {
                    'platform_count': {'$size': '$PlatformsArray'}
                }
            })

            # Group by platform count
            pipeline.append({
                '$group': {
                    '_id': '$platform_count',
                    'game_count': {'$sum': 1},
                    'games': {'$push': '$Title'}
                }
            })

            # Project for frontend
            pipeline.append({
                '$project': {
                    '_id': 0,
                    'platform_count': '$_id',
                    'game_count': '$game_count',
                    'games': {'$slice': ['$games', 10]}  # Limit to 10 example games
                }
            })

            # Sort by platform count
            pipeline.append({'$sort': {'platform_count': 1}})

            result = list(collection.aggregate(pipeline, allowDiskUse=True))
            print(f"Tactical Venn data result: {len(result)} platform count groups")
            return result

        except Exception as e:
            print(f"Error in get_tactical_venn_data: {e}")
            return []

    def get_tactical_chord_data(self, year_range=None, genres=None):
        """Get data for Chord diagram: Developer ↔ Platform ↔ Genre connections."""
        try:
            print(f"Fetching tactical Chord data with genre filter: {genres}")
            collection = self.db.enriched_games
            pipeline = []

            # Add year extraction
            pipeline.append({
                '$addFields': {
                    'extractedYear': {
                        '$convert': {
                            'input': {'$arrayElemAt': [{'$split': [{'$ifNull': ['$Release_Date_IGDB', '']}, '/']}, 2]},
                            'to': 'int',
                            'onError': None,
                            'onNull': None
                        }
                    }
                }
            })

            # Filter for valid data
            match_conditions = {
                'Developer': {'$exists': True, '$ne': None, '$ne': ''},
                'Platform': {'$exists': True, '$ne': None, '$ne': ''},
                'Genre': {'$exists': True, '$ne': None, '$ne': ''}
            }

            # Apply genre filter
            if genres:
                genre_regex = '|'.join([genre.replace('(', '\\(').replace(')', '\\)') for genre in genres])
                match_conditions['Genre'] = {'$regex': genre_regex, '$options': 'i'}

            pipeline.append({'$match': match_conditions})

            # Apply year range filter
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

            # Group by Developer-Platform-Genre combinations
            pipeline.append({
                '$group': {
                    '_id': {
                        'developer': '$Developer',
                        'platform': '$Platform',
                        'genre': '$Genre'
                    },
                    'count': {'$sum': 1}
                }
            })

            # Project for chord diagram
            pipeline.append({
                '$project': {
                    '_id': 0,
                    'developer': '$_id.developer',
                    'platform': '$_id.platform',
                    'genre': '$_id.genre',
                    'count': '$count'
                }
            })

            # Sort by count descending
            pipeline.append({'$sort': {'count': -1}})

            result = list(collection.aggregate(pipeline, allowDiskUse=True))
            print(f"Tactical Chord data result: {len(result)} connections")
            return result

        except Exception as e:
            print(f"Error in get_tactical_chord_data: {e}")
            return []

    def get_tactical_dumbbell_data(self, year_range=None, platforms=None, genres=None):
        """Get data for Dumbbell chart: Min vs Max ratings across platforms for top genres."""
        try:
            print(f"Fetching tactical Dumbbell data with filters - platforms: {platforms}, genres: {genres}")
            collection = self.db.enriched_games
            pipeline = []

            # Add year extraction and platform array
            pipeline.append({
                '$addFields': {
                    'extractedYear': {
                        '$convert': {
                            'input': {'$arrayElemAt': [{'$split': [{'$ifNull': ['$Release_Date_IGDB', '']}, '/']}, 2]},
                            'to': 'int',
                            'onError': None,
                            'onNull': None
                        }
                    },
                    'PlatformsArray': {'$split': [{'$ifNull': ['$Platform', '']}, ', ']}
                }
            })

            # Filter for valid data
            match_conditions = {
                'Genre': {'$exists': True, '$ne': None, '$ne': ''},
                'Platform': {'$exists': True, '$ne': None, '$ne': ''},
                'Rating': {'$exists': True, '$ne': None, '$type': 'number'}
            }

            # Apply platform filter
            if platforms:
                platform_regex = '|'.join([platform.replace('(', '\\(').replace(')', '\\)') for platform in platforms])
                match_conditions['Platform'] = {'$regex': platform_regex, '$options': 'i'}

            # Apply genre filter
            if genres:
                genre_regex = '|'.join([genre.replace('(', '\\(').replace(')', '\\)') for genre in genres])
                match_conditions['Genre'] = {'$regex': genre_regex, '$options': 'i'}

            pipeline.append({'$match': match_conditions})

            # Apply year range filter
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

            # Unwind platforms
            pipeline.append({'$unwind': '$PlatformsArray'})

            # Group by Genre and Platform
            pipeline.append({
                '$group': {
                    '_id': {
                        'genre': '$Genre',
                        'platform': '$PlatformsArray'
                    },
                    'min_rating': {'$min': '$Rating'},
                    'max_rating': {'$max': '$Rating'},
                    'avg_rating': {'$avg': '$Rating'},
                    'count': {'$sum': 1}
                }
            })

            # Filter for platforms with at least 3 games
            pipeline.append({'$match': {'count': {'$gte': 3}}})

            # Project for dumbbell chart
            pipeline.append({
                '$project': {
                    '_id': 0,
                    'genre': '$_id.genre',
                    'platform': '$_id.platform',
                    'min_rating': {'$round': ['$min_rating', 1]},
                    'max_rating': {'$round': ['$max_rating', 1]},
                    'avg_rating': {'$round': ['$avg_rating', 1]},
                    'count': 1
                }
            })

            # Sort by genre and average rating
            pipeline.append({'$sort': {'genre': 1, 'avg_rating': -1}})

            result = list(collection.aggregate(pipeline, allowDiskUse=True))
            print(f"Tactical Dumbbell data result: {len(result)} genre-platform combinations")
            return result

        except Exception as e:
            print(f"Error in get_tactical_dumbbell_data: {e}")
            return []

    def get_tactical_marimekko_data(self, year_range=None, genres=None):
        """Get data for Marimekko chart: Relative genre share and platform share with market share calculation."""
        try:
            print(f"Fetching tactical Marimekko data with genre filter: {genres}")
            collection = self.db.enriched_games
            pipeline = []

            # Add year extraction and arrays
            pipeline.append({
                '$addFields': {
                    'extractedYear': {
                        '$convert': {
                            'input': {'$arrayElemAt': [{'$split': [{'$ifNull': ['$Release_Date_IGDB', '']}, '/']}, 2]},
                            'to': 'int',
                            'onError': None,
                            'onNull': None
                        }
                    },
                    'GenresArray': {'$split': [{'$ifNull': ['$Genre', '']}, ', ']},
                    'PlatformsArray': {'$split': [{'$ifNull': ['$Platform', '']}, ', ']}
                }
            })

            # Filter for valid data
            match_conditions = {
                'Genre': {'$exists': True, '$ne': None, '$ne': ''},
                'Platform': {'$exists': True, '$ne': None, '$ne': ''}
            }

            # Apply genre filter
            if genres:
                genre_regex = '|'.join([genre.replace('(', '\\(').replace(')', '\\)') for genre in genres])
                match_conditions['Genre'] = {'$regex': genre_regex, '$options': 'i'}

            pipeline.append({'$match': match_conditions})

            # Apply year range filter
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

            # Unwind both arrays
            pipeline.append({'$unwind': '$GenresArray'})
            pipeline.append({'$unwind': '$PlatformsArray'})

            # Group by Genre and Platform
            pipeline.append({
                '$group': {
                    '_id': {
                        'genre': '$GenresArray',
                        'platform': '$PlatformsArray'
                    },
                    'count': {'$sum': 1}
                }
            })

            # Calculate total for market share
            pipeline.append({
                '$group': {
                    '_id': None,
                    'total_count': {'$sum': '$count'},
                    'combinations': {
                        '$push': {
                            'genre': '$_id.genre',
                            'platform': '$_id.platform',
                            'count': '$count'
                        }
                    }
                }
            })

            # Unwind and calculate market share
            pipeline.append({'$unwind': '$combinations'})
            pipeline.append({
                '$project': {
                    '_id': 0,
                    'genre': '$combinations.genre',
                    'platform': '$combinations.platform',
                    'count': '$combinations.count',
                    'market_share': {
                        '$round': [
                            {'$multiply': [
                                {'$divide': ['$combinations.count', '$total_count']},
                                100
                            ]},
                            2
                        ]
                    }
                }
            })

            # Sort by market share descending
            pipeline.append({'$sort': {'market_share': -1}})

            result = list(collection.aggregate(pipeline, allowDiskUse=True))
            print(f"Tactical Marimekko data result: {len(result)} genre-platform combinations")
            return result

        except Exception as e:
            print(f"Error in get_tactical_marimekko_data: {e}")
            return []

    # === ANALYTICAL LIFECYCLE DASHBOARD METHODS ===
    
    def get_lifecycle_survival_data(self, year_range=None, genres=None, platforms=None, min_rating=None, min_votes=None):
        """Get survival curve data: % of games still getting votes N years after release."""
        try:
            print(f"Fetching lifecycle survival data.")
            collection = self.db.enriched_games
            pipeline = []

            # Add year extraction
            pipeline.append({
                '$addFields': {
                    'extractedYear': {
                        '$convert': {
                            'input': {'$arrayElemAt': [{'$split': [{'$ifNull': ['$Release_Date_IGDB', '']}, '/']}, 2]},
                            'to': 'int',
                            'onError': None,
                            'onNull': None
                        }
                    },
                    'currentYear': datetime.now().year
                }
            })

            # Filter for valid data
            match_conditions = {
                'extractedYear': {'$exists': True, '$ne': None, '$type': 'number'},
                'Number_of_Votes': {'$exists': True, '$ne': None, '$type': 'number', '$gt': 0}
            }

            if min_rating:
                match_conditions['Rating'] = {'$gte': min_rating}
            if min_votes:
                match_conditions['Number_of_Votes']['$gte'] = min_votes

            pipeline.append({'$match': match_conditions})

            # Apply filters
            if year_range and len(year_range) == 2:
                pipeline.append({
                    '$match': {
                        'extractedYear': {
                            '$gte': year_range[0],
                            '$lte': year_range[1]
                        }
                    }
                })

            # Calculate years since release
            pipeline.append({
                '$addFields': {
                    'yearsSinceRelease': {'$subtract': ['$currentYear', '$extractedYear']}
                }
            })

            # Group by years since release
            pipeline.append({
                '$group': {
                    '_id': '$yearsSinceRelease',
                    'games_with_votes': {'$sum': 1},
                    'total_votes': {'$sum': '$Number_of_Votes'},
                    'avg_rating': {'$avg': '$Rating'}
                }
            })

            # Sort by years since release
            pipeline.append({'$sort': {'_id': 1}})

            result = list(collection.aggregate(pipeline, allowDiskUse=True))
            print(f"Lifecycle survival data result: {len(result)} time periods")
            return result

        except Exception as e:
            print(f"Error in get_lifecycle_survival_data: {e}")
            return []

    def get_lifecycle_ridgeline_data(self, year_range=None, genres=None):
        """Get ridgeline plot data: Rating distribution across genres."""
        try:
            print(f"Fetching lifecycle ridgeline data.")
            collection = self.db.enriched_games
            pipeline = []

            # Add year extraction
            pipeline.append({
                '$addFields': {
                    'extractedYear': {
                        '$convert': {
                            'input': {'$arrayElemAt': [{'$split': [{'$ifNull': ['$Release_Date_IGDB', '']}, '/']}, 2]},
                            'to': 'int',
                            'onError': None,
                            'onNull': None
                        }
                    }
                }
            })

            # Filter for valid data
            match_conditions = {
                'Genre': {'$exists': True, '$ne': None, '$ne': ''},
                'Rating': {'$exists': True, '$ne': None, '$type': 'number'}
            }
            pipeline.append({'$match': match_conditions})

            # Apply filters
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

            # Project for ridgeline
            pipeline.append({
                '$project': {
                    '_id': 0,
                    'genre': '$Genre',
                    'rating': '$Rating',
                    'title': '$Title'
                }
            })

            result = list(collection.aggregate(pipeline, allowDiskUse=True))
            print(f"Lifecycle ridgeline data result: {len(result)} games")
            return result

        except Exception as e:
            print(f"Error in get_lifecycle_ridgeline_data: {e}")
            return []

    def get_lifecycle_timeline_data(self, year_range=None, min_votes=None):
        """Get timeline bubble chart data: Most voted games across release years."""
        try:
            print(f"Fetching lifecycle timeline data.")
            collection = self.db.enriched_games
            pipeline = []

            # Add year extraction
            pipeline.append({
                '$addFields': {
                    'extractedYear': {
                        '$convert': {
                            'input': {'$arrayElemAt': [{'$split': [{'$ifNull': ['$Release_Date_IGDB', '']}, '/']}, 2]},
                            'to': 'int',
                            'onError': None,
                            'onNull': None
                        }
                    }
                }
            })

            # Filter for valid data
            match_conditions = {
                'extractedYear': {'$exists': True, '$ne': None, '$type': 'number'},
                'Number_of_Votes': {'$exists': True, '$ne': None, '$type': 'number', '$gt': 0},
                'Rating': {'$exists': True, '$ne': None, '$type': 'number'},
                'Title': {'$exists': True, '$ne': None, '$ne': ''}
            }

            if min_votes:
                match_conditions['Number_of_Votes']['$gte'] = min_votes

            pipeline.append({'$match': match_conditions})

            # Apply year range filter
            if year_range and len(year_range) == 2:
                pipeline.append({
                    '$match': {
                        'extractedYear': {
                            '$gte': year_range[0],
                            '$lte': year_range[1]
                        }
                    }
                })

            # Sort by votes and limit to top games per year
            pipeline.append({'$sort': {'Number_of_Votes': -1}})

            # Project for timeline
            pipeline.append({
                '$project': {
                    '_id': 0,
                    'title': '$Title',
                    'year': '$extractedYear',
                    'rating': '$Rating',
                    'votes': '$Number_of_Votes',
                    'genre': '$Genre'
                }
            })

            result = list(collection.aggregate(pipeline, allowDiskUse=True))
            print(f"Lifecycle timeline data result: {len(result)} games")
            return result

        except Exception as e:
            print(f"Error in get_lifecycle_timeline_data: {e}")
            return []

    def get_lifecycle_hexbin_data(self, year_range=None, genres=None, platforms=None):
        """Get hexbin plot data: Cluster of games by Rating × Number_of_Votes."""
        try:
            print(f"Fetching lifecycle hexbin data.")
            collection = self.db.enriched_games
            pipeline = []

            # Add year extraction
            pipeline.append({
                '$addFields': {
                    'extractedYear': {
                        '$convert': {
                            'input': {'$arrayElemAt': [{'$split': [{'$ifNull': ['$Release_Date_IGDB', '']}, '/']}, 2]},
                            'to': 'int',
                            'onError': None,
                            'onNull': None
                        }
                    }
                }
            })

            # Filter for valid data
            match_conditions = {
                'Rating': {'$exists': True, '$ne': None, '$type': 'number'},
                'Number_of_Votes': {'$exists': True, '$ne': None, '$type': 'number', '$gt': 0}
            }
            pipeline.append({'$match': match_conditions})

            # Apply filters
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

            # Project for hexbin
            pipeline.append({
                '$project': {
                    '_id': 0,
                    'title': '$Title',
                    'rating': '$Rating',
                    'votes': '$Number_of_Votes',
                    'genre': '$Genre',
                    'year': '$extractedYear'
                }
            })

            result = list(collection.aggregate(pipeline, allowDiskUse=True))
            print(f"Lifecycle hexbin data result: {len(result)} games")
            return result

        except Exception as e:
            print(f"Error in get_lifecycle_hexbin_data: {e}")
            return []

    def get_lifecycle_parallel_data(self, year_range=None, genres=None):
        """Get parallel coordinates data: Compare genres across Rating, Votes, Platform Count."""
        try:
            print(f"Fetching lifecycle parallel data.")
            collection = self.db.enriched_games
            pipeline = []

            # Add year extraction and platform count
            pipeline.append({
                '$addFields': {
                    'extractedYear': {
                        '$convert': {
                            'input': {'$arrayElemAt': [{'$split': [{'$ifNull': ['$Release_Date_IGDB', '']}, '/']}, 2]},
                            'to': 'int',
                            'onError': None,
                            'onNull': None
                        }
                    },
                    'platform_count': {'$size': {'$split': [{'$ifNull': ['$Platform', '']}, ', ']}}
                }
            })

            # Filter for valid data
            match_conditions = {
                'Genre': {'$exists': True, '$ne': None, '$ne': ''},
                'Rating': {'$exists': True, '$ne': None, '$type': 'number'},
                'Number_of_Votes': {'$exists': True, '$ne': None, '$type': 'number'}
            }
            pipeline.append({'$match': match_conditions})

            # Apply filters
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

            # Group by genre
            pipeline.append({
                '$group': {
                    '_id': '$Genre',
                    'avg_rating': {'$avg': '$Rating'},
                    'avg_votes': {'$avg': '$Number_of_Votes'},
                    'avg_platform_count': {'$avg': '$platform_count'},
                    'game_count': {'$sum': 1},
                    'max_rating': {'$max': '$Rating'},
                    'min_rating': {'$min': '$Rating'}
                }
            })

            # Project for parallel coordinates
            pipeline.append({
                '$project': {
                    '_id': 0,
                    'genre': '$_id',
                    'avg_rating': {'$round': ['$avg_rating', 2]},
                    'avg_votes': {'$round': ['$avg_votes', 0]},
                    'avg_platform_count': {'$round': ['$avg_platform_count', 1]},
                    'game_count': 1,
                    'rating_range': {'$round': [{'$subtract': ['$max_rating', '$min_rating']}, 1]}
                }
            })

            result = list(collection.aggregate(pipeline, allowDiskUse=True))
            print(f"Lifecycle parallel data result: {len(result)} genres")
            return result

        except Exception as e:
            print(f"Error in get_lifecycle_parallel_data: {e}")
            return []

    def get_lifecycle_tree_data(self, year_range=None, genres=None):
        """Get tree diagram data: Genre → Subgenre → Platform expansion patterns."""
        try:
            print(f"Fetching evolution tree data.")
            collection = self.db.enriched_games
            pipeline = []

            # Add year extraction and arrays
            pipeline.append({
                '$addFields': {
                    'extractedYear': {
                        '$convert': {
                            'input': {'$arrayElemAt': [{'$split': [{'$ifNull': ['$Release_Date_IGDB', '']}, '/']}, 2]},
                            'to': 'int',
                            'onError': None,
                            'onNull': None
                        }
                    },
                    'GenresArray': {'$split': [{'$ifNull': ['$Genre', '']}, ', ']},
                    'PlatformsArray': {'$split': [{'$ifNull': ['$Platform', '']}, ', ']}
                }
            })

            # Filter for valid data
            match_conditions = {
                'Genre': {'$exists': True, '$ne': None, '$ne': ''},
                'Platform': {'$exists': True, '$ne': None, '$ne': ''}
            }
            pipeline.append({'$match': match_conditions})

            # Apply year range filter
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

            # Unwind arrays
            pipeline.append({'$unwind': '$GenresArray'})
            pipeline.append({'$unwind': '$PlatformsArray'})

            # Group by genre and platform
            pipeline.append({
                '$group': {
                    '_id': {
                        'genre': '$GenresArray',
                        'platform': '$PlatformsArray'
                    },
                    'count': {'$sum': 1}
                }
            })

            # Project for tree diagram
            pipeline.append({
                '$project': {
                    '_id': 0,
                    'parent': '$_id.genre',
                    'child': '$_id.platform',
                    'value': '$count'
                }
            })

            # Sort by count
            pipeline.append({'$sort': {'value': -1}})

            result = list(collection.aggregate(pipeline, allowDiskUse=True))
            print(f"Evolution tree data result: {len(result)} genre-platform relationships")
            return result

        except Exception as e:
            print(f"Error in get_evolution_tree_data: {e}")
            return []

    # === ANALYTICAL EVOLUTION DASHBOARD METHODS ===
    
    def get_evolution_stream_data(self, year_range=None, genres=None):
        """Get stream graph data: Genre popularity or rating trend over time."""
        try:
            print(f"Fetching evolution stream data.")
            collection = self.db.enriched_games
            pipeline = []

            # Add year extraction and genre array
            pipeline.append({
                '$addFields': {
                    'extractedYear': {
                        '$convert': {
                            'input': {'$arrayElemAt': [{'$split': [{'$ifNull': ['$Release_Date_IGDB', '']}, '/']}, 2]},
                            'to': 'int',
                            'onError': None,
                            'onNull': None
                        }
                    },
                    'GenresArray': {'$split': [{'$ifNull': ['$Genre', '']}, ', ']}
                }
            })

            # Filter for valid data
            match_conditions = {
                'extractedYear': {'$exists': True, '$ne': None, '$type': 'number'},
                'Genre': {'$exists': True, '$ne': None, '$ne': ''},
                'Rating': {'$exists': True, '$ne': None, '$type': 'number'}
            }
            pipeline.append({'$match': match_conditions})

            # Apply year range filter
            if year_range and len(year_range) == 2:
                pipeline.append({
                    '$match': {
                        'extractedYear': {
                            '$gte': year_range[0],
                            '$lte': year_range[1]
                        }
                    }
                })

            # Unwind genres
            pipeline.append({'$unwind': '$GenresArray'})

            # Group by year and genre
            pipeline.append({
                '$group': {
                    '_id': {
                        'year': '$extractedYear',
                        'genre': '$GenresArray'
                    },
                    'count': {'$sum': 1},
                    'avg_rating': {'$avg': '$Rating'}
                }
            })

            # Project for stream graph
            pipeline.append({
                '$project': {
                    '_id': 0,
                    'year': '$_id.year',
                    'genre': '$_id.genre',
                    'count': 1,
                    'avg_rating': {'$round': ['$avg_rating', 2]}
                }
            })

            # Sort by year and genre
            pipeline.append({'$sort': {'year': 1, 'genre': 1}})

            result = list(collection.aggregate(pipeline, allowDiskUse=True))
            print(f"Evolution stream data result: {len(result)} year-genre combinations")
            return result

        except Exception as e:
            print(f"Error in get_evolution_stream_data: {e}")
            return []

    def get_evolution_bubble_data(self, year_range=None, genres=None):
        """Get bubble timeline data: High-rated game launches over time by genre."""
        try:
            print(f"Fetching evolution bubble data.")
            collection = self.db.enriched_games
            pipeline = []

            # Add year extraction
            pipeline.append({
                '$addFields': {
                    'extractedYear': {
                        '$convert': {
                            'input': {'$arrayElemAt': [{'$split': [{'$ifNull': ['$Release_Date_IGDB', '']}, '/']}, 2]},
                            'to': 'int',
                            'onError': None,
                            'onNull': None
                        }
                    }
                }
            })

            # Filter for high-rated games
            match_conditions = {
                'extractedYear': {'$exists': True, '$ne': None, '$type': 'number'},
                'Genre': {'$exists': True, '$ne': None, '$ne': ''},
                'Rating': {'$exists': True, '$ne': None, '$type': 'number', '$gte': 7.0},
                'Number_of_Votes': {'$exists': True, '$ne': None, '$type': 'number', '$gt': 0},
                'Title': {'$exists': True, '$ne': None, '$ne': ''}
            }
            pipeline.append({'$match': match_conditions})

            # Apply year range filter
            if year_range and len(year_range) == 2:
                pipeline.append({
                    '$match': {
                        'extractedYear': {
                            '$gte': year_range[0],
                            '$lte': year_range[1]
                        }
                    }
                })

            # Project for bubble chart
            pipeline.append({
                '$project': {
                    '_id': 0,
                    'title': '$Title',
                    'year': '$extractedYear',
                    'genre': '$Genre',
                    'rating': '$Rating',
                    'votes': '$Number_of_Votes'
                }
            })

            # Sort by rating and votes
            pipeline.append({'$sort': {'rating': -1, 'votes': -1}})

            result = list(collection.aggregate(pipeline, allowDiskUse=True))
            print(f"Evolution bubble data result: {len(result)} high-rated games")
            return result

        except Exception as e:
            print(f"Error in get_evolution_bubble_data: {e}")
            return []

    def get_evolution_hexbin_data(self, year_range=None, genres=None):
        """Get hexbin data: Votes vs rating clusters."""
        try:
            print(f"Fetching evolution hexbin data.")
            collection = self.db.enriched_games
            pipeline = []

            # Add year extraction
            pipeline.append({
                '$addFields': {
                    'extractedYear': {
                        '$convert': {
                            'input': {'$arrayElemAt': [{'$split': [{'$ifNull': ['$Release_Date_IGDB', '']}, '/']}, 2]},
                            'to': 'int',
                            'onError': None,
                            'onNull': None
                        }
                    }
                }
            })

            # Filter for valid data
            match_conditions = {
                'Rating': {'$exists': True, '$ne': None, '$type': 'number'},
                'Number_of_Votes': {'$exists': True, '$ne': None, '$type': 'number', '$gt': 0},
                'Genre': {'$exists': True, '$ne': None, '$ne': ''}
            }
            pipeline.append({'$match': match_conditions})

            # Apply year range filter
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

            # Project for hexbin
            pipeline.append({
                '$project': {
                    '_id': 0,
                    'title': '$Title',
                    'rating': '$Rating',
                    'votes': '$Number_of_Votes',
                    'genre': '$Genre',
                    'year': '$extractedYear'
                }
            })

            result = list(collection.aggregate(pipeline, allowDiskUse=True))
            print(f"Evolution hexbin data result: {len(result)} games")
            return result

        except Exception as e:
            print(f"Error in get_evolution_hexbin_data: {e}")
            return []

    def get_evolution_parallel_data(self, year_range=None, genres=None):
        """Get parallel coordinates data: Compare multiple metrics across genres."""
        try:
            print(f"Fetching evolution parallel data.")
            collection = self.db.enriched_games
            pipeline = []

            # Add year extraction and platform count
            pipeline.append({
                '$addFields': {
                    'extractedYear': {
                        '$convert': {
                            'input': {'$arrayElemAt': [{'$split': [{'$ifNull': ['$Release_Date_IGDB', '']}, '/']}, 2]},
                            'to': 'int',
                            'onError': None,
                            'onNull': None
                        }
                    },
                    'platform_count': {'$size': {'$split': [{'$ifNull': ['$Platform', '']}, ', ']}}
                }
            })

            # Filter for valid data
            match_conditions = {
                'Genre': {'$exists': True, '$ne': None, '$ne': ''},
                'Rating': {'$exists': True, '$ne': None, '$type': 'number'},
                'Number_of_Votes': {'$exists': True, '$ne': None, '$type': 'number'}
            }
            pipeline.append({'$match': match_conditions})

            # Apply year range filter
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

            # Group by genre
            pipeline.append({
                '$group': {
                    '_id': '$Genre',
                    'avg_rating': {'$avg': '$Rating'},
                    'total_votes': {'$sum': '$Number_of_Votes'},
                    'avg_platform_reach': {'$avg': '$platform_count'},
                    'game_count': {'$sum': 1},
                    'rating_volatility': {'$stdDevPop': '$Rating'}
                }
            })

            # Project for parallel coordinates
            pipeline.append({
                '$project': {
                    '_id': 0,
                    'genre': '$_id',
                    'avg_rating': {'$round': ['$avg_rating', 2]},
                    'total_votes': 1,
                    'avg_platform_reach': {'$round': ['$avg_platform_reach', 1]},
                    'game_count': 1,
                    'rating_volatility': {'$round': [{'$ifNull': ['$rating_volatility', 0]}, 2]}
                }
            })

            # Sort by average rating
            pipeline.append({'$sort': {'avg_rating': -1}})

            result = list(collection.aggregate(pipeline, allowDiskUse=True))
            print(f"Evolution parallel data result: {len(result)} genres")
            return result

        except Exception as e:
            print(f"Error in get_evolution_parallel_data: {e}")
            return []

    def get_evolution_tree_data(self, year_range=None, genres=None):
        """Get tree diagram data: Genre → Subgenre → Platform expansion patterns."""
        try:
            print(f"Fetching evolution tree data.")
            collection = self.db.enriched_games
            pipeline = []

            # Add year extraction and arrays
            pipeline.append({
                '$addFields': {
                    'extractedYear': {
                        '$convert': {
                            'input': {'$arrayElemAt': [{'$split': [{'$ifNull': ['$Release_Date_IGDB', '']}, '/']}, 2]},
                            'to': 'int',
                            'onError': None,
                            'onNull': None
                        }
                    },
                    'GenresArray': {'$split': [{'$ifNull': ['$Genre', '']}, ', ']},
                    'PlatformsArray': {'$split': [{'$ifNull': ['$Platform', '']}, ', ']}
                }
            })

            # Filter for valid data
            match_conditions = {
                'Genre': {'$exists': True, '$ne': None, '$ne': ''},
                'Platform': {'$exists': True, '$ne': None, '$ne': ''}
            }
            pipeline.append({'$match': match_conditions})

            # Apply year range filter
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

            # Unwind arrays
            pipeline.append({'$unwind': '$GenresArray'})
            pipeline.append({'$unwind': '$PlatformsArray'})

            # Group by genre and platform
            pipeline.append({
                '$group': {
                    '_id': {
                        'genre': '$GenresArray',
                        'platform': '$PlatformsArray'
                    },
                    'count': {'$sum': 1}
                }
            })

            # Project for tree diagram
            pipeline.append({
                '$project': {
                    '_id': 0,
                    'parent': '$_id.genre',
                    'child': '$_id.platform',
                    'value': '$count'
                }
            })

            # Sort by count
            pipeline.append({'$sort': {'value': -1}})

            result = list(collection.aggregate(pipeline, allowDiskUse=True))
            print(f"Evolution tree data result: {len(result)} genre-platform relationships")
            return result

        except Exception as e:
            print(f"Error in get_evolution_tree_data: {e}")
            return []

    # === DEVELOPER PERFORMANCE METHODS ===
    
    def get_developer_studio_performance_data(self, year_range=None, studio_types=None, countries=None):
        """Get studio type performance analysis data."""
        try:
            print(f"Fetching developer studio performance data with filters - studio_types: {studio_types}, countries: {countries}")
            
            # Use the developer mapping collection
            developer_collection = self.db.developer_mapping
            games_collection = self.db.enriched_games
            
            # First get developer metadata
            developer_pipeline = []
            
            # Filter by studio type and country if specified
            match_conditions = {
                'Studio_Type': {'$exists': True, '$ne': None, '$ne': ''},
                'Replay_Rate': {'$exists': True, '$ne': None, '$type': 'number'}
            }
            
            if studio_types:
                match_conditions['Studio_Type'] = {'$in': studio_types}
            
            if countries:
                match_conditions['Country'] = {'$in': countries}
            
            developer_pipeline.append({'$match': match_conditions})
            
            # Group by studio type and calculate average replay rate
            developer_pipeline.append({
                '$group': {
                    '_id': '$Studio_Type',
                    'avg_replay_rate': {'$avg': '$Replay_Rate'},
                    'developer_count': {'$sum': 1},
                    'avg_years_active': {'$avg': '$Years_Active'}
                }
            })
            
            # Project for frontend
            developer_pipeline.append({
                '$project': {
                    '_id': 0,
                    'studio_type': '$_id',
                    'avg_replay_rate': {'$round': ['$avg_replay_rate', 3]},
                    'developer_count': 1,
                    'avg_years_active': {'$round': ['$avg_years_active', 1]}
                }
            })
            
            # Sort by average replay rate
            developer_pipeline.append({'$sort': {'avg_replay_rate': -1}})
            
            result = list(developer_collection.aggregate(developer_pipeline, allowDiskUse=True))
            print(f"Developer studio performance data result: {len(result)} studio types")
            return result
            
        except Exception as e:
            print(f"Error in get_developer_studio_performance_data: {e}")
            return []

    def get_developer_geographic_data(self, year_range=None, studio_types=None):
        """Get developer geographic distribution data."""
        try:
            print(f"Fetching developer geographic data with studio_types filter: {studio_types}")
            
            developer_collection = self.db.developer_mapping
            pipeline = []
            
            # Filter conditions
            match_conditions = {
                'Country': {'$exists': True, '$ne': None, '$ne': ''},
                'Studio_Type': {'$exists': True, '$ne': None, '$ne': ''}
            }
            
            if studio_types:
                match_conditions['Studio_Type'] = {'$in': studio_types}
            
            pipeline.append({'$match': match_conditions})
            
            # Group by country
            pipeline.append({
                '$group': {
                    '_id': '$Country',
                    'developer_count': {'$sum': 1},
                    'avg_replay_rate': {'$avg': '$Replay_Rate'},
                    'studio_types': {'$addToSet': '$Studio_Type'}
                }
            })
            
            # Project for frontend
            pipeline.append({
                '$project': {
                    '_id': 0,
                    'country': '$_id',
                    'developer_count': 1,
                    'avg_replay_rate': {'$round': ['$avg_replay_rate', 3]},
                    'studio_type_diversity': {'$size': '$studio_types'}
                }
            })
            
            # Sort by developer count
            pipeline.append({'$sort': {'developer_count': -1}})
            
            result = list(developer_collection.aggregate(pipeline, allowDiskUse=True))
            print(f"Developer geographic data result: {len(result)} countries")
            return result
            
        except Exception as e:
            print(f"Error in get_developer_geographic_data: {e}")
            return []

    def get_developer_maturity_data(self, year_range=None, maturity_levels=None):
        """Get developer maturity vs performance analysis."""
        try:
            print(f"Fetching developer maturity data with maturity_levels filter: {maturity_levels}")
            
            developer_collection = self.db.developer_mapping
            pipeline = []
            
            # Filter conditions
            match_conditions = {
                'Maturity_Level': {'$exists': True, '$ne': None, '$ne': ''},
                'Years_Active': {'$exists': True, '$ne': None, '$type': 'number'},
                'Replay_Rate': {'$exists': True, '$ne': None, '$type': 'number'}
            }
            
            if maturity_levels:
                match_conditions['Maturity_Level'] = {'$in': maturity_levels}
            
            pipeline.append({'$match': match_conditions})
            
            # Project individual developer data for analysis
            pipeline.append({
                '$project': {
                    '_id': 0,
                    'name': '$Name',
                    'maturity_level': '$Maturity_Level',
                    'years_active': '$Years_Active',
                    'replay_rate': '$Replay_Rate',
                    'studio_type': '$Studio_Type',
                    'country': '$Country'
                }
            })
            
            # Sort by years active
            pipeline.append({'$sort': {'years_active': -1}})
            
            # Limit to prevent overwhelming the chart
            pipeline.append({'$limit': 100})
            
            result = list(developer_collection.aggregate(pipeline, allowDiskUse=True))
            print(f"Developer maturity data result: {len(result)} developers")
            return result
            
        except Exception as e:
            print(f"Error in get_developer_maturity_data: {e}")
            return []

    def get_developer_replay_rate_data(self, year_range=None, studio_types=None, countries=None):
        """Get replay rate distribution by studio type."""
        try:
            print(f"Fetching developer replay rate data")
            
            developer_collection = self.db.developer_mapping
            pipeline = []
            
            # Filter conditions
            match_conditions = {
                'Studio_Type': {'$exists': True, '$ne': None, '$ne': ''},
                'Replay_Rate': {'$exists': True, '$ne': None, '$type': 'number'}
            }
            
            if studio_types:
                match_conditions['Studio_Type'] = {'$in': studio_types}
            
            if countries:
                match_conditions['Country'] = {'$in': countries}
            
            pipeline.append({'$match': match_conditions})
            
            # Group by studio type and calculate replay rate statistics
            pipeline.append({
                '$group': {
                    '_id': '$Studio_Type',
                    'min_replay_rate': {'$min': '$Replay_Rate'},
                    'max_replay_rate': {'$max': '$Replay_Rate'},
                    'avg_replay_rate': {'$avg': '$Replay_Rate'},
                    'median_replay_rate': {'$avg': '$Replay_Rate'},  # Approximation
                    'developer_count': {'$sum': 1}
                }
            })
            
            # Project for dumbbell chart
            pipeline.append({
                '$project': {
                    '_id': 0,
                    'studio_type': '$_id',
                    'min_replay_rate': {'$round': ['$min_replay_rate', 3]},
                    'max_replay_rate': {'$round': ['$max_replay_rate', 3]},
                    'avg_replay_rate': {'$round': ['$avg_replay_rate', 3]},
                    'developer_count': 1
                }
            })
            
            # Sort by average replay rate
            pipeline.append({'$sort': {'avg_replay_rate': -1}})
            
            result = list(developer_collection.aggregate(pipeline, allowDiskUse=True))
            print(f"Developer replay rate data result: {len(result)} studio types")
            return result
            
        except Exception as e:
            print(f"Error in get_developer_replay_rate_data: {e}")
            return []

    def get_developer_country_studio_matrix(self, year_range=None, countries=None):
        """Get country vs studio type matrix for heatmap."""
        try:
            print(f"Fetching developer country-studio matrix data")
            
            developer_collection = self.db.developer_mapping
            pipeline = []
            
            # Filter conditions
            match_conditions = {
                'Country': {'$exists': True, '$ne': None, '$ne': ''},
                'Studio_Type': {'$exists': True, '$ne': None, '$ne': ''}
            }
            
            if countries:
                match_conditions['Country'] = {'$in': countries}
            
            pipeline.append({'$match': match_conditions})
            
            # Group by country and studio type
            pipeline.append({
                '$group': {
                    '_id': {
                        'country': '$Country',
                        'studio_type': '$Studio_Type'
                    },
                    'developer_count': {'$sum': 1},
                    'avg_replay_rate': {'$avg': '$Replay_Rate'}
                }
            })
            
            # Project for heatmap
            pipeline.append({
                '$project': {
                    '_id': 0,
                    'country': '$_id.country',
                    'studio_type': '$_id.studio_type',
                    'developer_count': 1,
                    'avg_replay_rate': {'$round': ['$avg_replay_rate', 3]}
                }
            })
            
            # Sort by developer count
            pipeline.append({'$sort': {'developer_count': -1}})
            
            result = list(developer_collection.aggregate(pipeline, allowDiskUse=True))
            print(f"Developer country-studio matrix data result: {len(result)} combinations")
            return result
            
        except Exception as e:
            print(f"Error in get_developer_country_studio_matrix: {e}")
            return []


