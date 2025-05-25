import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import os
import numpy as np
from collections import Counter
from pymongo import MongoClient

# Function to handle comma-separated strings and explode
def explode_split_column(df, column_name, id_column='Title'):
    if column_name not in df.columns:
        return pd.DataFrame(columns=[id_column, column_name])
    
    # Ensure the column is string type, replace NaN with empty string
    df[column_name] = df[column_name].fillna('').astype(str)
    
    # Split by comma, strip whitespace, and explode
    s = df[column_name].str.split(',').explode()
    
    # Create a new dataframe with the original ID and the split values
    exploded_df = pd.DataFrame({
        id_column: df[id_column].loc[s.index],
        column_name: s.values
    }).reset_index(drop=True)
    
    # Remove rows with empty strings resulting from splitting empty/NaN values
    exploded_df = exploded_df[exploded_df[column_name].str.strip() != '']
    
    return exploded_df

# === MongoDB Connection ===
def get_mongo_collection(database_name, collection_name):
    """Creates a connection to MongoDB and returns the specified collection."""
    try:
        # Connect to MongoDB
        client = MongoClient('mongodb://localhost:27017/') # Replace with your MongoDB connection string if different
        db = client[database_name]
        collection = db[collection_name]
        st.success(f"Connected to MongoDB: {database_name}.{collection_name}")
        return collection
    except Exception as e:
        st.error(f"Error connecting to MongoDB: {e}")
        return None

# === Load Data from MongoDB ===
@st.cache_data
def load_data_from_mongodb():
    """Loads the dataset from the MongoDB collection."""
    database_name = 'Capstones'
    collection_name = 'Capstone3' # Assuming your main game data is in this collection
    
    collection = get_mongo_collection(database_name, collection_name)
    if collection is None:
        return None
        
    try:
        # Fetch all documents from the collection
        # We convert to a list of dictionaries and then to a pandas DataFrame
        data = list(collection.find())
        df = pd.DataFrame(data)
        
        # --- Data Cleaning and Preparation (Adjust as needed for MongoDB data structure) ---
        # Ensure Rating column is numeric, coercing errors to NaN
        if 'Rating' in df.columns:
             df['Rating'] = pd.to_numeric(df['Rating'], errors='coerce')

        # Convert Release_Date_IGDB to datetime and extract year on load
        # Assuming Release_Date_IGDB is stored in a format pandas can parse (e.g., ISO 8601 string or datetime object)
        if 'Release_Date_IGDB' in df.columns:
            # Attempt to convert, handling potential errors
            df['Release_Date_IGDB'] = pd.to_datetime(df['Release_Date_IGDB'], errors='coerce')
            # Extract year, handling NaT results in NaN
            df['Release_Year_Extracted'] = df['Release_Date_IGDB'].dt.year
        else:
            st.warning("'Release_Date_IGDB' column not found in MongoDB data.")

        # Handle potential '_id' column from MongoDB if not needed for analysis
        if '_id' in df.columns:
            df = df.drop(columns=['_id'])
            
        return df
    except Exception as e:
        st.error(f"Error loading data from MongoDB: {e}")
        return None

# Load data from MongoDB
df = load_data_from_mongodb()

# === Streamlit App Title ===
st.title('Studio Performance Overview') # Changed main title

if df is not None:
    # === Sidebar Widgets (Context) ===
    st.sidebar.header("Filter Data")

    # Filter 1: Genre (Multiselect)
    all_genres = sorted(list(set(df['Genre'].dropna().str.split(',').explode().str.strip().unique()))) if 'Genre' in df.columns else []
    selected_genres = st.sidebar.multiselect('Select Genre(s)', all_genres)

    # Filter 2: Platform (Multiselect)
    all_platforms = sorted(list(set(df['Platform'].dropna().str.split(',').explode().str.strip().unique()))) if 'Platform' in df.columns else []
    selected_platforms = st.sidebar.multiselect('Select Platform(s)', all_platforms)

    # Filter 3: Release Year Range (Slider)
    release_years = df['Release_Year_Extracted'].dropna() if 'Release_Year_Extracted' in df.columns else pd.Series(dtype=int)
    # Ensure min/max year are valid integers; use fallbacks if Series is empty
    min_year = int(release_years.min()) if not release_years.empty and pd.notna(release_years.min()) else 1980
    max_year = int(release_years.max()) if not release_years.empty and pd.notna(release_years.max()) else 2024

    # Adjust slider range if min_year > max_year (can happen with empty data after filtering)
    if min_year > max_year:
        selected_year_range = st.sidebar.slider('Select Release Year Range', 1980, 2024, (1980, 2024))
    else:
        selected_year_range = st.sidebar.slider('Select Release Year Range', min_year, max_year, (min_year, max_year))

    # === Apply Filters ===
    # Start with the original dataframe and apply filters sequentially
    filtered_df = df.copy()

    if selected_genres:
        # Ensure index alignment by applying the filter to the dataframe directly
        # Use .fillna('') before splitting to maintain index alignment
        filtered_df = filtered_df[filtered_df['Genre'].fillna('').str.split(',').apply(lambda x: any(item.strip() in selected_genres for item in x))]

    if selected_platforms:
         # Ensure the column exists and is treated as string, fillna('') to maintain index alignment
         if 'Platform' in filtered_df.columns:
             # Create a boolean mask with the same index as filtered_df
             # Iterate through selected platforms and create a combined mask
             platform_filter_mask = pd.Series([False] * len(filtered_df), index=filtered_df.index) # Initialize with False
             for platform in selected_platforms:
                 # For each selected platform, check if it's in the comma-separated string
                 # Use .str.contains for substring matching, case-insensitive, and handle potential NaNs
                 # escape=False is used to treat platform names literally, not as regex
                 platform_filter_mask = platform_filter_mask | filtered_df['Platform'].fillna('').str.contains(platform, case=False, na=False, regex=False)

             # Apply the mask using .loc for explicit index alignment
             filtered_df = filtered_df.loc[platform_filter_mask]
         else:
             st.warning("'Platform' column not found in dataframe during filtering.")

    # Apply year filter if the column exists and filter is valid
    if 'Release_Year_Extracted' in filtered_df.columns and not release_years.empty:
         # Apply the filter directly to the dataframe
         # Ensure the year column is not NaN before comparing
         filtered_df = filtered_df[filtered_df['Release_Year_Extracted'].notna() & (filtered_df['Release_Year_Extracted'] >= selected_year_range[0]) & (filtered_df['Release_Year_Extracted'] <= selected_year_range[1])]

    # Re-calculate games per publisher on filtered data for KPIs and charts
    games_per_pub = pd.Series(dtype=int) # Initialize as empty Series with correct dtype
    if 'Publisher' in filtered_df.columns:
        pub_exploded_df = explode_split_column(filtered_df, 'Publisher', id_column='Title')
        if not pub_exploded_df.empty:
             games_per_pub = pub_exploded_df['Publisher'].value_counts()

    # === Main Content Area ===

    # --- Key Insights Section (Visually Grouped) ---
    with st.container(): # Wrap key insights in a container for potential visual grouping
        st.markdown("### Key Insights") # Use markdown for a slightly larger header

        # Add some space before the KPIs
        st.write("")

        # 2 Main Points (KPIs) - Side by Side
        kpi_col1, kpi_col2 = st.columns(2)

        with kpi_col1:
            st.subheader("Total Games")
            st.metric(label="Count", value=len(filtered_df))

        with kpi_col2:
            st.subheader("Top Publisher")
            if not games_per_pub.empty:
                top_publisher = games_per_pub.index[0]
                top_publisher_count = games_per_pub.iloc[0]
                st.metric(label="by Game Count", value=f"{top_publisher}", delta=f"{top_publisher_count} games")
            else:
                st.info("Publisher data not available.")

        # Add some space between KPIs and Highly Rated Games
        st.write("")

        # Add a list of Most Highly Rated Games (similar to example)
        st.subheader("Most Highly Rated Games")
        if 'Title' in filtered_df.columns and 'Rating' in filtered_df.columns:
            # Sort by rating and get top N, drop rows with NaN rating
            top_n_rated = 5
            top_rated_games = filtered_df.dropna(subset=['Rating']).sort_values(by='Rating', ascending=False).head(top_n_rated)

            if not top_rated_games.empty:
                for i, (index, row) in enumerate(top_rated_games.iterrows()):
                    st.write(f"NO.{i+1} {row['Title']} **{row['Rating']:.1f}**")
            else:
                st.info("No highly rated games found for the selected filters.")

    st.markdown("--- ") # Horizontal rule after Key Insights

    # === General Visualizations Section (Arranged in Columns) ===
    st.markdown("### General Visualizations") # Use markdown for a slightly larger header

    # Row 1 of Visualizations
    vis_col1, vis_col2 = st.columns(2)

    with vis_col1:
        # 1. Games Released Per Year
        st.subheader("Games Released Per Year")
        if 'Release_Year_Extracted' in filtered_df.columns:
            df_years_filtered = filtered_df.dropna(subset=['Release_Year_Extracted']).copy()
            df_years_filtered['Release_Year_Extracted'] = df_years_filtered['Release_Year_Extracted'].astype(int)

            if len(df_years_filtered) > 0:
                games_per_year = df_years_filtered['Release_Year_Extracted'].value_counts().sort_index()
                fig_year = px.line(games_per_year, x=games_per_year.index, y=games_per_year.values,
                                   labels={'x': 'Year', 'y': 'Number of Games'})
                st.plotly_chart(fig_year, use_container_width=True)
            else:
                st.info("No valid release date data available to plot games per year for the selected filters.")
        else:
            st.warning("'Release_Date_IGDB' column not found in dataset.")

    with vis_col2:
        # 4. Game Share by Publisher (Pie Chart)
        st.subheader("Game Share by Publisher")
        if not games_per_pub.empty:
             top_n_share = 10
             share_data = games_per_pub.head(top_n_share)

             if len(share_data) > 0:
                 fig_pub_share = px.pie(share_data, 
                                        values=share_data.values, 
                                        names=share_data.index,
                                        title='Game Share Distribution by Top 10 Publishers (Filtered)')
                 st.plotly_chart(fig_pub_share, use_container_width=True)
             else:
                  st.info("No publisher data available for share analysis with the selected filters.")
        else:
            st.warning("'Publisher' column not found in dataset.")

    st.markdown("--- ") # Horizontal rule between rows

    # Add vertical space between visualization rows
    st.write("")
    st.write("")

    # Row 2 of Visualizations
    vis_col3, vis_col4 = st.columns(2)

    with vis_col3:
         # 3. Top Publishers by Game Count (Bar Chart)
        st.subheader("Top Publishers by Game Count")
        if not games_per_pub.empty:
            top_n = 20
            publishers_to_display = games_per_pub.head(top_n)
            if len(publishers_to_display) > 0:
                fig_pub_count = px.bar(publishers_to_display, 
                                       x=publishers_to_display.index, 
                                       y=publishers_to_display.values,
                                       labels={'x': 'Publisher', 'y': 'Number of Games'})
                st.plotly_chart(fig_pub_count, use_container_width=True)
            else:
                 st.info("No publisher data available for analysis with the selected filters.")
        else:
            st.warning("'Publisher' column not found in dataset.")

    with vis_col4:
        # Average Rating by Platform Bar Chart
        st.subheader("Average Rating by Platform")
        if 'Platform' in filtered_df.columns and 'Rating' in filtered_df.columns:
             platform_exploded_df = explode_split_column(filtered_df, 'Platform', id_column='Title')
             if not platform_exploded_df.empty:
                 platform_rating_df = pd.merge(platform_exploded_df, filtered_df[['Title', 'Rating']], on='Title', how='left')
                 avg_rating_per_platform = platform_rating_df.dropna(subset=['Rating']).groupby('Platform')['Rating'].mean().sort_values(ascending=False)

                 top_n_platform = 10
                 platforms_to_display = avg_rating_per_platform.head(top_n_platform)
                 if len(platforms_to_display) > 0:
                     fig_platform_rating = px.bar(platforms_to_display,
                                                  x=platforms_to_display.index,
                                                  y=platforms_to_display.values,
                                                  labels={'x': 'Platform', 'y': 'Average Rating'})
                     st.plotly_chart(fig_platform_rating, use_container_width=True)
                 else:
                     st.info("No platform data or rating data available for analysis with the selected filters.")
             else:
                 st.info("No platform data available for analysis with the selected filters.")
        else:
             st.warning("'Platform' or 'Rating' column not found in dataset.")

    st.markdown("--- ") # Horizontal rule before Deep Dive Analysis

    # Add vertical space before Deep Dive Analysis
    st.write("")
    st.write("")

    # === Deep Dive Analysis Section ===
    st.markdown("### Deep Dive Analysis") # Use markdown for a slightly larger header

    # 2. Average Rating Per Developer (Bar Chart)
    st.subheader("Average Rating Per Developer (Top 20 - Filtered)")
    if 'Developer' in filtered_df.columns and 'Rating' in filtered_df.columns:
        dev_exploded_df = explode_split_column(filtered_df, 'Developer', id_column='Title')
        if not dev_exploded_df.empty:
            # Merge with the filtered_df to ensure index alignment and correct ratings
            dev_rating_df = pd.merge(dev_exploded_df, filtered_df[['Title', 'Rating']], on='Title', how='left')

            avg_rating_per_dev = dev_rating_df.dropna(subset=['Rating']).groupby('Developer')['Rating'].mean().sort_values(ascending=False)

            top_n = 20
            # Ensure there are enough developers to display top N
            developers_to_display = avg_rating_per_dev.head(top_n)
            if len(developers_to_display) > 0:
                fig_dev_rating = px.bar(developers_to_display, 
                                        x=developers_to_display.index, 
                                        y=developers_to_display.values,
                                        labels={'x': 'Developer', 'y': 'Average Rating'})
                st.plotly_chart(fig_dev_rating, use_container_width=True)
            else:
                st.info("No developer data or rating data available for analysis with the selected filters.")
        else:
            st.info("No developer data available for analysis with the selected filters.")
    else:
        st.warning("'Developer' or 'Rating' column not found in dataset.")

    # Filtered Data Table (for direct data exploration)
    st.subheader("Filtered Data Table")
    st.dataframe(filtered_df, use_container_width=True)

else:
    st.warning("Failed to load data. Please ensure 'filtered_enriched_video_game_dataset.csv' is in the correct directory.") 