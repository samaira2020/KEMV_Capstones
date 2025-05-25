from flask import Flask, render_template, request, jsonify
from db import MongoDBHandler
import pandas as pd
from datetime import datetime
import logging

app = Flask(__name__)

# Initialize MongoDB handler
db_handler = MongoDBHandler()

# Initialize logger
logger = logging.getLogger(__name__)

# === Flask Routes ===
@app.route('/')
def index():
    # We will ignore filter parameters for now to display all data
    # selected_genres = request.args.getlist('genre')
    # selected_platforms = request.args.getlist('platform')
    # year_start = request.args.get('year_start', type=int)
    # year_end = request.args.get('year_end', type=int)

    # year_range_filter = None
    # if year_start is not None and year_end is not None:
    #     year_range_filter = [year_start, year_end]

    stats = {}
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
        # Fetch filter options data first
        # Use get_mapping_data to get genres and platforms for the filters
        genre_mapping_data = db_handler.get_mapping_data('genre_mapping')
        all_genres = [item['Name'] for item in genre_mapping_data]

        platform_mapping_data = db_handler.get_mapping_data('platform_mapping')
        all_platforms = [item['Name'] for item in platform_mapping_data]

        # Determine min and max year based on data
        games_per_year_raw = list(db_handler.get_games_per_year_raw())
        valid_years = [item['extractedYear'] for item in games_per_year_raw if item.get('extractedYear') is not None and isinstance(item['extractedYear'], (int, float))]

        if valid_years:
            min_year_data = min(valid_years)
            max_year_data = max(valid_years)
        else:
            # Default or handle cases with no valid year data
            min_year_data = 1980  # Or another appropriate default
            max_year_data = 2023  # Or another appropriate default

        # Get selected genres, platforms, and year range from request or set defaults
        selected_genres = request.args.getlist('genre')
        selected_platforms = request.args.getlist('platform')
        year_start = request.args.get('year_start', type=int, default=min_year_data)
        year_end = request.args.get('year_end', type=int, default=max_year_data)
        year_range = [year_start, year_end]

        print(f"Selected Genres: {selected_genres}")
        print(f"Selected Platforms: {selected_platforms}")
        print(f"Selected Year Range: {year_range}")

        # Fetch dashboard data using the determined year range
        try:
            stats_raw = list(db_handler.get_game_statistics(year_range))
            if stats_raw:
                stats_data = stats_raw[0]
            else:
                stats_data = {'total_games': 0}
            print(f"Stats data after assignment: {stats_data} (type: {type(stats_data)})")
            print(f"Processed stats data before passing to template: {stats_data} (type: {type(stats_data)})")
        except Exception as e:
            print(f"Error fetching stats: {e}")
            stats_data = {}

        try:
            top_games = list(db_handler.get_top_rated_games(year_range))
        except Exception as e:
            print(f"Error fetching top games: {e}")
            top_games = []

        try:
            platform_counts = list(db_handler.get_games_count_by_platform(year_range))
        except Exception as e:
            print(f"Error fetching platform counts: {e}")
            platform_counts = []

        try:
            genre_counts = list(db_handler.get_games_count_by_genre(year_range))
        except Exception as e:
            print(f"Error fetching genre counts: {e}")
            genre_counts = []

        try:
            games_per_year = list(db_handler.get_games_per_year(year_range))
        except Exception as e:
            print(f"Error fetching games per year: {e}")
            games_per_year = []

        try:
            publisher_counts = list(db_handler.get_games_count_by_publisher(year_range))
        except Exception as e:
            print(f"Error fetching publisher counts: {e}")
            publisher_counts = []

        try:
            avg_rating_platform = list(db_handler.get_avg_rating_by_platform(year_range))
        except Exception as e:
            print(f"Error fetching average rating by platform: {e}")
            avg_rating_platform = []

        try:
            avg_rating_developer = list(db_handler.get_avg_rating_by_developer(year_range))
        except Exception as e:
            print(f"Error fetching average rating by developer: {e}")
            avg_rating_developer = []

        # Fetch a list of games for the new layout
        try:
            games_list = list(db_handler.get_games(limit=50)) # Fetching up to 50 games for now
        except Exception as e:
            print(f"Error fetching games list: {e}")
            games_list = []

        # Log the fetched data
        print("--- Dashboard Data Fetched (Detailed) ---")
        print(f"Stats: {stats_data} (type: {type(stats_data)})")
        print(f"Top Games: {top_games} (type: {type(top_games)})")
        print(f"Platform Counts: {platform_counts} (type: {type(platform_counts)})")
        print(f"Genre Counts: {genre_counts} (type: {type(genre_counts)})")
        print(f"Games Per Year: {games_per_year} (type: {type(games_per_year)})")
        print(f"Publisher Counts: {publisher_counts} (type: {type(publisher_counts)})")
        print(f"Avg Rating Platform: {avg_rating_platform} (type: {type(avg_rating_platform)})")
        print(f"Avg Rating Developer: {avg_rating_developer} (type: {type(avg_rating_developer)})")
        print(f"All Genres: {all_genres} (type: {type(all_genres)})")
        print(f"All Platforms: {all_platforms} (type: {type(all_platforms)})")
        print(f"Min Year: {min_year_data} (type: {type(min_year_data)})")
        print(f"Max Year: {max_year_data} (type: {type(max_year_data)})")
        print(f"Year Range: {year_range} (type: {type(year_range)})")
        print(f"Games List: {games_list} (type: {type(games_list)})")
        print("-----------------------------------------")

    except Exception as e:
        error = f"An error occurred: {e}"
        print(f"An error occurred: {e}")
        # Initialize empty data structures in case of error
        stats = {}
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
        max_year_data = 2023
        year_range = [min_year_data, max_year_data]
        games_list = [] # Initialize games_list in case of error
        stats_data = {} # Initialize stats_data in case of error

    return render_template('index.html', stats=stats_data, top_games=top_games, platform_counts=platform_counts, genre_counts=genre_counts, games_per_year=games_per_year, publisher_counts=publisher_counts, avg_rating_platform=avg_rating_platform, avg_rating_developer=avg_rating_developer, all_genres=all_genres, all_platforms=all_platforms, min_year=min_year_data, max_year=max_year_data, year_range=year_range, error=error, games_list=games_list)

@app.route('/search')
def search():
    # Example search parameters (you can modify these based on your needs)
    search_term = request.args.get('q', '')
    min_rating = request.args.get('min_rating')
    max_rating = request.args.get('max_rating')
    category = request.args.get('category', '')

    # Convert rating filters to float, handle potential errors
    try:
        min_rating = float(min_rating) if min_rating is not None else None
        max_rating = float(max_rating) if max_rating is not None else None
    except ValueError:
        min_rating = None
        max_rating = None

    results = []
    error = None

    try:
        results = db_handler.search_games(
            search_term=search_term,
            min_rating=min_rating,
            max_rating=max_rating,
            category=category,
        )
    except Exception as e:
        print(f"Error fetching data from MongoDB: {e}")
        error = str(e)

    return render_template('search.html', results=results, error=error)

# Endpoint to get filter options dynamically (optional, for more complex filtering)
@app.route('/filter_options')
def get_filter_options():
    try:
        genre_mapping_data = db_handler.get_mapping_data('genre_mapping')
        all_genres = [item['Name'] for item in genre_mapping_data]

        platform_mapping_data = db_handler.get_mapping_data('platform_mapping')
        all_platforms = [item['Name'] for item in platform_mapping_data]

        return jsonify({
            'genres': all_genres,
            'platforms': all_platforms
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # To run in debug mode:
    app.run(debug=True)
    # To run in production:
    # app.run() 