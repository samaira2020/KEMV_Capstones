import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pymongo import MongoClient
from datetime import datetime

# === MongoDB Connection ===
@st.cache_resource
def get_mongo_connection():
    """Creates a cached connection to MongoDB."""
    try:
        client = MongoClient('mongodb://localhost:27017/')
        db = client['Capstones']
        collection = db['enriched_games']  # Using the enriched_games collection
        # Test connection
        collection.find_one()
        st.success(f"Connected to MongoDB: Capstones.enriched_games")
        return collection
    except Exception as e:
        st.error(f"Error connecting to MongoDB: {e}")
        return None

# === MongoDB Query Builder ===
def build_mongo_query(selected_genres=None, selected_platforms=None, selected_year_range=None):
    """Build MongoDB query based on selected filters."""
    query = {}
    
    if selected_genres:
        # Create regex pattern for genres (case-insensitive, word boundary)
        genre_pattern = '|'.join([f'\\b{genre}\\b' for genre in selected_genres])
        query['Genre'] = {'$regex': genre_pattern, '$options': 'i'}
    
    if selected_platforms:
        # Create regex pattern for platforms (case-insensitive, word boundary)
        platform_pattern = '|'.join([f'\\b{platform}\\b' for platform in selected_platforms])
        query['Platform'] = {'$regex': platform_pattern, '$options': 'i'}
    
    if selected_year_range:
        query['Release_Year_Extracted'] = {
            '$gte': selected_year_range[0], 
            '$lte': selected_year_range[1]
        }
    
    return query

# === MongoDB Analytics Functions ===
@st.cache_data
def get_total_games_count(collection, mongo_query):
    """Get total count of games matching the query."""
    try:
        return collection.count_documents(mongo_query)
    except Exception as e:
        st.error(f"Error getting total games count: {e}")
        return 0

@st.cache_data
def get_games_per_publisher(collection, mongo_query, limit=20):
    """Get games count per publisher using MongoDB aggregation."""
    try:
        pipeline = [
            {'$match': mongo_query},
            {'$addFields': {
                'publishers_array': {
                    '$split': [{'$ifNull': ['$Publisher', '']}, ',']
                }
            }},
            {'$unwind': '$publishers_array'},
            {'$addFields': {
                'publisher_clean': {'$trim': {'input': '$publishers_array'}}
            }},
            {'$match': {'publisher_clean': {'$ne': ''}}},
            {'$group': {
                '_id': '$publisher_clean',
                'count': {'$sum': 1}
            }},
            {'$sort': {'count': -1}},
            {'$limit': limit}
        ]
        return list(collection.aggregate(pipeline))
    except Exception as e:
        st.error(f"Error getting games per publisher: {e}")
        return []

@st.cache_data
def get_games_per_year(collection, mongo_query):
    """Get games count per year using MongoDB aggregation."""
    try:
        pipeline = [
            {'$match': {**mongo_query, 'Release_Year_Extracted': {'$ne': None}}},
            {'$group': {
                '_id': '$Release_Year_Extracted',
                'count': {'$sum': 1}
            }},
            {'$sort': {'_id': 1}}
        ]
        return list(collection.aggregate(pipeline))
    except Exception as e:
        st.error(f"Error getting games per year: {e}")
        return []

@st.cache_data
def get_top_rated_games(collection, mongo_query, limit=5):
    """Get top rated games using MongoDB aggregation."""
    try:
        pipeline = [
            {'$match': {**mongo_query, 'Rating': {'$ne': None, '$type': 'number'}}},
            {'$sort': {'Rating': -1}},
            {'$limit': limit},
            {'$project': {'Title': 1, 'Rating': 1, '_id': 0}}
        ]
        return list(collection.aggregate(pipeline))
    except Exception as e:
        st.error(f"Error getting top rated games: {e}")
        return []

@st.cache_data
def get_avg_rating_per_developer(collection, mongo_query, limit=20):
    """Get average rating per developer using MongoDB aggregation."""
    try:
        pipeline = [
            {'$match': {**mongo_query, 'Rating': {'$ne': None, '$type': 'number'}}},
            {'$addFields': {
                'developers_array': {
                    '$split': [{'$ifNull': ['$Developer', '']}, ',']
                }
            }},
            {'$unwind': '$developers_array'},
            {'$addFields': {
                'developer_clean': {'$trim': {'input': '$developers_array'}}
            }},
            {'$match': {'developer_clean': {'$ne': ''}}},
            {'$group': {
                '_id': '$developer_clean',
                'avg_rating': {'$avg': '$Rating'},
                'game_count': {'$sum': 1}
            }},
            {'$match': {'game_count': {'$gte': 2}}},  # Only developers with 2+ games
            {'$sort': {'avg_rating': -1}},
            {'$limit': limit}
        ]
        return list(collection.aggregate(pipeline))
    except Exception as e:
        st.error(f"Error getting average rating per developer: {e}")
        return []

@st.cache_data
def get_avg_rating_per_platform(collection, mongo_query, limit=10):
    """Get average rating per platform using MongoDB aggregation."""
    try:
        pipeline = [
            {'$match': {**mongo_query, 'Rating': {'$ne': None, '$type': 'number'}}},
            {'$addFields': {
                'platforms_array': {
                    '$split': [{'$ifNull': ['$Platform', '']}, ',']
                }
            }},
            {'$unwind': '$platforms_array'},
            {'$addFields': {
                'platform_clean': {'$trim': {'input': '$platforms_array'}}
            }},
            {'$match': {'platform_clean': {'$ne': ''}}},
            {'$group': {
                '_id': '$platform_clean',
                'avg_rating': {'$avg': '$Rating'},
                'game_count': {'$sum': 1}
            }},
            {'$match': {'game_count': {'$gte': 5}}},  # Only platforms with 5+ games
            {'$sort': {'avg_rating': -1}},
            {'$limit': limit}
        ]
        return list(collection.aggregate(pipeline))
    except Exception as e:
        st.error(f"Error getting average rating per platform: {e}")
        return []

@st.cache_data
def get_available_filters(collection):
    """Get available filter options from MongoDB."""
    try:
        # Get unique genres
        genre_pipeline = [
            {'$addFields': {
                'genres_array': {
                    '$split': [{'$ifNull': ['$Genre', '']}, ',']
                }
            }},
            {'$unwind': '$genres_array'},
            {'$addFields': {
                'genre_clean': {'$trim': {'input': '$genres_array'}}
            }},
            {'$match': {'genre_clean': {'$ne': ''}}},
            {'$group': {'_id': '$genre_clean'}},
            {'$sort': {'_id': 1}}
        ]
        genres = [doc['_id'] for doc in collection.aggregate(genre_pipeline)]
        
        # Get unique platforms
        platform_pipeline = [
            {'$addFields': {
                'platforms_array': {
                    '$split': [{'$ifNull': ['$Platform', '']}, ',']
                }
            }},
            {'$unwind': '$platforms_array'},
            {'$addFields': {
                'platform_clean': {'$trim': {'input': '$platforms_array'}}
            }},
            {'$match': {'platform_clean': {'$ne': ''}}},
            {'$group': {'_id': '$platform_clean'}},
            {'$sort': {'_id': 1}}
        ]
        platforms = [doc['_id'] for doc in collection.aggregate(platform_pipeline)]
        
        # Get year range
        year_pipeline = [
            {'$match': {'Release_Year_Extracted': {'$ne': None, '$type': 'number'}}},
            {'$group': {
                '_id': None,
                'min_year': {'$min': '$Release_Year_Extracted'},
                'max_year': {'$max': '$Release_Year_Extracted'}
            }}
        ]
        year_result = list(collection.aggregate(year_pipeline))
        if year_result:
            min_year = int(year_result[0]['min_year'])
            max_year = int(year_result[0]['max_year'])
        else:
            min_year, max_year = 1980, 2024
        
        return genres, platforms, min_year, max_year
    except Exception as e:
        st.error(f"Error getting available filters: {e}")
        return [], [], 1980, 2024

# === Main Streamlit App ===
def main():
    st.set_page_config(page_title="Studio Performance Overview", layout="wide")
    st.title('🎮 Studio Performance Overview')
    
    # Get MongoDB connection
    collection = get_mongo_connection()
    if collection is None:
        st.error("Failed to connect to MongoDB. Please ensure MongoDB is running and the database exists.")
        return
    
    # Get available filter options
    with st.spinner("Loading filter options..."):
        all_genres, all_platforms, min_year, max_year = get_available_filters(collection)
    
    # === Sidebar Filters ===
    st.sidebar.header("🔍 Filter Data")
    
    # Genre filter
    selected_genres = st.sidebar.multiselect(
        'Select Genre(s)', 
        all_genres,
        help="Select one or more genres to filter games"
    )
    
    # Platform filter
    selected_platforms = st.sidebar.multiselect(
        'Select Platform(s)', 
        all_platforms,
        help="Select one or more platforms to filter games"
    )
    
    # Year range filter
    selected_year_range = st.sidebar.slider(
        'Select Release Year Range', 
        min_year, max_year, (min_year, max_year),
        help="Select the range of release years"
    )
    
    # Build MongoDB query
    mongo_query = build_mongo_query(selected_genres, selected_platforms, selected_year_range)
    
    # Display current filters
    if selected_genres or selected_platforms or selected_year_range != (min_year, max_year):
        st.sidebar.markdown("### 📋 Active Filters:")
        if selected_genres:
            st.sidebar.write(f"**Genres:** {', '.join(selected_genres)}")
        if selected_platforms:
            st.sidebar.write(f"**Platforms:** {', '.join(selected_platforms)}")
        if selected_year_range != (min_year, max_year):
            st.sidebar.write(f"**Years:** {selected_year_range[0]} - {selected_year_range[1]}")
    
    # === Key Insights Section ===
    st.markdown("### 📊 Key Insights")
    
    # Get data for KPIs
    with st.spinner("Loading key insights..."):
        total_games = get_total_games_count(collection, mongo_query)
        games_per_pub = get_games_per_publisher(collection, mongo_query, limit=1)
        top_rated_games = get_top_rated_games(collection, mongo_query, limit=5)
    
    # KPI Row
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="🎯 Total Games",
            value=f"{total_games:,}",
            help="Total number of games matching current filters"
        )
    
    with col2:
        if games_per_pub:
            top_publisher = games_per_pub[0]['_id']
            top_publisher_count = games_per_pub[0]['count']
            st.metric(
                label="🏆 Top Publisher",
                value=top_publisher,
                delta=f"{top_publisher_count} games"
            )
        else:
            st.metric(label="🏆 Top Publisher", value="No data")
    
    with col3:
        if top_rated_games:
            highest_rated = top_rated_games[0]
            st.metric(
                label="⭐ Highest Rated Game",
                value=highest_rated['Title'][:30] + "..." if len(highest_rated['Title']) > 30 else highest_rated['Title'],
                delta=f"{highest_rated['Rating']:.1f} rating"
            )
        else:
            st.metric(label="⭐ Highest Rated Game", value="No data")
    
    # Top Rated Games List
    st.markdown("#### 🌟 Most Highly Rated Games")
    if top_rated_games:
        for i, game in enumerate(top_rated_games, 1):
            st.write(f"**{i}.** {game['Title']} - **{game['Rating']:.1f}** ⭐")
    else:
        st.info("No highly rated games found for the selected filters.")
    
    st.divider()
    
    # === Visualizations Section ===
    st.markdown("### 📈 Analytics Dashboard")
    
    # Row 1: Time Series and Publisher Distribution
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📅 Games Released Per Year")
        with st.spinner("Loading games per year..."):
            games_per_year = get_games_per_year(collection, mongo_query)
        
        if games_per_year:
            df_year = pd.DataFrame(games_per_year)
            df_year = df_year.rename(columns={'_id': 'Year', 'count': 'Games'})
            
            fig_year = px.line(
                df_year, x='Year', y='Games',
                title='Games Released Over Time',
                markers=True
            )
            fig_year.update_layout(
                xaxis_title="Release Year",
                yaxis_title="Number of Games",
                hovermode='x unified'
            )
            st.plotly_chart(fig_year, use_container_width=True)
        else:
            st.info("No release year data available for the selected filters.")
    
    with col2:
        st.markdown("#### 🏢 Game Share by Publisher")
        with st.spinner("Loading publisher data..."):
            games_per_pub_chart = get_games_per_publisher(collection, mongo_query, limit=10)
        
        if games_per_pub_chart:
            df_pub = pd.DataFrame(games_per_pub_chart)
            df_pub = df_pub.rename(columns={'_id': 'Publisher', 'count': 'Games'})
            
            fig_pub = px.pie(
                df_pub, values='Games', names='Publisher',
                title='Top 10 Publishers by Game Count'
            )
            fig_pub.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig_pub, use_container_width=True)
        else:
            st.info("No publisher data available for the selected filters.")
    
    st.divider()
    
    # Row 2: Publisher Bar Chart and Platform Ratings
    col3, col4 = st.columns(2)
    
    with col3:
        st.markdown("#### 📊 Top Publishers by Game Count")
        if games_per_pub_chart:
            df_pub_bar = pd.DataFrame(games_per_pub_chart[:15])  # Top 15 for bar chart
            df_pub_bar = df_pub_bar.rename(columns={'_id': 'Publisher', 'count': 'Games'})
            
            fig_pub_bar = px.bar(
                df_pub_bar, x='Games', y='Publisher',
                title='Top 15 Publishers',
                orientation='h'
            )
            fig_pub_bar.update_layout(
                yaxis={'categoryorder': 'total ascending'},
                xaxis_title="Number of Games",
                yaxis_title="Publisher"
            )
            st.plotly_chart(fig_pub_bar, use_container_width=True)
        else:
            st.info("No publisher data available for the selected filters.")
    
    with col4:
        st.markdown("#### 🎮 Average Rating by Platform")
        with st.spinner("Loading platform ratings..."):
            platform_ratings = get_avg_rating_per_platform(collection, mongo_query)
        
        if platform_ratings:
            df_platform = pd.DataFrame(platform_ratings)
            df_platform = df_platform.rename(columns={
                '_id': 'Platform', 
                'avg_rating': 'Average Rating',
                'game_count': 'Game Count'
            })
            
            fig_platform = px.bar(
                df_platform, x='Average Rating', y='Platform',
                title='Top Platforms by Average Rating (5+ games)',
                orientation='h',
                hover_data=['Game Count']
            )
            fig_platform.update_layout(
                yaxis={'categoryorder': 'total ascending'},
                xaxis_title="Average Rating",
                yaxis_title="Platform"
            )
            st.plotly_chart(fig_platform, use_container_width=True)
        else:
            st.info("No platform rating data available for the selected filters.")
    
    st.divider()
    
    # === Deep Dive Analysis ===
    st.markdown("### 🔍 Deep Dive Analysis")
    
    st.markdown("#### 👨‍💻 Average Rating Per Developer (Top 20)")
    with st.spinner("Loading developer analytics..."):
        dev_ratings = get_avg_rating_per_developer(collection, mongo_query)
    
    if dev_ratings:
        df_dev = pd.DataFrame(dev_ratings)
        df_dev = df_dev.rename(columns={
            '_id': 'Developer', 
            'avg_rating': 'Average Rating',
            'game_count': 'Game Count'
        })
        
        fig_dev = px.bar(
            df_dev, x='Average Rating', y='Developer',
            title='Top 20 Developers by Average Rating (2+ games)',
            orientation='h',
            hover_data=['Game Count'],
            color='Average Rating',
            color_continuous_scale='viridis'
        )
        fig_dev.update_layout(
            yaxis={'categoryorder': 'total ascending'},
            xaxis_title="Average Rating",
            yaxis_title="Developer",
            height=600
        )
        st.plotly_chart(fig_dev, use_container_width=True)
    else:
        st.info("No developer rating data available for the selected filters.")
    
    # === Data Explorer ===
    with st.expander("🔍 Data Explorer", expanded=False):
        st.markdown("#### Raw Data Sample")
        try:
            # Get a sample of filtered data
            sample_data = list(collection.find(mongo_query).limit(100))
            if sample_data:
                df_sample = pd.DataFrame(sample_data)
                # Remove MongoDB _id field for display
                if '_id' in df_sample.columns:
                    df_sample = df_sample.drop('_id', axis=1)
                st.dataframe(df_sample, use_container_width=True)
                st.info(f"Showing sample of {len(df_sample)} games from {total_games:,} total matching games.")
            else:
                st.info("No data available for the selected filters.")
        except Exception as e:
            st.error(f"Error loading sample data: {e}")

if __name__ == "__main__":
    main() 
    
    pipeline = [
    {'$addFields': {
        'genres_array': {'$split': [{'$ifNull': ['$Genre', '']}, ',']}
    }},
    {'$unwind': '$genres_array'},
    {'$addFields': {'genre_clean': {'$trim': {'input': '$genres_array'}}}},
    {'$match': {'genre_clean': {'$ne': ''}}},
    {'$group': {'_id': '$genre_clean'}},
    {'$sort': {'_id': 1}}
]


pipeline = [
    {'$match': {**mongo_query, 'Rating': {'$ne': None, '$type': 'number'}}},
    {'$addFields': {
        'developers_array': {'$split': [{'$ifNull': ['$Developer', '']}, ',']}
    }},
    {'$unwind': '$developers_array'},
    {'$addFields': {
        'developer_clean': {'$trim': {'input': '$developers_array'}}
    }},
    {'$match': {'developer_clean': {'$ne': ''}}},
    {'$group': {
        '_id': '$developer_clean',
        'avg_rating': {'$avg': '$Rating'},
        'game_count': {'$sum': 1}
    }},
    {'$match': {'game_count': {'$gte': 2}}},
    {'$sort': {'avg_rating': -1}},
    {'$limit': limit}
]
