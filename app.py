from flask import Flask, render_template, request, jsonify
from db import MongoDBHandler
import pandas as pd
from datetime import datetime
import logging
import json
from bson import ObjectId

app = Flask(__name__)

# Custom JSON encoder to handle MongoDB ObjectId and other types
class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        if hasattr(obj, 'isoformat'):  # datetime objects
            return obj.isoformat()
        return super().default(obj)

# Add custom filter for safe JSON serialization
def safe_tojson(obj):
    try:
        return json.dumps(obj, cls=CustomJSONEncoder)
    except (TypeError, ValueError) as e:
        logging.warning(f"JSON serialization error: {e}")
        return json.dumps({})

app.jinja_env.filters['safe_tojson'] = safe_tojson

# Initialize MongoDB handler
db_handler = MongoDBHandler()

# Initialize logger
logger = logging.getLogger(__name__)

# === Flask Routes ===
@app.route('/')
def index():
    # Determine which tab is active
    active_tab = request.args.get('tab', 'studio')
    
    # Map tab names to ensure consistency
    tab_mapping = {
        'studio': 'studio',
        'operational': 'operational', 
        'tactical': 'tactical',
        'cross-platform': 'tactical',  # Alternative name
        'analytical-lifecycle': 'analytical-lifecycle',
        'lifecycle': 'analytical-lifecycle',  # Alternative name
        'analytical-evolution': 'analytical-evolution',
        'evolution': 'analytical-evolution'  # Alternative name
    }
    
    active_tab = tab_mapping.get(active_tab, 'studio')
    
    # Debug: Print the active tab for troubleshooting
    print(f"Active tab detected: {active_tab}")
    print(f"Request args: {dict(request.args)}")

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
    min_year = 1980
    max_year = datetime.now().year
    year_range = [min_year, max_year]
    error = None

    # Operational dashboard variables
    recent_releases = []
    rating_trends = []
    monthly_activity = []
    platform_performance = []
    top_rated_recent = []

    # Tactical dashboard variables
    tactical_sankey_data = []
    tactical_venn_data = []
    tactical_chord_data = []
    tactical_dumbbell_data = []
    tactical_marimekko_data = []

    # Analytical Lifecycle dashboard variables
    lifecycle_survival_data = []
    lifecycle_ridgeline_data = []
    lifecycle_timeline_data = []
    lifecycle_hexbin_data = []
    lifecycle_parallel_data = []

    # Analytical Evolution dashboard variables
    evolution_stream_data = []
    evolution_bubble_data = []
    evolution_hexbin_data = []
    evolution_parallel_data = []
    evolution_tree_data = []

    try:
        # Fetch filter options data first
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
            min_year_data = 1980
            max_year_data = 2023

        if active_tab == 'studio':
            # === STUDIO PERFORMANCE TAB LOGIC ===
            selected_genres = request.args.getlist('genre')
            selected_platforms = request.args.getlist('platform')
            
            # Validate selected genres and platforms
            valid_genres = [genre for genre in selected_genres if genre in all_genres]
            valid_platforms = [platform for platform in selected_platforms if platform in all_platforms]
                
            year_start = request.args.get('year_start', type=int, default=min_year_data)
            year_end = request.args.get('year_end', type=int, default=max_year_data)
            
            if year_start > year_end:
                year_start, year_end = year_end, year_start
            
            year_range = [year_start, year_end]

            # Fetch studio performance data
            stats_data = db_handler.get_game_statistics(year_range)
            if not stats_data:
                stats_data = {'total_games': 0}

            top_games = list(db_handler.get_top_rated_games(year_range=year_range))
            platform_counts = list(db_handler.get_games_count_by_platform(year_range=year_range))
            genre_counts = list(db_handler.get_games_count_by_genre(year_range=year_range))
            games_per_year = list(db_handler.get_games_per_year(year_range=year_range))
            publisher_counts = list(db_handler.get_games_count_by_publisher(year_range=year_range))
            avg_rating_platform = list(db_handler.get_avg_rating_by_platform(year_range=year_range))
            avg_rating_developer = list(db_handler.get_avg_rating_by_developer(year_range=year_range))

        else:
            # === OPERATIONAL DASHBOARD TAB LOGIC ===
            selected_genres = []
            selected_platforms = []
            
            # Parse operational filters
            op_years = request.args.getlist('op_years')
            op_months = request.args.getlist('op_months')
            op_min_rating = request.args.get('op_min_rating')
            op_timeframe = request.args.get('op_timeframe', 'recent')
            
            # Convert to integers
            op_years = [int(year) for year in op_years if year.isdigit()]
            op_months = [int(month) for month in op_months if month.isdigit()]
            
            # Determine year range for operational dashboard
            if op_timeframe == 'recent':
                op_year_range = [max_year_data - 5, max_year_data]
            elif op_timeframe == 'last_decade':
                op_year_range = [max_year_data - 10, max_year_data]
            elif op_timeframe == 'custom' and op_years:
                op_year_range = [min(op_years), max(op_years)]
            elif op_timeframe == 'all':
                op_year_range = [min_year_data, max_year_data]
            else:
                # Default to recent if no timeframe specified
                op_year_range = [max_year_data - 5, max_year_data]
            
            # If custom is selected but no years provided, fall back to recent
            if op_timeframe == 'custom' and not op_years:
                print("Custom timeframe selected but no years provided, falling back to recent")
                op_year_range = [max_year_data - 5, max_year_data]
            
            year_range = op_year_range

            # Fetch basic stats for operational dashboard
            stats_data = db_handler.get_game_statistics(op_year_range)
            if not stats_data:
                stats_data = {'total_games': 0}

            print(f"Operational filters - Years: {op_years}, Months: {op_months}, Min Rating: {op_min_rating}, Timeframe: {op_timeframe}")
            print(f"Operational year range: {op_year_range}")
            print(f"Available year data range: {min_year_data} - {max_year_data}")

        # Initialize operational filter variables for use in data fetching
        if active_tab != 'operational':
            op_months = None
            op_min_rating = None

        # === ENHANCED ANALYTICS (for both tabs) ===
        try:
            if active_tab == 'operational':
                # Use operational filters for director analytics
                director_analytics = list(db_handler.get_director_analytics(
                    year_range=year_range,
                    months=op_months if op_months else None,
                    min_rating=op_min_rating if op_min_rating else None
                ))
            else:
                director_analytics = list(db_handler.get_director_analytics(year_range=year_range))
        except Exception as e:
            print(f"Error fetching director analytics: {e}")
            director_analytics = []

        try:
            if active_tab == 'operational':
                # Use operational filters for game type distribution
                game_type_distribution = list(db_handler.get_game_type_distribution(
                    year_range=year_range,
                    months=op_months if op_months else None,
                    min_rating=op_min_rating if op_min_rating else None
                ))
            else:
                game_type_distribution = list(db_handler.get_game_type_distribution(year_range=year_range))
        except Exception as e:
            print(f"Error fetching game type distribution: {e}")
            game_type_distribution = []

        try:
            if active_tab == 'operational':
                # Use operational filters for rating distribution
                rating_distribution = list(db_handler.get_rating_distribution(
                    year_range=year_range,
                    months=op_months if op_months else None,
                    min_rating=op_min_rating if op_min_rating else None
                ))
            else:
                rating_distribution = list(db_handler.get_rating_distribution(year_range=year_range))
        except Exception as e:
            print(f"Error fetching rating distribution: {e}")
            rating_distribution = []

        try:
            if active_tab == 'operational':
                # Use operational filters for votes analytics
                votes_analytics = db_handler.get_votes_analytics(
                    year_range=year_range,
                    months=op_months if op_months else None,
                    min_rating=op_min_rating if op_min_rating else None
                )
            else:
                votes_analytics = db_handler.get_votes_analytics(year_range=year_range)
        except Exception as e:
            print(f"Error fetching votes analytics: {e}")
            votes_analytics = {}

        try:
            if active_tab == 'operational':
                # Use operational filters for most voted games
                most_voted_games = list(db_handler.get_most_voted_games(
                    year_range=year_range,
                    months=op_months if op_months else None,
                    min_rating=op_min_rating if op_min_rating else None
                ))
            else:
                most_voted_games = list(db_handler.get_most_voted_games(year_range=year_range))
        except Exception as e:
            print(f"Error fetching most voted games: {e}")
            most_voted_games = []

        try:
            collection_summary = db_handler.get_collection_summary()
        except Exception as e:
            print(f"Error fetching collection summary: {e}")
            collection_summary = {}

        # === OPERATIONAL DASHBOARD DATA ===
        try:
            if active_tab == 'operational':
                # Use operational filters for recent releases
                recent_releases = list(db_handler.get_recent_releases(
                    limit=20, 
                    months=op_months if op_months else None,
                    min_rating=op_min_rating if op_min_rating else None,
                    year_range=year_range
                ))
            else:
                recent_releases = list(db_handler.get_recent_releases(limit=20))
        except Exception as e:
            print(f"Error fetching recent releases: {e}")
            recent_releases = []

        try:
            if active_tab == 'operational':
                # Use operational filters for rating trends
                rating_trends = list(db_handler.get_rating_trends_by_month(
                    year_range=year_range,
                    months=op_months if op_months else None
                ))
            else:
                rating_trends = list(db_handler.get_rating_trends_by_month(year_range=year_range))
        except Exception as e:
            print(f"Error fetching rating trends: {e}")
            rating_trends = []

        try:
            if active_tab == 'operational':
                # Use operational filters for monthly activity
                monthly_activity = list(db_handler.get_monthly_release_activity(
                    year_range=year_range,
                    months=op_months if op_months else None
                ))
            else:
                monthly_activity = list(db_handler.get_monthly_release_activity(year_range=year_range))
        except Exception as e:
            print(f"Error fetching monthly activity: {e}")
            monthly_activity = []

        try:
            if active_tab == 'operational':
                # Use operational filters for platform performance
                platform_performance = list(db_handler.get_platform_performance_metrics(
                    year_range=year_range,
                    months=op_months if op_months else None,
                    min_rating=op_min_rating if op_min_rating else None
                ))
            else:
                platform_performance = list(db_handler.get_platform_performance_metrics(year_range=year_range))
        except Exception as e:
            print(f"Error fetching platform performance: {e}")
            platform_performance = []

        try:
            if active_tab == 'operational':
                # Use operational filters for top rated recent games
                top_rated_recent = list(db_handler.get_top_rated_recent_games(
                    year_range=year_range, 
                    limit=15,
                    months=op_months if op_months else None,
                    min_rating=op_min_rating if op_min_rating else None
                ))
            else:
                top_rated_recent = list(db_handler.get_top_rated_recent_games(year_range=year_range, limit=15))
        except Exception as e:
            print(f"Error fetching top rated recent games: {e}")
            top_rated_recent = []

        # === TACTICAL DASHBOARD DATA ===
        try:
            # Parse tactical filters
            tactical_year_start = request.args.get('tactical_year_start', type=int)
            tactical_year_end = request.args.get('tactical_year_end', type=int)
            tactical_platforms = request.args.getlist('tactical_platforms')
            tactical_genres = request.args.getlist('tactical_genres')
            tactical_developer = request.args.get('tactical_developer', '')
            tactical_analysis = request.args.get('tactical_analysis', 'market_opportunity')
            
            # Use tactical year range if provided, otherwise use default
            tactical_year_range = year_range
            if tactical_year_start and tactical_year_end:
                tactical_year_range = [tactical_year_start, tactical_year_end]
            
            # Always fetch tactical dashboard data for availability
            tactical_sankey_data = list(db_handler.get_tactical_sankey_data(
                year_range=tactical_year_range, 
                platforms=tactical_platforms if tactical_platforms else None,
                genres=tactical_genres if tactical_genres else None
            ))
            tactical_venn_data = list(db_handler.get_tactical_venn_data(
                year_range=tactical_year_range,
                platforms=tactical_platforms if tactical_platforms else None
            ))
            tactical_chord_data = list(db_handler.get_tactical_chord_data(
                year_range=tactical_year_range,
                genres=tactical_genres if tactical_genres else None
            ))
            tactical_dumbbell_data = list(db_handler.get_tactical_dumbbell_data(
                year_range=tactical_year_range,
                platforms=tactical_platforms if tactical_platforms else None,
                genres=tactical_genres if tactical_genres else None
            ))
            tactical_marimekko_data = list(db_handler.get_tactical_marimekko_data(
                year_range=tactical_year_range,
                genres=tactical_genres if tactical_genres else None
            ))
            print(f"Tactical data fetched - Sankey: {len(tactical_sankey_data)}, Venn: {len(tactical_venn_data)}")
        except Exception as e:
            print(f"Error fetching tactical dashboard data: {e}")
            tactical_sankey_data = []
            tactical_venn_data = []
            tactical_chord_data = []
            tactical_dumbbell_data = []
            tactical_marimekko_data = []

        # === ANALYTICAL LIFECYCLE DASHBOARD DATA ===
        try:
            # Parse lifecycle filters
            search_term = request.args.get('search_term', '')
            lifecycle_genres = request.args.getlist('lifecycle_genres')
            lifecycle_platforms = request.args.getlist('lifecycle_platforms')
            min_rating = request.args.get('min_rating', type=float)
            min_votes = request.args.get('min_votes', type=int)
            game_type = request.args.get('game_type', '')
            
            # Always fetch lifecycle dashboard data for availability
            lifecycle_survival_data = list(db_handler.get_lifecycle_survival_data(
                year_range=year_range,
                genres=lifecycle_genres if lifecycle_genres else None,
                platforms=lifecycle_platforms if lifecycle_platforms else None,
                min_rating=min_rating,
                min_votes=min_votes
            ))
            lifecycle_ridgeline_data = list(db_handler.get_lifecycle_ridgeline_data(
                year_range=year_range,
                genres=lifecycle_genres if lifecycle_genres else None
            ))
            lifecycle_timeline_data = list(db_handler.get_lifecycle_timeline_data(
                year_range=year_range,
                min_votes=min_votes,
                search_term=search_term if search_term else None
            ))
            lifecycle_hexbin_data = list(db_handler.get_lifecycle_hexbin_data(
                year_range=year_range,
                genres=lifecycle_genres if lifecycle_genres else None,
                platforms=lifecycle_platforms if lifecycle_platforms else None
            ))
            lifecycle_parallel_data = list(db_handler.get_lifecycle_parallel_data(
                year_range=year_range,
                genres=lifecycle_genres if lifecycle_genres else None
            ))
            print(f"Lifecycle data fetched - Survival: {len(lifecycle_survival_data)}, Timeline: {len(lifecycle_timeline_data)}")
        except Exception as e:
            print(f"Error fetching lifecycle dashboard data: {e}")
            lifecycle_survival_data = []
            lifecycle_ridgeline_data = []
            lifecycle_timeline_data = []
            lifecycle_hexbin_data = []
            lifecycle_parallel_data = []

        # === ANALYTICAL EVOLUTION DASHBOARD DATA ===
        try:
            # Parse evolution filters
            evolution_genres = request.args.getlist('evolution_genres')
            evolution_platforms = request.args.getlist('evolution_platforms')
            evolution_period = request.args.get('evolution_period', 'all_time')
            evolution_metric = request.args.get('evolution_metric', 'rating_trends')
            
            # Adjust year range based on evolution period
            evolution_year_range = year_range
            if evolution_period == 'modern_era':
                evolution_year_range = [2000, max_year_data]
            elif evolution_period == 'recent_decade':
                evolution_year_range = [max_year_data - 10, max_year_data]
            
            # Always fetch evolution dashboard data for availability
            evolution_stream_data = list(db_handler.get_evolution_stream_data(
                year_range=evolution_year_range,
                genres=evolution_genres if evolution_genres else None
            ))
            evolution_bubble_data = list(db_handler.get_evolution_bubble_data(
                year_range=evolution_year_range,
                genres=evolution_genres if evolution_genres else None
            ))
            evolution_hexbin_data = list(db_handler.get_evolution_hexbin_data(
                year_range=evolution_year_range,
                genres=evolution_genres if evolution_genres else None
            ))
            evolution_parallel_data = list(db_handler.get_evolution_parallel_data(
                year_range=evolution_year_range,
                genres=evolution_genres if evolution_genres else None
            ))
            evolution_tree_data = list(db_handler.get_evolution_tree_data(
                year_range=evolution_year_range,
                genres=evolution_genres if evolution_genres else None
            ))
            print(f"Evolution data fetched - Stream: {len(evolution_stream_data)}, Bubble: {len(evolution_bubble_data)}")
        except Exception as e:
            print(f"Error fetching evolution dashboard data: {e}")
            evolution_stream_data = []
            evolution_bubble_data = []
            evolution_hexbin_data = []
            evolution_parallel_data = []
            evolution_tree_data = []

        print(f"Active Tab: {active_tab}")
        print(f"Year Range: {year_range}")
        print(f"Stats: {stats_data}")

    except Exception as e:
        error = f"An error occurred: {e}"
        print(f"An error occurred: {e}")
        # Initialize empty data structures in case of error
        stats_data = {'total_games': 0}
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
        selected_genres = []
        selected_platforms = []
        director_analytics = []
        game_type_distribution = []
        rating_distribution = []
        votes_analytics = {}
        most_voted_games = []
        collection_summary = {}
        recent_releases = []
        rating_trends = []
        monthly_activity = []
        platform_performance = []
        top_rated_recent = []
        tactical_sankey_data = []
        tactical_venn_data = []
        tactical_chord_data = []
        tactical_dumbbell_data = []
        tactical_marimekko_data = []
        lifecycle_survival_data = []
        lifecycle_ridgeline_data = []
        lifecycle_timeline_data = []
        lifecycle_hexbin_data = []
        lifecycle_parallel_data = []
        evolution_stream_data = []
        evolution_bubble_data = []
        evolution_hexbin_data = []
        evolution_parallel_data = []
        evolution_tree_data = []

    return render_template('index.html', 
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
                         selected_genres=selected_genres,
                         selected_platforms=selected_platforms,
                         active_tab=active_tab,
                         # Enhanced analytics data
                         director_analytics=director_analytics,
                         game_type_distribution=game_type_distribution,
                         rating_distribution=rating_distribution,
                         votes_analytics=votes_analytics,
                         most_voted_games=most_voted_games,
                         collection_summary=collection_summary,
                         # Operational dashboard data
                         recent_releases=recent_releases,
                         rating_trends=rating_trends,
                         monthly_activity=monthly_activity,
                         platform_performance=platform_performance,
                         top_rated_recent=top_rated_recent,
                         # Tactical dashboard data
                         tactical_sankey_data=tactical_sankey_data,
                         tactical_venn_data=tactical_venn_data,
                         tactical_chord_data=tactical_chord_data,
                         tactical_dumbbell_data=tactical_dumbbell_data,
                         tactical_marimekko_data=tactical_marimekko_data,
                         # Lifecycle dashboard data
                         lifecycle_survival_data=lifecycle_survival_data,
                         lifecycle_ridgeline_data=lifecycle_ridgeline_data,
                         lifecycle_timeline_data=lifecycle_timeline_data,
                         lifecycle_hexbin_data=lifecycle_hexbin_data,
                         lifecycle_parallel_data=lifecycle_parallel_data,
                         # Evolution dashboard data
                         evolution_stream_data=evolution_stream_data,
                         evolution_bubble_data=evolution_bubble_data,
                         evolution_hexbin_data=evolution_hexbin_data,
                         evolution_parallel_data=evolution_parallel_data,
                         evolution_tree_data=evolution_tree_data,
                         error=error)

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