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
        print(f"JSON serialization error: {e}")
        return json.dumps({})

app.jinja_env.filters['safe_tojson'] = safe_tojson

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize database handler
db_handler = MongoDBHandler()

@app.route('/')
def index():
    # Determine which tab is active
    active_tab = request.args.get('tab', 'studio')
    
    # Tab mapping for consistency
    tab_mapping = {
        'studio': 'studio',
        'operational': 'operational', 
        'tactical': 'tactical',
        'analytical-lifecycle': 'analytical-lifecycle',
        'analytical-evolution': 'analytical-evolution'
    }
    
    # Normalize tab name
    active_tab = tab_mapping.get(active_tab, 'studio')
    
    print(f"Active tab: {active_tab}")

    # Initialize all variables with default values
    stats_data = {'total_games': 0}
    top_games = []
    platform_counts = []
    genre_counts = []
    games_per_year = []
    publisher_counts = []
    avg_rating_platform = []
    avg_rating_developer = []
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

    # Initialize filter variables
    selected_genres = []
    selected_platforms = []

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

    # Initialize operational filter variables
    op_months = None
    op_min_rating = None
    
    # Initialize year_range with default values
    year_range = [1980, 2023]

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
            
        # Update default year_range with actual data
        year_range = [min_year_data, max_year_data]

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

            print(f"Studio filters - Genres: {selected_genres}, Platforms: {selected_platforms}, Year range: {year_range}")

            # Fetch studio performance data with filters
            stats_data = db_handler.get_game_statistics(year_range)
            if not stats_data:
                stats_data = {'total_games': 0}

            # Apply filters to data fetching
            top_games = list(db_handler.get_top_rated_games(
                year_range=year_range, 
                genres=valid_genres if valid_genres else None,
                platforms=valid_platforms if valid_platforms else None
            ))
            platform_counts = list(db_handler.get_games_count_by_platform(
                year_range=year_range,
                genres=valid_genres if valid_genres else None,
                platforms=valid_platforms if valid_platforms else None
            ))
            genre_counts = list(db_handler.get_games_count_by_genre(
                year_range=year_range,
                genres=valid_genres if valid_genres else None,
                platforms=valid_platforms if valid_platforms else None
            ))
            games_per_year = list(db_handler.get_games_per_year(
                year_range=year_range,
                genres=valid_genres if valid_genres else None,
                platforms=valid_platforms if valid_platforms else None
            ))
            publisher_counts = list(db_handler.get_games_count_by_publisher(
                year_range=year_range,
                genres=valid_genres if valid_genres else None,
                platforms=valid_platforms if valid_platforms else None
            ))
            avg_rating_platform = list(db_handler.get_avg_rating_by_platform(
                year_range=year_range,
                genres=valid_genres if valid_genres else None,
                platforms=valid_platforms if valid_platforms else None
            ))
            avg_rating_developer = list(db_handler.get_avg_rating_by_developer(
                year_range=year_range,
                genres=valid_genres if valid_genres else None,
                platforms=valid_platforms if valid_platforms else None
            ))

        elif active_tab == 'operational':
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

        else:
            # === OTHER DASHBOARD TABS (tactical, lifecycle, evolution) ===
            selected_genres = []
            selected_platforms = []
            
            # Use default year range for other tabs
            year_range = [min_year_data, max_year_data]
            
            # Fetch basic stats
            stats_data = db_handler.get_game_statistics(year_range)
            if not stats_data:
                stats_data = {'total_games': 0}

        # Initialize operational filter variables for use in data fetching
        if active_tab != 'operational':
            op_months = None
            op_min_rating = None

        # === ENHANCED ANALYTICS (for all tabs) ===
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
                    months=op_months if op_months else None,
                    min_rating=op_min_rating if op_min_rating else None
                ))
            else:
                top_rated_recent = list(db_handler.get_top_rated_recent_games(year_range=year_range))
        except Exception as e:
            print(f"Error fetching top rated recent games: {e}")
            top_rated_recent = []

        # === TACTICAL DASHBOARD DATA ===
        if active_tab == 'tactical':
            # Parse tactical filters for developer performance
            tactical_studio_types = request.args.getlist('tactical_studio_types')
            tactical_countries = request.args.getlist('tactical_countries')
            tactical_maturity = request.args.getlist('tactical_maturity')
            tactical_year_start = request.args.get('tactical_year_start', type=int, default=min_year_data)
            tactical_year_end = request.args.get('tactical_year_end', type=int, default=max_year_data)
            
            if tactical_year_start > tactical_year_end:
                tactical_year_start, tactical_year_end = tactical_year_end, tactical_year_start
            
            tactical_year_range = [tactical_year_start, tactical_year_end]
            
            print(f"Developer Performance filters - Studio Types: {tactical_studio_types}, Countries: {tactical_countries}, Maturity: {tactical_maturity}, Year range: {tactical_year_range}")

            try:
                # Studio Type Performance Analysis
                tactical_sankey_data = list(db_handler.get_developer_studio_performance_data(
                    year_range=tactical_year_range,
                    studio_types=tactical_studio_types if tactical_studio_types else None,
                    countries=tactical_countries if tactical_countries else None
                ))
            except Exception as e:
                print(f"Error fetching developer studio performance data: {e}")
                tactical_sankey_data = []

            try:
                # Geographic Distribution Analysis
                tactical_venn_data = list(db_handler.get_developer_geographic_data(
                    year_range=tactical_year_range,
                    studio_types=tactical_studio_types if tactical_studio_types else None
                ))
            except Exception as e:
                print(f"Error fetching developer geographic data: {e}")
                tactical_venn_data = []

            try:
                # Developer Maturity vs Performance
                tactical_chord_data = list(db_handler.get_developer_maturity_data(
                    year_range=tactical_year_range,
                    maturity_levels=tactical_maturity if tactical_maturity else None
                ))
            except Exception as e:
                print(f"Error fetching developer maturity data: {e}")
                tactical_chord_data = []

            try:
                # Replay Rate Distribution by Studio Type
                tactical_dumbbell_data = list(db_handler.get_developer_replay_rate_data(
                    year_range=tactical_year_range,
                    studio_types=tactical_studio_types if tactical_studio_types else None,
                    countries=tactical_countries if tactical_countries else None
                ))
            except Exception as e:
                print(f"Error fetching developer replay rate data: {e}")
                tactical_dumbbell_data = []

            try:
                # Country vs Studio Type Matrix
                tactical_marimekko_data = list(db_handler.get_developer_country_studio_matrix(
                    year_range=tactical_year_range,
                    countries=tactical_countries if tactical_countries else None
                ))
            except Exception as e:
                print(f"Error fetching developer country-studio matrix data: {e}")
                tactical_marimekko_data = []

            # Initialize Developer Performance KPIs with dynamic data extraction
            tactical_kpis = {
                'top_studio_type': {'name': 'Unknown', 'avg_replay_rate': 0.0},
                'most_productive_country': {'name': 'Unknown', 'developer_count': 0},
                'avg_developer_experience': {'years': 0.0, 'total_developers': 0}
            }

            # KPI 1: Top Performing Studio Type (highest average replay rate)
            try:
                # Get all studio performance data to calculate averages
                all_studio_data = list(db_handler.get_developer_studio_performance_data(
                    year_range=tactical_year_range,
                    studio_types=tactical_studio_types if tactical_studio_types else None,
                    countries=tactical_countries if tactical_countries else None
                ))
                
                if all_studio_data:
                    studio_performance = {}
                    for item in all_studio_data:
                        studio_type = item.get('studio_type', 'Unknown')
                        replay_rate = item.get('avg_replay_rate', 0)
                        developer_count = item.get('developer_count', 0)
                        
                        if studio_type not in studio_performance:
                            studio_performance[studio_type] = {'total_replay': 0, 'total_devs': 0}
                        
                        studio_performance[studio_type]['total_replay'] += replay_rate * developer_count
                        studio_performance[studio_type]['total_devs'] += developer_count
                    
                    # Calculate weighted average replay rate for each studio type
                    studio_averages = {}
                    for studio, data in studio_performance.items():
                        if data['total_devs'] > 0:
                            studio_averages[studio] = data['total_replay'] / data['total_devs']
                    
                    if studio_averages:
                        top_studio = max(studio_averages.items(), key=lambda x: x[1])
                        tactical_kpis['top_studio_type'] = {
                            'name': top_studio[0],
                            'avg_replay_rate': round(top_studio[1], 3)
                        }
            except Exception as e:
                print(f"Error calculating top studio type KPI: {e}")

            # KPI 2: Most Productive Country (highest developer count)
            try:
                # Get geographic data to find most productive country
                all_geographic_data = list(db_handler.get_developer_geographic_data(
                    year_range=tactical_year_range,
                    studio_types=tactical_studio_types if tactical_studio_types else None
                ))
                
                if all_geographic_data:
                    country_counts = {}
                    for item in all_geographic_data:
                        country = item.get('country', 'Unknown')
                        count = item.get('developer_count', 0)
                        country_counts[country] = country_counts.get(country, 0) + count
                    
                    if country_counts:
                        most_productive = max(country_counts.items(), key=lambda x: x[1])
                        tactical_kpis['most_productive_country'] = {
                            'name': most_productive[0],
                            'developer_count': most_productive[1]
                        }
            except Exception as e:
                print(f"Error calculating most productive country KPI: {e}")

            # KPI 3: Average Developer Experience (years active)
            try:
                # Get maturity data to calculate average experience
                all_maturity_data = list(db_handler.get_developer_maturity_data(
                    year_range=tactical_year_range,
                    maturity_levels=tactical_maturity if tactical_maturity else None
                ))
                
                if all_maturity_data:
                    total_years = 0
                    total_developers = 0
                    
                    for item in all_maturity_data:
                        years_active = item.get('years_active', 0)
                        # Each record represents one developer
                        total_years += years_active
                        total_developers += 1
                    
                    if total_developers > 0:
                        avg_years = total_years / total_developers
                        tactical_kpis['avg_developer_experience'] = {
                            'years': round(avg_years, 1),
                            'total_developers': total_developers
                        }
            except Exception as e:
                print(f"Error calculating average developer experience KPI: {e}")

        else:
            # Initialize empty data for non-tactical tabs
            tactical_sankey_data = []
            tactical_venn_data = []
            tactical_chord_data = []
            tactical_dumbbell_data = []
            tactical_marimekko_data = []
            tactical_kpis = {
                'top_studio_type': {'name': 'Unknown', 'avg_replay_rate': 0.0},
                'most_productive_country': {'name': 'Unknown', 'developer_count': 0},
                'avg_developer_experience': {'years': 0.0, 'total_developers': 0}
            }

        # === ANALYTICAL LIFECYCLE DASHBOARD DATA ===
        if active_tab == 'analytical-lifecycle':
            # Parse lifecycle filters
            lifecycle_search = request.args.get('lifecycle_search', '')
            lifecycle_genres = request.args.getlist('lifecycle_genres')
            lifecycle_platforms = request.args.getlist('lifecycle_platforms')
            lifecycle_min_rating = request.args.get('min_rating', type=float)
            lifecycle_min_votes = request.args.get('min_votes', type=int)
            lifecycle_year_start = request.args.get('lifecycle_year_start', type=int, default=min_year_data)
            lifecycle_year_end = request.args.get('lifecycle_year_end', type=int, default=max_year_data)
            
            if lifecycle_year_start > lifecycle_year_end:
                lifecycle_year_start, lifecycle_year_end = lifecycle_year_end, lifecycle_year_start
            
            lifecycle_year_range = [lifecycle_year_start, lifecycle_year_end]
            
            print(f"Lifecycle filters - Search: {lifecycle_search}, Genres: {lifecycle_genres}, Platforms: {lifecycle_platforms}")
            print(f"Lifecycle filters - Min Rating: {lifecycle_min_rating}, Min Votes: {lifecycle_min_votes}, Year range: {lifecycle_year_range}")

            try:
                lifecycle_survival_data = list(db_handler.get_lifecycle_survival_data(
                    year_range=lifecycle_year_range,
                    genres=lifecycle_genres if lifecycle_genres else None,
                    platforms=lifecycle_platforms if lifecycle_platforms else None,
                    min_rating=lifecycle_min_rating,
                    min_votes=lifecycle_min_votes
                ))
            except Exception as e:
                print(f"Error fetching lifecycle survival data: {e}")
                lifecycle_survival_data = []

            try:
                lifecycle_ridgeline_data = list(db_handler.get_lifecycle_ridgeline_data(
                    year_range=lifecycle_year_range,
                    genres=lifecycle_genres if lifecycle_genres else None
                ))
            except Exception as e:
                print(f"Error fetching lifecycle ridgeline data: {e}")
                lifecycle_ridgeline_data = []

            try:
                lifecycle_timeline_data = list(db_handler.get_lifecycle_timeline_data(
                    year_range=lifecycle_year_range,
                    min_votes=lifecycle_min_votes
                ))
            except Exception as e:
                print(f"Error fetching lifecycle timeline data: {e}")
                lifecycle_timeline_data = []

            try:
                lifecycle_hexbin_data = list(db_handler.get_lifecycle_hexbin_data(
                    year_range=lifecycle_year_range,
                    genres=lifecycle_genres if lifecycle_genres else None,
                    platforms=lifecycle_platforms if lifecycle_platforms else None
                ))
            except Exception as e:
                print(f"Error fetching lifecycle hexbin data: {e}")
                lifecycle_hexbin_data = []

            try:
                lifecycle_parallel_data = list(db_handler.get_lifecycle_parallel_data(
                    year_range=lifecycle_year_range,
                    genres=lifecycle_genres if lifecycle_genres else None
                ))
            except Exception as e:
                print(f"Error fetching lifecycle parallel data: {e}")
                lifecycle_parallel_data = []

        # === ANALYTICAL EVOLUTION DASHBOARD DATA ===
        if active_tab == 'analytical-evolution':
            # Parse evolution filters
            evolution_genres = request.args.getlist('evolution_genres')
            evolution_platforms = request.args.getlist('evolution_platforms')
            evolution_year_start = request.args.get('evolution_year_start', type=int, default=min_year_data)
            evolution_year_end = request.args.get('evolution_year_end', type=int, default=max_year_data)
            
            if evolution_year_start > evolution_year_end:
                evolution_year_start, evolution_year_end = evolution_year_end, evolution_year_start
            
            evolution_year_range = [evolution_year_start, evolution_year_end]
            
            print(f"Evolution filters - Genres: {evolution_genres}, Platforms: {evolution_platforms}, Year range: {evolution_year_range}")

            try:
                evolution_stream_data = list(db_handler.get_evolution_stream_data(
                    year_range=evolution_year_range,
                    genres=evolution_genres if evolution_genres else None
                ))
            except Exception as e:
                print(f"Error fetching evolution stream data: {e}")
                evolution_stream_data = []

            try:
                evolution_bubble_data = list(db_handler.get_evolution_bubble_data(
                    year_range=evolution_year_range,
                    genres=evolution_genres if evolution_genres else None
                ))
            except Exception as e:
                print(f"Error fetching evolution bubble data: {e}")
                evolution_bubble_data = []

            try:
                evolution_hexbin_data = list(db_handler.get_evolution_hexbin_data(
                    year_range=evolution_year_range,
                    genres=evolution_genres if evolution_genres else None
                ))
            except Exception as e:
                print(f"Error fetching evolution hexbin data: {e}")
                evolution_hexbin_data = []

            try:
                evolution_parallel_data = list(db_handler.get_evolution_parallel_data(
                    year_range=evolution_year_range,
                    genres=evolution_genres if evolution_genres else None
                ))
            except Exception as e:
                print(f"Error fetching evolution parallel data: {e}")
                evolution_parallel_data = []

            try:
                evolution_tree_data = list(db_handler.get_evolution_tree_data(
                    year_range=evolution_year_range,
                    genres=evolution_genres if evolution_genres else None
                ))
            except Exception as e:
                print(f"Error fetching evolution tree data: {e}")
                evolution_tree_data = []

    except Exception as e:
        print(f"Error in main data fetching: {e}")
        # Set default values for all variables in case of error
        stats_data = {'total_games': 0}
        all_genres = []
        all_platforms = []
        min_year_data = 1980
        max_year_data = 2023
        selected_genres = []
        selected_platforms = []

    # Render the template with all data
    return render_template('index.html', 
                         active_tab=active_tab,
                         stats=stats_data, 
                         top_games=top_games, 
                         platform_counts=platform_counts, 
                         genre_counts=genre_counts, 
                         games_per_year=games_per_year, 
                         publisher_counts=publisher_counts, 
                         avg_rating_platform=avg_rating_platform, 
                         avg_rating_developer=avg_rating_developer, 
                         director_analytics=director_analytics,
                         game_type_distribution=game_type_distribution,
                         rating_distribution=rating_distribution,
                         votes_analytics=votes_analytics,
                         most_voted_games=most_voted_games,
                         collection_summary=collection_summary,
                         recent_releases=recent_releases,
                         rating_trends=rating_trends,
                         monthly_activity=monthly_activity,
                         platform_performance=platform_performance,
                         top_rated_recent=top_rated_recent,
                         tactical_sankey_data=tactical_sankey_data,
                         tactical_venn_data=tactical_venn_data,
                         tactical_chord_data=tactical_chord_data,
                         tactical_dumbbell_data=tactical_dumbbell_data,
                         tactical_marimekko_data=tactical_marimekko_data,
                         lifecycle_survival_data=lifecycle_survival_data,
                         lifecycle_ridgeline_data=lifecycle_ridgeline_data,
                         lifecycle_timeline_data=lifecycle_timeline_data,
                         lifecycle_hexbin_data=lifecycle_hexbin_data,
                         lifecycle_parallel_data=lifecycle_parallel_data,
                         evolution_stream_data=evolution_stream_data,
                         evolution_bubble_data=evolution_bubble_data,
                         evolution_hexbin_data=evolution_hexbin_data,
                         evolution_parallel_data=evolution_parallel_data,
                         evolution_tree_data=evolution_tree_data,
                         all_genres=all_genres,
                         all_platforms=all_platforms,
                         min_year_data=min_year_data,
                         max_year_data=max_year_data,
                         min_year=min_year_data,
                         max_year=max_year_data,
                         year_range=year_range,
                         selected_genres=selected_genres,
                         selected_platforms=selected_platforms,
                         tactical_kpis=tactical_kpis)

@app.route('/search')
def search():
    # Example search parameters (you can modify these based on your needs)
    search_term = request.args.get('q', '')
    min_rating = request.args.get('min_rating', type=float)
    max_rating = request.args.get('max_rating', type=float)
    category = request.args.get('category', '')

    try:
        # Use the search_games method from MongoDBHandler
        results = db_handler.search_games(
            search_term=search_term,
            min_rating=min_rating,
            max_rating=max_rating,
            category=category
        )
        
        # Convert results to a format suitable for JSON response
        search_results = []
        for game in results:
            search_results.append({
                'title': game.get('Title', ''),
                'rating': game.get('Rating', 0),
                'genre': game.get('Genre', ''),
                'platform': game.get('Platform', ''),
                'publisher': game.get('Publisher', '')
            })
        
        return jsonify({
            'results': search_results,
            'count': len(search_results)
        })
    except Exception as e:
        logger.error(f"Search error: {e}")
        return jsonify({'error': 'Search failed', 'results': [], 'count': 0}), 500

@app.route('/filter_options')
def get_filter_options():
    """Get available filter options for dropdowns."""
    try:
        # Get genre options
        genre_mapping = db_handler.get_mapping_data('genre_mapping')
        genres = [item['Name'] for item in genre_mapping]

        # Get platform options
        platform_mapping = db_handler.get_mapping_data('platform_mapping')
        platforms = [item['Name'] for item in platform_mapping]

        return jsonify({
            'genres': sorted(genres),
            'platforms': sorted(platforms)
        })
    except Exception as e:
        logger.error(f"Filter options error: {e}")
        return jsonify({'genres': [], 'platforms': []}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001) 