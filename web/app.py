#!/usr/bin/env python3
"""
TERRASCAN
Full-featured environmental health dashboard
"""

import sys
import os
import json
from datetime import datetime, timedelta
from flask import Flask, render_template, jsonify, make_response
from dotenv import load_dotenv
from database.db import execute_query

# Load environment variables
load_dotenv()

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from database.db import init_database, execute_query
from tasks.runner import TaskRunner
from utils import get_version, register_template_filters

def create_app():
    """Create and configure the Flask application"""
    app = Flask(__name__, 
                static_folder='static',
                static_url_path='/static')
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'eco-watch-terra-scan-2024')
    
    # Initialize database on startup
    init_database()
    
    # Add version and cache-busting to all templates
    @app.context_processor
    def inject_version():
        return {
            'version': get_version(),
            'cache_bust': datetime.now().timestamp(),
            'build_time': datetime.now().strftime('%Y%m%d-%H%M%S')
        }
    
    # Disable Flask template caching in production
    app.jinja_env.cache = {}
    app.jinja_env.auto_reload = True
    
    # Register datetime template filters
    register_template_filters(app)

    # Enhanced cache-busting decorator for main pages
    def no_cache(f):
        """Decorator to prevent ALL caching of dynamic content"""
        def decorated_function(*args, **kwargs):
            response = make_response(f(*args, **kwargs))
            # Ultra-aggressive cache busting headers
            response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0, private'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '0'
            response.headers['Last-Modified'] = datetime.now().strftime('%a, %d %b %Y %H:%M:%S GMT')
            response.headers['ETag'] = f'"{datetime.now().timestamp()}"'
            # Additional Railway/CDN cache busting
            response.headers['Vary'] = 'Accept-Encoding, User-Agent'
            response.headers['X-Accel-Expires'] = '0'  # Nginx cache busting
            response.headers['Surrogate-Control'] = 'no-store'  # Varnish/CDN cache busting
            return response
        decorated_function.__name__ = f.__name__
        return decorated_function

    @app.route('/')
    @no_cache
    def index():
        """TERRASCAN - Homepage with environmental overview and hero map"""
        try:
            # Get current environmental data
            health_data = get_environmental_health_data()
            
            # Calculate environmental health score
            health_score = calculate_environmental_health_score(health_data)
            
            # Prepare template data with individual data sections
            fire_data = {
                'active_fires': health_data['fires']['count'],
                'count': health_data['fires']['count'],
                'avg_brightness': health_data['fires']['avg_brightness'],
                'last_update': health_data['last_updated']
            }
            
            air_data = {
                'avg_pm25': health_data['air_quality']['avg_pm25'],
                'measurements': health_data['air_quality']['station_count'],
                'status': get_air_quality_status(health_data['air_quality']['avg_pm25']),
                'last_update': health_data['last_updated']
            }
            
            ocean_data = {
                'avg_temp': health_data['ocean_temperature']['avg_temp'],
                'measurements': health_data['ocean_temperature']['station_count'],
                'status': get_ocean_status(health_data['ocean_temperature']['avg_temp']),
                'last_update': health_data['last_updated']
            }
            
            weather_data = {
                'avg_temp': health_data['weather']['avg_temp'],
                'avg_humidity': health_data['weather']['avg_humidity'],
                'avg_wind_speed': health_data['weather']['avg_wind_speed'],
                'avg_pressure': health_data['weather']['avg_pressure'],
                'alert_count': health_data['weather']['alert_count'],
                'city_count': health_data['weather']['city_count'],
                'last_update': health_data['last_updated']
            }
            
            biodiversity_data = {
                'avg_observations': health_data['biodiversity']['avg_observations'],
                'avg_diversity': health_data['biodiversity']['avg_diversity'],
                'region_count': health_data['biodiversity']['region_count'],
                'total_observations': health_data['biodiversity']['total_observations'],
                'last_update': health_data['last_updated']
            }
            
            response = make_response(render_template('index.html',
                                                   health_data=health_data,
                                                   health_score=health_score,
                                                   fire_data=fire_data,
                                                   air_data=air_data,
                                                   ocean_data=ocean_data,
                                                   weather_data=weather_data,
                                                   biodiversity_data=biodiversity_data))
            
            # Extra aggressive cache busting for this specific issue
            response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '0'
            response.headers['Last-Modified'] = datetime.now().strftime('%a, %d %b %Y %H:%M:%S GMT')
            response.headers['ETag'] = f'"{datetime.now().timestamp()}"'
            
            return response
                                 
        except Exception as e:
            return f"TERRASCAN Error: {e}", 500

    @app.route('/dashboard')
    @no_cache
    def dashboard():
        """TERRASCAN - Single dashboard showing environmental health"""
        try:
            # Get current environmental data
            health_data = get_environmental_health_data()
            
            # Calculate environmental health score
            health_score = calculate_environmental_health_score(health_data)
            
            # Prepare template data with individual data sections (same as index route)
            fire_data = {
                'active_fires': health_data['fires']['count'],
                'count': health_data['fires']['count'],
                'avg_brightness': health_data['fires']['avg_brightness'],
                'status': 'ACTIVE MONITORING' if health_data['fires']['count'] > 0 else 'NORMAL',
                'last_update': health_data['last_updated']
            }
            
            air_data = {
                'avg_pm25': health_data['air_quality']['avg_pm25'],
                'measurements': health_data['air_quality']['station_count'],
                'status': get_air_quality_status(health_data['air_quality']['avg_pm25']),
                'last_update': health_data['last_updated']
            }
            
            ocean_data = {
                'avg_temp': health_data['ocean_temperature']['avg_temp'],
                'measurements': health_data['ocean_temperature']['station_count'],
                'status': get_ocean_status(health_data['ocean_temperature']['avg_temp']),
                'last_update': health_data['last_updated']
            }
            
            return render_template('dashboard.html', 
                                 health_data=health_data,
                                 health_score=health_score,
                                 fire_data=fire_data,
                                 air_data=air_data,
                                 ocean_data=ocean_data)
                                 
        except Exception as e:
            return f"TERRASCAN Error: {e}", 500

    @app.route('/map')
    @no_cache
    def map_view():
        """TERRASCAN - Interactive world map with environmental data layers"""
        try:
            # Get current environmental data for health score widget
            health_data = get_environmental_health_data()
            
            # Calculate environmental health score
            health_score = calculate_environmental_health_score(health_data)
            
            return render_template('map.html',
                                 health_data=health_data,
                                 health_score=health_score)
                                 
        except Exception as e:
            return f"TERRASCAN Map Error: {e}", 500

    @app.route('/about')
    def about():
        """TERRASCAN - About page with project information"""
        return render_template('about.html')

    @app.route('/tasks')
    @no_cache
    def tasks():
        """TERRASCAN - Task management and monitoring interface"""
        try:
            # Get all tasks from database
            all_tasks = execute_query("""
                SELECT id, name, description, command, active, cron_schedule, 
                       created_date, updated_date, parameters
                FROM task 
                ORDER BY name
            """)
            
            # Get recent task runs with details
            recent_runs = execute_query("""
                SELECT tl.*, t.name as task_name, t.description as task_description
                FROM task_log tl 
                JOIN task t ON tl.task_id = t.id 
                ORDER BY tl.started_at DESC 
                LIMIT 50
            """)
            
            # Get currently running tasks
            running_query = """
                SELECT tl.*, t.name as task_name, t.description as task_description
                FROM task_log tl 
                JOIN task t ON tl.task_id = t.id 
                WHERE tl.completed_at IS NULL 
                AND tl.started_at > NOW() - INTERVAL '1 hour'
                ORDER BY tl.started_at DESC
            """
            
            running_tasks = execute_query(running_query)
            
            # Calculate task statistics
            stats = {
                'total_tasks': len(all_tasks),
                'active_tasks': len([t for t in all_tasks if t['active']]),
                'running_tasks': len(running_tasks),
                'recent_runs': len(recent_runs)
            }
            
            return render_template('tasks.html',
                                 tasks=all_tasks,
                                 recent_runs=recent_runs,
                                 running_tasks=running_tasks,
                                 stats=stats)
                                 
        except Exception as e:
            return f"TERRASCAN Tasks Error: {e}", 500

    @app.route('/system')
    @no_cache
    def system():
        """TERRASCAN - System status and data provider information"""
        try:
            # Get system statistics (safely handle empty results)
            total_records_result = execute_query("SELECT COUNT(*) as count FROM metric_data")
            total_records = total_records_result[0]['count'] if total_records_result and total_records_result[0]['count'] is not None else 0
            
            active_tasks_query = "SELECT COUNT(*) as count FROM task WHERE active = true"
            
            active_tasks_result = execute_query(active_tasks_query)
            active_tasks = active_tasks_result[0]['count'] if active_tasks_result and active_tasks_result[0]['count'] is not None else 0
            
            recent_runs_query = "SELECT COUNT(*) as count FROM task_log WHERE started_at > NOW() - INTERVAL '24 hours'"
            
            recent_runs_result = execute_query(recent_runs_query)
            recent_runs_count = recent_runs_result[0]['count'] if recent_runs_result and recent_runs_result[0]['count'] is not None else 0
            
            system_status = {
                'total_records': total_records,
                'active_tasks': active_tasks,
                'recent_runs': recent_runs_count
            }
            
            # Get provider statistics
            providers = {}
            
            # NASA FIRMS stats
            nasa_stats_result = execute_query("""
                SELECT COUNT(*) as total_records, MAX(timestamp) as last_run
                FROM metric_data
                WHERE provider_key = 'nasa_firms'
            """)
            nasa_stats = nasa_stats_result[0] if nasa_stats_result else {'total_records': 0, 'last_run': None}
            providers['nasa_firms'] = {
                'total_records': nasa_stats['total_records'] or 0,
                'last_run': nasa_stats['last_run'] or 'Never',
                'status': 'operational' if (nasa_stats['total_records'] or 0) > 0 else 'no_data'
            }
            
            # OpenAQ stats
            openaq_stats_result = execute_query("""
                SELECT COUNT(*) as total_records, MAX(timestamp) as last_run
                FROM metric_data 
                WHERE provider_key = 'openaq'
            """)
            openaq_stats = openaq_stats_result[0] if openaq_stats_result else {'total_records': 0, 'last_run': None}
            providers['openaq'] = {
                'total_records': openaq_stats['total_records'] or 0,
                'last_run': openaq_stats['last_run'] or 'Never',
                'status': 'operational' if (openaq_stats['total_records'] or 0) > 0 else 'no_data'
            }
            
            # NOAA Ocean stats
            noaa_stats_result = execute_query("""
                SELECT COUNT(*) as total_records, MAX(timestamp) as last_run
                FROM metric_data
                WHERE provider_key = 'noaa_ocean'
            """)
            noaa_stats = noaa_stats_result[0] if noaa_stats_result else {'total_records': 0, 'last_run': None}
            providers['noaa_ocean'] = {
                'total_records': noaa_stats['total_records'] or 0,
                'last_run': noaa_stats['last_run'] or 'Never',
                'status': 'operational' if (noaa_stats['total_records'] or 0) > 0 else 'no_data'
            }
            
            # OpenWeather stats
            weather_stats_result = execute_query("""
                SELECT COUNT(*) as total_records, MAX(timestamp) as last_run
                FROM metric_data
                WHERE provider_key = 'openweather'
            """)
            weather_stats = weather_stats_result[0] if weather_stats_result else {'total_records': 0, 'last_run': None}
            providers['openweather'] = {
                'total_records': weather_stats['total_records'] or 0,
                'last_run': weather_stats['last_run'] or 'Never',
                'status': 'operational' if (weather_stats['total_records'] or 0) > 0 else 'no_data'
            }
            
            # GBIF Biodiversity stats
            gbif_stats_result = execute_query("""
                SELECT COUNT(*) as total_records, MAX(timestamp) as last_run
                FROM metric_data
                WHERE provider_key = 'gbif'
            """)
            gbif_stats = gbif_stats_result[0] if gbif_stats_result else {'total_records': 0, 'last_run': None}
            providers['gbif'] = {
                'total_records': gbif_stats['total_records'] or 0,
                'last_run': gbif_stats['last_run'] or 'Never',
                'status': 'operational' if (gbif_stats['total_records'] or 0) > 0 else 'no_data'
            }
            
            # Get recent task runs
            recent_runs = execute_query("""
                SELECT tl.*, t.name as task_name, t.description as task_description
                FROM task_log tl 
                JOIN task t ON tl.task_id = t.id 
                ORDER BY tl.started_at DESC 
                LIMIT 20
            """)
            
            # Get data breakdown by provider
            data_breakdown = execute_query("""
                SELECT provider_key, COUNT(*) as record_count
                FROM metric_data 
                GROUP BY provider_key
                ORDER BY record_count DESC
            """)
            
            # Get database info
            database_size = "PostgreSQL (Railway)"
            
            # Check if simulation mode is enabled
            from database.config_manager import get_system_config
            simulation_mode = get_system_config('simulation_mode', True)
            
            # Get version info
            from utils import get_version
            version = get_version()
            
            return render_template('system.html',
                                 system_status=system_status,
                                 providers=providers,
                                 recent_runs=recent_runs,
                                 data_breakdown=data_breakdown,
                                 database_size=database_size,
                                 simulation_mode=simulation_mode,
                                 version=version)
                                 
        except Exception as e:
            return f"TERRASCAN System Error: {e}", 500

    @app.route('/api/map-data')
    @no_cache
    def api_map_data():
        """API endpoint to get environmental data for map visualization"""
        try:
            # Get fire data with coordinates
            fires_query = """
                SELECT location_lat as latitude, location_lng as longitude,
                       value as brightness, 
                       75 as confidence,
                       DATE(timestamp) as acq_date
                FROM metric_data 
                WHERE provider_key = 'nasa_firms' 
                AND timestamp > NOW() - INTERVAL '24 hours'
                AND location_lat IS NOT NULL 
                AND location_lng IS NOT NULL
                AND value > 300
                ORDER BY timestamp DESC
                LIMIT 500
            """
            
            fires = execute_query(fires_query)
            
            # Get air quality data with coordinates
            air_query = """
                SELECT location_lat as latitude, location_lng as longitude,
                       AVG(value) as value,
                       MAX(metadata) as metadata,
                       MAX(timestamp) as last_updated
                FROM metric_data 
                WHERE provider_key = 'openaq' 
                AND metric_name = 'air_quality_pm25'
                AND timestamp > NOW() - INTERVAL '7 days'
                AND location_lat IS NOT NULL 
                AND location_lng IS NOT NULL
                GROUP BY location_lat, location_lng
                ORDER BY value DESC
                LIMIT 200
            """
            
            air_quality = execute_query(air_query)
            
            # Get ocean data with coordinates
            ocean_query = """
                SELECT location_lat as latitude, location_lng as longitude,
                       AVG(CASE WHEN metric_name = 'water_temperature' THEN value END) as temperature,
                       AVG(CASE WHEN metric_name = 'water_level' THEN value END) as water_level,
                       MAX(metadata) as metadata,
                       MAX(timestamp) as last_updated
                FROM metric_data 
                WHERE provider_key = 'noaa_ocean' 
                AND DATE(timestamp) > CURRENT_DATE - INTERVAL '7 days'
                AND location_lat IS NOT NULL 
                AND location_lng IS NOT NULL
                GROUP BY location_lat, location_lng
                LIMIT 20
            """
            
            ocean_stations = execute_query(ocean_query)
            
            # Process data for map
            fire_data = []
            for fire in fires or []:
                fire_data.append({
                    'latitude': fire['latitude'],
                    'longitude': fire['longitude'],
                    'brightness': fire['brightness'],
                    'confidence': fire['confidence'] or 75,
                    'acq_date': fire['acq_date']
                })
            
            air_data = []
            for station in air_quality or []:
                # Extract location name from metadata if available
                location = "Unknown Location"
                try:
                    if station['metadata']:
                        metadata = json.loads(station['metadata'])
                        location = metadata.get('location', location)
                except:
                    pass
                    
                air_data.append({
                    'latitude': station['latitude'],
                    'longitude': station['longitude'],
                    'value': round(station['value'], 1),
                    'location': location,
                    'last_updated': station['last_updated']
                })
            
            ocean_data = []
            for station in ocean_stations or []:
                # Extract station name from metadata if available
                name = "Ocean Station"
                try:
                    if station['metadata']:
                        metadata = json.loads(station['metadata'])
                        name = metadata.get('station_name', name)
                except:
                    pass
                    
                ocean_data.append({
                    'latitude': station['latitude'],
                    'longitude': station['longitude'],
                    'temperature': round(station['temperature'], 1) if station['temperature'] else 20.0,
                    'water_level': round(station['water_level'], 2) if station['water_level'] else 0.0,
                    'name': name,
                    'last_updated': station['last_updated']
                })
            
            return jsonify({
                'success': True,
                'fires': fire_data,
                'air_quality': air_data,
                'ocean': ocean_data,
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e),
                'fires': [],
                'air_quality': [],
                'ocean': []
            })

    @app.route('/api/refresh')
    def api_refresh():
        """Refresh environmental data by running tasks"""
        try:
            runner = TaskRunner()
            
            # Run all environmental data tasks
            results = []
            
            # NASA Fires
            fire_result = runner.run_task('nasa_fires_global', triggered_by='dashboard_refresh')
            results.append({'task': 'fires', 'success': fire_result['success']})
            
            # Air Quality  
            air_result = runner.run_task('openaq_latest', triggered_by='dashboard_refresh')
            results.append({'task': 'air_quality', 'success': air_result['success']})
            
            # Ocean Data (both water level and temperature)
            ocean_level_result = runner.run_task('noaa_ocean_water_level', triggered_by='dashboard_refresh')
            results.append({'task': 'ocean_level', 'success': ocean_level_result['success']})
            
            ocean_temp_result = runner.run_task('noaa_ocean_temperature', 
                                               triggered_by='dashboard_refresh',
                                               trigger_parameters={'product': 'water_temperature'})
            results.append({'task': 'ocean_temp', 'success': ocean_temp_result['success']})
            
            return jsonify({
                'success': True,
                'message': 'Environmental data refreshed',
                'results': results
            })
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    @app.route('/api/collect-all-data')
    @no_cache
    def api_collect_all_data():
        """API endpoint to manually trigger all environmental data collection"""
        try:
            from tasks.runner import TaskRunner
            runner = TaskRunner()
            
            # List of all data collection tasks to run
            tasks_to_run = [
                'nasa_fires_global',
                'openaq_latest', 
                'noaa_ocean_water_level',
                'noaa_ocean_temperature',
                'openweather_current',
                'gbif_species_observations'
            ]
            
            results = []
            total_records = 0
            
            for task_name in tasks_to_run:
                try:
                    result = runner.run_task(task_name, triggered_by='manual_collection')
                    results.append({
                        'task': task_name,
                        'success': result['success'],
                        'records': result.get('records_processed', 0),
                        'message': result.get('message', 'Completed')
                    })
                    if result['success']:
                        total_records += result.get('records_processed', 0)
                except Exception as e:
                    results.append({
                        'task': task_name,
                        'success': False,
                        'records': 0,
                        'error': str(e)
                    })
            
            successful_tasks = sum(1 for r in results if r['success'])
            
            return jsonify({
                'success': True,
                'timestamp': datetime.utcnow().isoformat(),
                'summary': {
                    'total_tasks': len(tasks_to_run),
                    'successful_tasks': successful_tasks,
                    'failed_tasks': len(tasks_to_run) - successful_tasks,
                    'total_records_collected': total_records
                },
                'task_results': results
            })
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }), 500

    @app.route('/api/collect-biodiversity')
    @no_cache
    def api_collect_biodiversity():
        """API endpoint to manually trigger biodiversity data collection"""
        try:
            # Check if we need to initialize production database first
            database_url = os.environ.get('DATABASE_URL')
            if database_url:
                # We're in production, check if tables exist
                try:
                    existing_tables = execute_query("SELECT COUNT(*) as count FROM information_schema.tables WHERE table_schema = 'public'")
                    table_count = existing_tables[0]['count'] if existing_tables else 0
                    
                    if table_count < 3:  # If we don't have the main tables
                        # Initialize production database
                        from setup_production_railway import setup_railway_production
                        setup_success = setup_railway_production()
                        
                        if not setup_success:
                            return jsonify({
                                'success': False,
                                'error': 'Failed to initialize production database',
                                'timestamp': datetime.utcnow().isoformat()
                            }), 500
                except Exception as e:
                    # If we can't check tables, try to initialize anyway
                    try:
                        from setup_production_railway import setup_railway_production
                        setup_railway_production()
                    except:
                        pass  # Continue with biodiversity collection
            
            # Test GBIF biodiversity collection
            try:
                from tasks.fetch_gbif_biodiversity import fetch_biodiversity_data
                
                print("🧪 Testing GBIF biodiversity data collection...")
                result = fetch_biodiversity_data(product='species_observations')
                
                if result['success']:
                    # Get updated biodiversity stats
                    if IS_PRODUCTION:
                        stats_query = """
                            SELECT 
                                COUNT(*) as total_records,
                                AVG(CASE WHEN metric_name = 'species_observations' THEN value END) as avg_observations,
                                AVG(CASE WHEN metric_name = 'species_diversity' THEN value END) as avg_diversity,
                                COUNT(DISTINCT CASE WHEN metric_name = 'species_observations' THEN CONCAT(location_lat, ',', location_lng) END) as region_count
                            FROM metric_data 
                            WHERE provider_key = 'gbif'
                            AND timestamp >= NOW() - INTERVAL '24 hours'
                        """
                    else:
                        stats_query = """
                            SELECT 
                                COUNT(*) as total_records,
                                AVG(CASE WHEN metric_name = 'species_observations' THEN value END) as avg_observations,
                                AVG(CASE WHEN metric_name = 'species_diversity' THEN value END) as avg_diversity,
                                COUNT(DISTINCT CASE WHEN metric_name = 'species_observations' THEN location_lat || ',' || location_lng END) as region_count
                            FROM metric_data 
                            WHERE provider_key = 'gbif'
                            AND timestamp >= datetime('now', '-24 hours')
                        """
                    
                    biodiversity_stats = execute_query(stats_query)
                    
                    stats = biodiversity_stats[0] if biodiversity_stats else {}
                    
                    return jsonify({
                        'success': True,
                        'timestamp': datetime.utcnow().isoformat(),
                        'message': result['message'],
                        'records_processed': result['records_processed'],
                        'biodiversity_stats': {
                            'total_records': stats.get('total_records', 0),
                            'avg_observations': round(stats.get('avg_observations', 0) or 0, 1),
                            'avg_diversity': round(stats.get('avg_diversity', 0) or 0, 1),
                            'region_count': stats.get('region_count', 0)
                        }
                    })
                else:
                    return jsonify({
                        'success': False,
                        'error': result.get('error', 'Unknown error'),
                        'timestamp': datetime.utcnow().isoformat()
                    }), 500
            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': str(e),
                    'timestamp': datetime.utcnow().isoformat()
                }), 500
                
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }), 500

    @app.route('/api/health')
    def api_health():
        """API endpoint for environmental health data"""
        try:
            health_data = get_environmental_health_data()
            health_score = calculate_environmental_health_score(health_data)
            
            return jsonify({
                'success': True,
                'data': health_data,
                'score': health_score
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            })

    @app.route('/api/setup-production')
    @no_cache
    def api_setup_production():
        """API endpoint to initialize production database"""
        try:
            # Check if we're in production
            database_url = os.environ.get('DATABASE_URL')
            if not database_url:
                return jsonify({
                    'success': False,
                    'error': 'Not in production environment - DATABASE_URL not found',
                    'timestamp': datetime.utcnow().isoformat()
                }), 400
            
            # Import and run the production setup
            from setup_production_railway import setup_railway_production
            
            success = setup_railway_production()
            
            if success:
                return jsonify({
                    'success': True,
                    'message': 'Production database initialized successfully',
                    'timestamp': datetime.utcnow().isoformat(),
                    'database_type': 'PostgreSQL',
                    'tables_created': [
                        'system_config',
                        'provider_config', 
                        'task',
                        'task_log',
                        'metric_data'
                    ],
                    'tasks_configured': 10,
                    'data_sources': [
                        'NASA FIRMS (fires)',
                        'OpenAQ (air quality)',
                        'NOAA Ocean (ocean data)',
                        'OpenWeatherMap (weather)',
                        'GBIF (biodiversity)'
                    ]
                })
            else:
                return jsonify({
                    'success': False,
                    'error': 'Production setup failed - check logs',
                    'timestamp': datetime.utcnow().isoformat()
                }), 500
                
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }), 500

    @app.route('/api/fix-tasks')
    @no_cache
    def api_fix_tasks():
        """API endpoint to fix task commands in production database"""
        try:
            # Check if we're in production
            database_url = os.environ.get('DATABASE_URL')
            if not database_url:
                return jsonify({
                    'success': False,
                    'error': 'Not in production environment',
                    'timestamp': datetime.utcnow().isoformat()
                }), 400
            
            # Update task commands to match actual function names
            task_updates = [
                ('nasa_fires_global', 'tasks.fetch_nasa_fires.fetch_nasa_fires', '{"region": "WORLD", "days": 7}'),
                ('openaq_latest', 'tasks.fetch_openaq_latest.fetch_openaq_latest', '{}'),
                ('noaa_ocean_water_level', 'tasks.fetch_noaa_ocean.fetch_noaa_ocean_data', '{"product": "water_level"}'),
                ('noaa_ocean_temperature', 'tasks.fetch_noaa_ocean.fetch_noaa_ocean_data', '{"product": "water_temperature"}'),
                ('openweather_current', 'tasks.fetch_openweathermap_weather.fetch_weather_data', '{"product": "current"}'),
                ('gbif_species_observations', 'tasks.fetch_gbif_biodiversity.fetch_biodiversity_data', '{"product": "species_observations"}'),
            ]
            
            updated_count = 0
            for task_name, command, parameters in task_updates:
                try:
                    from database.db import execute_insert
                    result = execute_insert("""
                        UPDATE task 
                        SET command = ?, parameters = ?, updated_date = CURRENT_TIMESTAMP
                        WHERE name = ?
                    """, (command, parameters, task_name))
                    if result:
                        updated_count += 1
                except Exception as e:
                    print(f"Failed to update task {task_name}: {e}")
            
            return jsonify({
                'success': True,
                'message': f'Updated {updated_count} task commands',
                'updated_tasks': updated_count,
                'timestamp': datetime.utcnow().isoformat()
            })
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }), 500

    @app.route('/health')
    def health_check():
        """Simple health check endpoint"""
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat()
        })

    @app.route('/api/debug-task/<task_name>')
    @no_cache
    def api_debug_task(task_name):
        """Debug endpoint to test individual task execution"""
        try:
            from tasks.runner import TaskRunner
            runner = TaskRunner()
            
            # Get the task details first
            from database.db import get_task_by_name
            task = get_task_by_name(task_name)
            
            if not task:
                return jsonify({
                    'success': False,
                    'error': f'Task {task_name} not found',
                    'timestamp': datetime.utcnow().isoformat()
                }), 404
            
            # Try to run the task with detailed error reporting
            result = runner.run_task(task_name, triggered_by='debug')
            
            return jsonify({
                'success': True,
                'task_details': {
                    'name': task['name'],
                    'command': task['command'],
                    'parameters': task['parameters'],
                    'active': task['active']
                },
                'execution_result': result,
                'timestamp': datetime.utcnow().isoformat()
            })
            
        except Exception as e:
            import traceback
            return jsonify({
                'success': False,
                'error': str(e),
                'traceback': traceback.format_exc(),
                'timestamp': datetime.utcnow().isoformat()
            }), 500

    # Task Management API Endpoints
    @app.route('/api/tasks')
    @no_cache
    def api_tasks():
        """Get all tasks with their current status"""
        try:
            # Get all tasks
            tasks = execute_query("""
                SELECT id, name, description, command, active, cron_schedule, 
                       created_date, updated_date, parameters
                FROM task 
                ORDER BY name
            """)
            
            # Get last run for each task
            for task in tasks:
                last_run = execute_query("""
                    SELECT * FROM task_log 
                    WHERE task_id = %s 
                    ORDER BY started_at DESC 
                    LIMIT 1
                """, (task['id'],))
                
                task['last_run'] = last_run[0] if last_run else None
            
            return jsonify({
                'success': True,
                'tasks': tasks
            })
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': f'Failed to get tasks: {str(e)}'
            }), 500

    @app.route('/api/tasks/<task_name>/run', methods=['POST'])
    @no_cache
    def api_run_task(task_name):
        """Trigger a task to run manually"""
        try:
            # Initialize task runner
            runner = TaskRunner()
            
            # Run the task
            result = runner.run_task(task_name, triggered_by='web_interface')
            
            if result['success']:
                return jsonify({
                    'success': True,
                    'message': f'Task "{task_name}" started successfully',
                    'run_id': result['run_id'],
                    'duration': result.get('duration', 0),
                    'records_processed': result.get('records_processed', 0)
                })
            else:
                return jsonify({
                    'success': False,
                    'error': result.get('error', 'Unknown error'),
                    'run_id': result.get('run_id')
                }), 500
                
        except Exception as e:
            return jsonify({
                'success': False,
                'error': f'Failed to run task: {str(e)}'
            }), 500

    @app.route('/api/tasks/<task_name>/logs')
    @no_cache
    def api_task_logs(task_name):
        """Get logs for a specific task"""
        try:
            # Get task logs
            logs = execute_query("""
                SELECT tl.*, t.name as task_name, t.description as task_description
                FROM task_log tl 
                JOIN task t ON tl.task_id = t.id 
                WHERE t.name = %s
                ORDER BY tl.started_at DESC 
                LIMIT 100
            """, (task_name,))
            
            return jsonify({
                'success': True,
                'logs': logs
            })
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': f'Failed to get task logs: {str(e)}'
            }), 500

    @app.route('/api/tasks/status')
    @no_cache
    def api_tasks_status():
        """Get overall task system status"""
        try:
            # Initialize task runner
            runner = TaskRunner()
            
            # Get task status
            status = runner.get_task_status()
            
            return jsonify({
                'success': True,
                'status': status
            })
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': f'Failed to get task status: {str(e)}'
            }), 500

    @app.route('/api/tasks/<task_name>/toggle', methods=['POST'])
    @no_cache
    def api_toggle_task(task_name):
        """Enable or disable a task"""
        try:
            # Get current task status
            task = execute_query("SELECT * FROM task WHERE name = %s", (task_name,))
            if not task:
                return jsonify({
                    'success': False,
                    'error': f'Task "{task_name}" not found'
                }), 404
            
            # Toggle active status
            new_status = not task[0]['active']
            
            execute_query("""
                UPDATE task 
                SET active = %s, updated_date = NOW() 
                WHERE name = %s
            """, (new_status, task_name))
            
            return jsonify({
                'success': True,
                'message': f'Task "{task_name}" {"enabled" if new_status else "disabled"}',
                'active': new_status
            })
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': f'Failed to toggle task: {str(e)}'
            }), 500



    @app.errorhandler(404)
    def not_found(error):
        return "TERRASCAN - Page not found", 404

    @app.errorhandler(500)
    def internal_error(error):
        return "TERRASCAN - Internal error", 500

    return app

def get_environmental_health_data():
    """Get current environmental health data from database"""
    try:
        # Get recent fire data (last 7 days)
        fire_query = """
            SELECT COUNT(*) as fire_count, AVG(value) as avg_brightness
            FROM metric_data 
            WHERE provider_key = 'nasa_firms' 
            AND timestamp >= NOW() - INTERVAL '7 days'
        """
        fire_data = execute_query(fire_query)
        
        # Get recent air quality data (last 7 days)
        air_query = """
            SELECT AVG(value) as avg_pm25, COUNT(*) as station_count
            FROM metric_data 
            WHERE provider_key = 'openaq' 
            AND metric_name = 'air_quality_pm25'
            AND timestamp >= NOW() - INTERVAL '7 days'
        """
        air_data = execute_query(air_query)
        
        # Get recent ocean temperature data (last 7 days)  
        ocean_query = """
            SELECT AVG(value) as avg_temp, COUNT(*) as station_count
            FROM metric_data
            WHERE provider_key = 'noaa_ocean'
            AND metric_name = 'water_temperature'
            AND timestamp >= NOW() - INTERVAL '7 days'
        """
        ocean_data = execute_query(ocean_query)
        
        # Get recent weather data (last 24 hours)
        weather_query = """
            SELECT 
                AVG(CASE WHEN metric_name = 'temperature' THEN value END) as avg_temp,
                AVG(CASE WHEN metric_name = 'humidity' THEN value END) as avg_humidity,
                AVG(CASE WHEN metric_name = 'wind_speed' THEN value END) as avg_wind_speed,
                AVG(CASE WHEN metric_name = 'atmospheric_pressure' THEN value END) as avg_pressure,
                COUNT(CASE WHEN metric_name = 'weather_alert' THEN 1 END) as alert_count,
                COUNT(DISTINCT CASE WHEN metric_name = 'temperature' THEN CONCAT(location_lat, ',', location_lng) END) as city_count
            FROM metric_data
            WHERE provider_key = 'openweather'
            AND timestamp >= NOW() - INTERVAL '24 hours'
        """
        weather_data = execute_query(weather_query)
        
        # Get recent biodiversity data (last 7 days)
        biodiversity_query = """
            SELECT 
                AVG(CASE WHEN metric_name = 'species_observations' THEN value END) as avg_observations,
                AVG(CASE WHEN metric_name = 'species_diversity' THEN value END) as avg_diversity,
                COUNT(DISTINCT CASE WHEN metric_name = 'species_observations' THEN CONCAT(location_lat, ',', location_lng) END) as region_count,
                SUM(CASE WHEN metric_name = 'species_observations' THEN value ELSE 0 END) as total_observations
            FROM metric_data
            WHERE provider_key = 'gbif'
            AND timestamp >= NOW() - INTERVAL '7 days'
        """
        
        biodiversity_data = execute_query(biodiversity_query)
        
        return {
            'fires': {
                'count': fire_data[0]['fire_count'] if fire_data else 0,
                'avg_brightness': round(fire_data[0]['avg_brightness'] or 0, 1) if fire_data else 0
            },
            'air_quality': {
                'avg_pm25': round(air_data[0]['avg_pm25'] or 0, 1) if air_data else 0,
                'station_count': air_data[0]['station_count'] if air_data else 0
            },
            'ocean_temperature': {
                'avg_temp': round(ocean_data[0]['avg_temp'] or 0, 1) if ocean_data else 0,
                'station_count': ocean_data[0]['station_count'] if ocean_data else 0
            },
            'weather': {
                'avg_temp': round(weather_data[0]['avg_temp'] or 0, 1) if weather_data else 0,
                'avg_humidity': round(weather_data[0]['avg_humidity'] or 0, 1) if weather_data else 0,
                'avg_wind_speed': round(weather_data[0]['avg_wind_speed'] or 0, 1) if weather_data else 0,
                'avg_pressure': round(weather_data[0]['avg_pressure'] or 0, 1) if weather_data else 0,
                'alert_count': weather_data[0]['alert_count'] if weather_data else 0,
                'city_count': weather_data[0]['city_count'] if weather_data else 0
            },
            'biodiversity': {
                'avg_observations': round(biodiversity_data[0]['avg_observations'] or 0, 1) if biodiversity_data else 0,
                'avg_diversity': round(biodiversity_data[0]['avg_diversity'] or 0, 1) if biodiversity_data else 0,
                'region_count': biodiversity_data[0]['region_count'] if biodiversity_data else 0,
                'total_observations': biodiversity_data[0]['total_observations'] if biodiversity_data else 0
            },
            'last_updated': datetime.utcnow().isoformat()
        }
    except Exception as e:
        # Return empty data on error
        return {
            'fires': {'count': 0, 'avg_brightness': 0},
            'air_quality': {'avg_pm25': 0, 'station_count': 0},
            'ocean_temperature': {'avg_temp': 0, 'station_count': 0},
            'weather': {'avg_temp': 0, 'avg_humidity': 0, 'avg_wind_speed': 0, 'avg_pressure': 0, 'alert_count': 0, 'city_count': 0},
            'biodiversity': {'avg_observations': 0, 'avg_diversity': 0, 'region_count': 0, 'total_observations': 0},
            'last_updated': datetime.utcnow().isoformat(),
            'error': str(e)
        }

def calculate_environmental_health_score(health_data):
    """Calculate environmental health score (0-100)"""
    score = 100  # Start with perfect score
    
    # Fire impact (up to -25 points)
    fire_count = health_data['fires']['count']
    if fire_count > 1000:
        score -= 25
    elif fire_count > 500:
        score -= 18
    elif fire_count > 100:
        score -= 10
    
    # Air quality impact (up to -30 points)  
    pm25 = health_data['air_quality']['avg_pm25']
    if pm25 > 75:  # Hazardous
        score -= 30
    elif pm25 > 55:  # Very unhealthy
        score -= 22
    elif pm25 > 35:  # Unhealthy
        score -= 15
    elif pm25 > 15:  # Moderate
        score -= 8
    
    # Ocean temperature impact (up to -15 points)
    ocean_temp = health_data['ocean_temperature']['avg_temp']
    if ocean_temp > 25:  # Very warm
        score -= 15
    elif ocean_temp > 23:  # Warm
        score -= 8
    elif ocean_temp < 15:  # Very cold
        score -= 12
    elif ocean_temp < 18:  # Cold
        score -= 5
    
    # Weather impact (up to -20 points)
    weather = health_data.get('weather', {})
    
    # Weather alerts impact (up to -10 points)
    alert_count = weather.get('alert_count', 0)
    if alert_count > 5:
        score -= 10
    elif alert_count > 2:
        score -= 6
    elif alert_count > 0:
        score -= 3
    
    # Extreme temperature impact (up to -5 points)
    avg_temp = weather.get('avg_temp', 20)
    if avg_temp > 40 or avg_temp < -10:  # Extreme temperatures
        score -= 5
    elif avg_temp > 35 or avg_temp < -5:  # Very hot/cold
        score -= 3
    
    # High wind speed impact (up to -3 points)
    wind_speed = weather.get('avg_wind_speed', 0)
    if wind_speed > 15:  # Very high winds (>54 km/h)
        score -= 3
    elif wind_speed > 10:  # High winds (>36 km/h)
        score -= 2
    
    # Low pressure systems (storms) impact (up to -2 points)
    pressure = weather.get('avg_pressure', 1013)
    if pressure < 980:  # Very low pressure (strong storms)
        score -= 2
    elif pressure < 1000:  # Low pressure (storms)
        score -= 1
    
    # Biodiversity impact (up to -10 points for poor biodiversity health)
    biodiversity = health_data.get('biodiversity', {})
    
    # Low species diversity impact (up to -5 points)
    avg_diversity = biodiversity.get('avg_diversity', 0)
    if avg_diversity < 5:  # Very low diversity
        score -= 5
    elif avg_diversity < 10:  # Low diversity
        score -= 3
    elif avg_diversity < 15:  # Moderate diversity
        score -= 1
    
    # Low observation counts (indicating ecosystem stress) (up to -3 points)
    avg_observations = biodiversity.get('avg_observations', 0)
    if avg_observations < 100:  # Very few observations
        score -= 3
    elif avg_observations < 500:  # Few observations
        score -= 2
    elif avg_observations < 1000:  # Moderate observations
        score -= 1
    
    # Lack of monitoring coverage (up to -2 points)
    region_count = biodiversity.get('region_count', 0)
    if region_count < 5:  # Very limited coverage
        score -= 2
    elif region_count < 10:  # Limited coverage
        score -= 1
    
    # Ensure score stays within bounds
    score = max(0, min(100, score))
    
    # Determine status based on score
    if score >= 80:
        status = 'STATUS EXCELLENT'
        color = '#28a745'  # Green
    elif score >= 60:
        status = 'STATUS GOOD'
        color = '#33a474'  # Deep green
    elif score >= 40:
        status = 'STATUS MODERATE'
        color = '#ffc107'  # Yellow
    elif score >= 20:
        status = 'STATUS POOR'
        color = '#fd7e14'  # Orange
    else:
        status = 'STATUS CRITICAL'
        color = '#dc3545'  # Red
    
    return {
        'score': score,
        'status': status,
        'color': color
    }

def get_air_quality_status(pm25):
    """Get air quality status based on PM2.5 levels"""
    if pm25 > 75:
        return 'HAZARDOUS'
    elif pm25 > 55:
        return 'VERY UNHEALTHY'
    elif pm25 > 35:
        return 'UNHEALTHY'
    elif pm25 > 15:
        return 'MODERATE'
    else:
        return 'GOOD'

def get_ocean_status(temp):
    """Get ocean status based on temperature"""
    if temp > 25:
        return 'WARM'
    elif temp < 15:
        return 'COOL'
    else:
        return 'NORMAL'

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000) 
