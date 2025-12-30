#!/usr/bin/env python3
"""
Terrascan - Environmental Health Dashboard
Clean, maintainable Flask application
"""

import os
import json
from datetime import datetime
from flask import Flask, render_template, jsonify, make_response, request
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import database and utilities
from database.db import (
    init_database, execute_query, execute_insert, get_running_tasks,
    get_recent_task_runs, get_task_by_name
)
from database.schema_inspector import get_schema_documentation
from tasks.runner import TaskRunner
from utils import get_version, register_template_filters
from utils.metric_value import create_metric_value
from utils.regional_scanner import get_scanner
from utils.regional_fetcher import get_regional_fetcher

def create_app():
    """Create and configure the Flask application"""
    app = Flask(__name__, static_folder='static', static_url_path='/static')
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'terrascan-2024')
    
    # Initialize database on startup
    init_database()
    
    # Register template filters and context
    register_template_filters(app)
    
    @app.context_processor
    def inject_version():
        return {'version': get_version()}
    
    # Simple no-cache decorator
    def no_cache(f):
        def decorated(*args, **kwargs):
            response = make_response(f(*args, **kwargs))
            response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '0'
            return response
        decorated.__name__ = f.__name__
        return decorated

    # Routes
    @app.route('/')
    @no_cache
    def index():
        """Homepage - Interactive map (main experience)"""
        try:
            health_data = get_environmental_health_data()
            health_score = calculate_environmental_health_score(health_data)
            return render_template('map.html',
                                 health_data=health_data,
                                 health_score=health_score)
        except Exception as e:
            return f"Error: {e}", 500

    @app.route('/status')
    @no_cache
    def status_dashboard():
        """Status dashboard - System overview with all metrics"""
        try:
            data = prepare_dashboard_data()
            return render_template('index.html', **data)
        except Exception as e:
            return f"Error: {e}", 500

    @app.route('/dashboard')
    @no_cache
    def dashboard():
        """Dashboard page (legacy redirect to status)"""
        try:
            data = prepare_dashboard_data()
            return render_template('dashboard.html', **data)
        except Exception as e:
            return f"Error: {e}", 500

    @app.route('/map')
    @no_cache
    def map_view():
        """Map page (legacy redirect to home)"""
        try:
            health_data = get_environmental_health_data()
            health_score = calculate_environmental_health_score(health_data)
            return render_template('map.html',
                                 health_data=health_data,
                                 health_score=health_score)
        except Exception as e:
            return f"Error: {e}", 500

    @app.route('/about')
    def about():
        """About page"""
        return render_template('about.html')

    @app.route('/tasks')
    @no_cache
    def tasks():
        """Task management page"""
        try:
            # Get tasks with last run information
            all_tasks = execute_query("""
                SELECT t.id, t.name, t.description, t.command, t.active, t.cron_schedule, 
                       t.created_date, t.updated_date, t.parameters,
                       lr.last_run_time, lr.last_status, lr.last_records_processed, lr.last_duration
                FROM task t
                LEFT JOIN (
                    SELECT task_id,
                           MAX(started_at) as last_run_time,
                           (SELECT status FROM task_log tl2 WHERE tl2.task_id = task_log.task_id AND tl2.started_at = MAX(task_log.started_at) LIMIT 1) as last_status,
                           (SELECT records_processed FROM task_log tl3 WHERE tl3.task_id = task_log.task_id AND tl3.started_at = MAX(task_log.started_at) LIMIT 1) as last_records_processed,
                           (SELECT duration_seconds FROM task_log tl4 WHERE tl4.task_id = task_log.task_id AND tl4.started_at = MAX(task_log.started_at) LIMIT 1) as last_duration
                    FROM task_log 
                    GROUP BY task_id
                ) lr ON t.id = lr.task_id
                ORDER BY t.name
            """)
            
            recent_runs = execute_query("""
                SELECT tl.*, t.name as task_name, t.description as task_description
                FROM task_log tl 
                JOIN task t ON tl.task_id = t.id 
                ORDER BY tl.started_at DESC LIMIT 50
            """)
            
            # Get running tasks
            running_tasks = get_running_tasks()

            # Simple stats
            stats = {
                'total_tasks': len(all_tasks),
                'active_tasks': len([t for t in all_tasks if t['active']]),
                'recent_runs': len(recent_runs),
                'running_tasks': len(running_tasks)
            }

            return render_template('tasks.html',
                                 tasks=all_tasks,
                                 recent_runs=recent_runs,
                                 stats=stats,
                                 running_tasks=running_tasks)
        except Exception as e:
            return f"Error: {e}", 500

    @app.route('/system')
    @no_cache
    def system():
        """System status page"""
        try:
            # Basic system stats
            total_records = get_count("SELECT COUNT(*) FROM metric_data")
            active_tasks = get_count("SELECT COUNT(*) FROM task WHERE active = true")
            recent_runs = get_count("""
                SELECT COUNT(*) FROM task_log 
                WHERE started_at > NOW() - INTERVAL '24 hours'
            """)
            
            system_status = {
                'total_records': total_records,
                'active_tasks': active_tasks,
                'recent_runs': recent_runs
            }
            
            # Provider stats (simplified)
            providers = get_provider_stats()
            
            # Recent runs
            recent_runs = execute_query("""
                SELECT tl.*, t.name as task_name, t.description as task_description
                FROM task_log tl 
                JOIN task t ON tl.task_id = t.id 
                ORDER BY tl.started_at DESC LIMIT 20
            """)
            
            # Data breakdown
            data_breakdown = execute_query("""
                SELECT provider_key, COUNT(*) as record_count
                FROM metric_data
                GROUP BY provider_key
                ORDER BY record_count DESC
            """)

            # Get database size
            db_size_result = execute_query("""
                SELECT pg_size_pretty(pg_database_size(current_database())) as size
            """)
            database_size = db_size_result[0]['size'] if db_size_result else 'Unknown'

            return render_template('system.html',
                                 system_status=system_status,
                                 providers=providers,
                                 recent_runs=recent_runs,
                                 data_breakdown=data_breakdown,
                                 database_size=database_size,
                                 simulation_mode=False,
                                 version=get_version())
        except Exception as e:
            return f"Error: {e}", 500

    @app.route('/system/schema')
    @no_cache
    def system_schema():
        """Database schema documentation page"""
        try:
            schema_data = get_schema_documentation()
            
            if 'error' in schema_data:
                return f"Schema Error: {schema_data['error']}", 500
            
            return render_template('system_schema.html',
                                 schema=schema_data,
                                 version=get_version())
        except Exception as e:
            return f"Error: {e}", 500

    # API Routes
    @app.route('/api/map-data')
    @no_cache
    def api_map_data():
        """Get environmental data for map"""
        try:
            # Get recent fire data
            fires = execute_query("""
                SELECT location_lat as latitude, location_lng as longitude,
                       value as brightness, DATE(timestamp) as acq_date, metadata
                FROM metric_data
                WHERE provider_key = 'nasa_firms'
                AND timestamp > NOW() - INTERVAL '24 hours'
                AND location_lat IS NOT NULL AND location_lng IS NOT NULL
                AND value > 300
                ORDER BY timestamp DESC LIMIT 500
            """)
            
            # Get air quality data - include recently scanned stations + worst globally
            air_quality = execute_query("""
                SELECT location_lat as latitude, location_lng as longitude,
                       AVG(value) as value, MAX(metadata) as metadata
                FROM metric_data
                WHERE provider_key = 'openaq'
                AND metric_name = 'air_quality_pm25'
                AND timestamp > NOW() - INTERVAL '7 days'
                AND location_lat IS NOT NULL AND location_lng IS NOT NULL
                GROUP BY location_lat, location_lng
                ORDER BY MAX(timestamp) DESC, value DESC LIMIT 500
            """)
            
            # Get ocean data (using Open-Meteo for global SST coverage)
            ocean_stations = execute_query("""
                SELECT location_lat as latitude, location_lng as longitude,
                       AVG(value) as temperature,
                       NULL as water_level,
                       MAX(timestamp) as last_updated,
                       MAX(metadata) as metadata
                FROM metric_data
                WHERE provider_key = 'openmeteo_marine'
                AND metric_name = 'sea_surface_temperature'
                AND timestamp > NOW() - INTERVAL '7 days'
                AND location_lat IS NOT NULL AND location_lng IS NOT NULL
                GROUP BY location_lat, location_lng LIMIT 50
            """)

            # Get conflict data from UCDP
            conflicts = execute_query("""
                SELECT location_lat as latitude, location_lng as longitude,
                       value as deaths, metadata, timestamp
                FROM metric_data
                WHERE provider_key = 'ucdp'
                AND metric_name = 'conflict_event'
                AND timestamp > NOW() - INTERVAL '365 days'
                AND location_lat IS NOT NULL AND location_lng IS NOT NULL
                ORDER BY timestamp DESC LIMIT 500
            """)

            # Get biodiversity data from GBIF
            biodiversity = execute_query("""
                SELECT location_lat as latitude, location_lng as longitude,
                       value as observations, metadata
                FROM metric_data
                WHERE provider_key = 'gbif'
                AND metric_name = 'species_observations'
                AND timestamp > NOW() - INTERVAL '30 days'
                AND location_lat IS NOT NULL AND location_lng IS NOT NULL
                ORDER BY value DESC LIMIT 50
            """)

            # Get aurora forecast from NOAA SWPC
            aurora = execute_query("""
                SELECT location_lat as latitude, location_lng as longitude,
                       value as intensity, metadata
                FROM metric_data
                WHERE provider_key = 'noaa_swpc'
                AND metric_name = 'aurora_forecast'
                AND location_lat IS NOT NULL AND location_lng IS NOT NULL
                ORDER BY value DESC LIMIT 2000
            """)

            # Get current Kp index
            kp_index = execute_query("""
                SELECT value as kp, metadata, timestamp
                FROM metric_data
                WHERE provider_key = 'noaa_swpc'
                AND metric_name = 'kp_index'
                ORDER BY timestamp DESC LIMIT 1
            """)

            return jsonify({
                'success': True,
                'fires': format_fire_data(fires or []),
                'air_quality': format_air_data(air_quality or []),
                'ocean': format_ocean_data(ocean_stations or []),
                'conflicts': format_conflict_data(conflicts or []),
                'biodiversity': format_biodiversity_data(biodiversity or []),
                'aurora': format_aurora_data(aurora or [], kp_index[0] if kp_index else None)
            })
            
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})

    @app.route('/api/refresh')
    def api_refresh():
        """Refresh environmental data"""
        try:
            runner = TaskRunner()
            
            # Run key tasks
            tasks = ['nasa_fires_global', 'openaq_latest', 'noaa_ocean_water_level', 'noaa_ocean_temperature', 'openmeteo_marine', 'ucdp_conflicts', 'noaa_aurora']
            results = []
            
            for task_name in tasks:
                result = runner.run_task(task_name, triggered_by='api_refresh')
                results.append({
                    'task': task_name,
                    'success': result['success']
                })
            
            return jsonify({
                'success': True,
                'message': 'Data refresh completed',
                'results': results
            })
            
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/health')
    def api_health():
        """Health check endpoint"""
        try:
            health_data = get_environmental_health_data()
            health_score = calculate_environmental_health_score(health_data)
            
            return jsonify({
                'success': True,
                'data': health_data,
                'score': health_score
            })
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})

    # Task Management API
    @app.route('/api/tasks')
    @no_cache
    def api_tasks():
        """Get all tasks"""
        try:
            tasks = execute_query("""
                SELECT t.id, t.name, t.description, t.command, t.active, t.cron_schedule, 
                       t.created_date, t.updated_date, t.parameters,
                       lr.last_run_time, lr.last_status, lr.last_records_processed, lr.last_duration
                FROM task t
                LEFT JOIN (
                    SELECT task_id,
                           MAX(started_at) as last_run_time,
                           (SELECT status FROM task_log tl2 WHERE tl2.task_id = task_log.task_id AND tl2.started_at = MAX(task_log.started_at) LIMIT 1) as last_status,
                           (SELECT records_processed FROM task_log tl3 WHERE tl3.task_id = task_log.task_id AND tl3.started_at = MAX(task_log.started_at) LIMIT 1) as last_records_processed,
                           (SELECT duration_seconds FROM task_log tl4 WHERE tl4.task_id = task_log.task_id AND tl4.started_at = MAX(task_log.started_at) LIMIT 1) as last_duration
                    FROM task_log 
                    GROUP BY task_id
                ) lr ON t.id = lr.task_id
                ORDER BY t.name
            """)
            return jsonify({'success': True, 'tasks': tasks})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/tasks/create', methods=['POST'])
    @no_cache
    def api_create_task():
        """Create a new task"""
        try:
            data = request.get_json()
            if not data:
                return jsonify({'success': False, 'error': 'No JSON data provided'}), 400

            name = data.get('name')
            description = data.get('description', '')
            command = data.get('command')
            cron_schedule = data.get('cron_schedule', '0 */6 * * *')
            active = data.get('active', True)

            if not name or not command:
                return jsonify({'success': False, 'error': 'name and command are required'}), 400

            execute_insert("""
                INSERT INTO task (name, description, command, cron_schedule, active)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (name) DO UPDATE SET
                    command = EXCLUDED.command,
                    description = EXCLUDED.description,
                    cron_schedule = EXCLUDED.cron_schedule,
                    active = EXCLUDED.active
            """, (name, description, command, cron_schedule, active))

            return jsonify({'success': True, 'message': f'Task "{name}" created/updated'})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/tasks/<task_name>/run', methods=['POST'])
    @no_cache
    def api_run_task(task_name):
        """Run a task manually"""
        try:
            runner = TaskRunner()
            result = runner.run_task(task_name, triggered_by='web_interface')
            
            return jsonify({
                'success': result['success'],
                'message': f'Task "{task_name}" completed',
                'run_id': result.get('run_id'),
                'records_processed': result.get('records_processed', 0)
            })
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/tasks/<task_name>/logs')
    @no_cache
    def api_task_logs(task_name):
        """Get task logs"""
        try:
            logs = execute_query("""
                SELECT tl.*, t.name as task_name, t.description as task_description
                FROM task_log tl 
                JOIN task t ON tl.task_id = t.id 
                WHERE t.name = %s
                ORDER BY tl.started_at DESC LIMIT 100
            """, (task_name,))
            
            return jsonify({'success': True, 'logs': logs})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/tasks/status')
    @no_cache
    def api_tasks_status():
        """Get current task system status"""
        try:
            running = get_running_tasks()
            recent = get_recent_task_runs(limit=5)

            return jsonify({
                'success': True,
                'running_tasks': len(running),
                'running_details': running,
                'recent_runs': recent
            })
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/tasks/<task_name>/toggle', methods=['POST'])
    @no_cache
    def api_toggle_task(task_name):
        """Toggle task active status"""
        try:
            # Get current task
            task = get_task_by_name(task_name)
            if not task:
                return jsonify({'success': False, 'error': f'Task {task_name} not found'}), 404

            # Toggle active status
            new_status = not task['active']
            execute_query(
                "UPDATE task SET active = %s, updated_date = NOW() WHERE name = %s",
                (new_status, task_name)
            )

            return jsonify({
                'success': True,
                'task': task_name,
                'active': new_status,
                'message': f'Task {task_name} {"enabled" if new_status else "disabled"}'
            })
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/collect-all-data', methods=['POST'])
    @no_cache
    def api_collect_all_data():
        """Run all data collection tasks"""
        try:
            runner = TaskRunner()
            tasks = ['nasa_fires_global', 'openaq_latest', 'noaa_ocean_water_level',
                     'noaa_ocean_temperature', 'openmeteo_marine', 'ucdp_conflicts', 'noaa_aurora']
            results = []

            for task_name in tasks:
                result = runner.run_task(task_name, triggered_by='web_collect_all')
                results.append({
                    'task': task_name,
                    'success': result['success'],
                    'records': result.get('records_processed', 0)
                })

            total_records = sum(r['records'] for r in results)
            successful = sum(1 for r in results if r['success'])

            return jsonify({
                'success': True,
                'message': f'Completed {successful}/{len(tasks)} tasks, {total_records} records',
                'results': results
            })
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/collect-biodiversity', methods=['POST'])
    @no_cache
    def api_collect_biodiversity():
        """Run biodiversity data collection"""
        try:
            runner = TaskRunner()
            result = runner.run_task('gbif_species_observations', triggered_by='web_interface')

            return jsonify({
                'success': result['success'],
                'message': f'Biodiversity collection completed',
                'records_processed': result.get('records_processed', 0)
            })
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/schema')
    @no_cache  
    def api_schema():
        """Get database schema as JSON"""
        try:
            schema_data = get_schema_documentation()
            
            if 'error' in schema_data:
                return jsonify({'success': False, 'error': schema_data['error']}), 500
            
            return jsonify({
                'success': True,
                'schema': schema_data,
                'generated_at': schema_data.get('generated_at'),
                'version': get_version()
            })
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/scan')
    @no_cache
    def api_scan_region():
        """
        Smart regional scanning endpoint - the heart of 'scan as you go'

        Query params:
            bbox: Bounding box as "south,west,north,east"
            zoom: Map zoom level
            layers: Comma-separated list (fires,air,ocean)
        """
        try:
            # Parse parameters
            bbox_str = request.args.get('bbox', '')
            zoom = int(request.args.get('zoom', 10))
            layers_str = request.args.get('layers', 'fires,air,ocean')

            if not bbox_str:
                return jsonify({'success': False, 'error': 'bbox parameter required'}), 400

            # Parse bbox: "south,west,north,east"
            try:
                parts = [float(x.strip()) for x in bbox_str.split(',')]
                if len(parts) != 4:
                    raise ValueError("bbox must have 4 coordinates")
                bbox = {
                    'south': parts[0],
                    'west': parts[1],
                    'north': parts[2],
                    'east': parts[3]
                }
            except (ValueError, IndexError) as e:
                return jsonify({'success': False, 'error': f'Invalid bbox format: {e}'}), 400

            layers = [l.strip() for l in layers_str.split(',') if l.strip()]

            # Get scanner instance
            scanner = get_scanner()

            # Check if region is cached
            cache_status = scanner.check_region_cached(bbox, zoom, layers)

            # If fully cached, return cached data
            if cache_status['cached']:
                data = scanner.get_cached_data(bbox, layers)
                return jsonify({
                    'success': True,
                    'cached': True,
                    'data': data,
                    'cache_status': cache_status,
                    'message': 'Data loaded from cache'
                })

            # Otherwise, we need to fetch fresh data for missing layers
            layers_to_fetch = cache_status['layers_needed']

            if layers_to_fetch:
                # Fetch fresh data from APIs
                fetcher = get_regional_fetcher()
                fetch_results = fetcher.fetch_region(bbox, layers_to_fetch)

                # Record this scan in the database
                total_records = fetch_results.get('total_records', 0)
                if total_records > 0:
                    scan_id = scanner.record_scan(
                        bbox, zoom, layers_to_fetch,
                        total_records, triggered_by='user_zoom'
                    )

            # Get all data (cached + newly fetched)
            data = scanner.get_cached_data(bbox, layers)

            return jsonify({
                'success': True,
                'cached': False,
                'partial_cache': len(cache_status['layers_available']) > 0,
                'data': data,
                'cache_status': cache_status,
                'fetch_results': fetch_results if layers_to_fetch else {},
                'message': f"Fetched fresh data for: {layers_to_fetch}. Total records: {fetch_results.get('total_records', 0) if layers_to_fetch else 0}"
            })

        except Exception as e:
            import traceback
            traceback.print_exc()
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/regions/stats')
    @no_cache
    def api_region_stats():
        """Get scanning statistics"""
        try:
            scanner = get_scanner()
            stats = scanner.get_scan_statistics()
            return jsonify({
                'success': True,
                'stats': stats
            })
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/scan-area', methods=['POST'])
    @no_cache
    def api_scan_area():
        """
        Simple on-demand area scanning endpoint
        Fetches fresh air quality data for a specific bounding box

        POST body:
            {
                "bbox": {"south": float, "west": float, "north": float, "east": float},
                "layers": ["air"]  // optional, defaults to air quality only for now
            }
        """
        try:
            from tasks.fetch_openaq_latest import fetch_openaq_latest

            data = request.get_json()
            if not data or 'bbox' not in data:
                return jsonify({'success': False, 'error': 'bbox required'}), 400

            bbox = data['bbox']

            # Validate bbox
            required_keys = ['south', 'west', 'north', 'east']
            if not all(k in bbox for k in required_keys):
                return jsonify({'success': False, 'error': 'bbox must have south, west, north, east'}), 400

            # Fetch air quality data for this area
            result = fetch_openaq_latest(limit=100, bbox=bbox)

            if result['success']:
                # Query the data we just fetched to return it
                new_stations = execute_query("""
                    SELECT location_lat as lat, location_lng as lng,
                           value as pm25, metadata
                    FROM metric_data
                    WHERE provider_key = 'openaq'
                    AND metric_name = 'air_quality_pm25'
                    AND location_lat BETWEEN %s AND %s
                    AND location_lng BETWEEN %s AND %s
                    AND timestamp > NOW() - INTERVAL '1 hour'
                    ORDER BY timestamp DESC
                    LIMIT 100
                """, (bbox['south'], bbox['north'], bbox['west'], bbox['east']))

                # Format for map display
                stations = []
                for s in (new_stations or []):
                    location = 'Unknown'
                    try:
                        if s.get('metadata'):
                            meta = json.loads(s['metadata']) if isinstance(s['metadata'], str) else s['metadata']
                            location = meta.get('station_name', 'Unknown')
                    except:
                        pass

                    stations.append({
                        'lat': float(s['lat']),
                        'lng': float(s['lng']),
                        'pm25': round(float(s['pm25']), 1),
                        'location': location
                    })

                return jsonify({
                    'success': True,
                    'message': result['message'],
                    'records_stored': result.get('records_stored', 0),
                    'stations': stations
                })
            else:
                return jsonify({
                    'success': False,
                    'error': result.get('message', 'Scan failed')
                }), 500

        except Exception as e:
            import traceback
            traceback.print_exc()
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.errorhandler(404)
    def not_found(error):
        return "Page not found", 404

    @app.errorhandler(500)
    def internal_error(error):
        return "Internal error", 500

    return app

# Helper Functions
def prepare_dashboard_data():
    """Prepare data for dashboard pages"""
    health_data = get_environmental_health_data()
    health_score = calculate_environmental_health_score(health_data)
    
    # Create smart metric values that handle display logic internally
    fire_data = {
        'count': create_metric_value(health_data['fires']['count'], 'fire_count'),
        'active_fires': create_metric_value(health_data['fires']['count'], 'fire_count'),  # Template expects active_fires
        'avg_brightness': create_metric_value(health_data['fires']['avg_brightness'], unit='K', decimal_places=1),
        'measurements': create_metric_value(health_data['fires']['count'], 'count'),
        'last_update': health_data['last_updated']
    }

    air_data = {
        'avg_pm25': create_metric_value(health_data['air_quality']['avg_pm25'], 'air_quality'),
        'measurements': create_metric_value(health_data['air_quality']['station_count'], 'count'),
        'last_update': health_data['last_updated']
    }

    # Use temperature if available, otherwise use water level as a metric
    ocean_temp = health_data['ocean_temperature']['avg_temp']
    ocean_water_level = health_data['ocean_temperature'].get('avg_water_level')

    ocean_data = {
        'avg_temp': create_metric_value(ocean_temp, 'ocean_temp') if ocean_temp else create_metric_value(ocean_water_level, unit='m', decimal_places=2),
        'measurements': create_metric_value(health_data['ocean_temperature']['station_count'], 'count'),
        'last_update': health_data['last_updated'],
        'has_temperature': ocean_temp is not None,
        'metric_name': 'Water Temperature' if ocean_temp else 'Water Level'
    }

    weather_data = {
        'avg_temp': create_metric_value(health_data['weather']['avg_temp'], 'temperature'),
        'avg_humidity': create_metric_value(health_data['weather']['avg_humidity'], unit='%', decimal_places=0),
        'avg_pressure': create_metric_value(None, unit=' hPa', decimal_places=1),  # Not implemented
        'avg_wind_speed': create_metric_value(None, unit=' km/h', decimal_places=1),  # Not implemented
        'city_count': create_metric_value(health_data['weather']['city_count'], 'count'),
        'alert_count': create_metric_value(None, 'count'),  # Not implemented
        'last_update': health_data['last_updated']
    }

    biodiversity_data = {
        'avg_observations': create_metric_value(health_data['biodiversity']['avg_observations'], 'count'),
        'avg_diversity': create_metric_value(
            (health_data['biodiversity']['avg_observations'] / 100) if (health_data['biodiversity']['avg_observations'] is not None and health_data['biodiversity']['avg_observations'] > 0) else None,
            unit='', decimal_places=1
        ),
        'total_observations': create_metric_value(
            (health_data['biodiversity']['avg_observations'] * health_data['biodiversity']['region_count']) if (health_data['biodiversity']['avg_observations'] is not None and health_data['biodiversity']['region_count'] is not None and health_data['biodiversity']['region_count'] > 0) else None,
            'count'
        ),
        'region_count': create_metric_value(health_data['biodiversity']['region_count'], 'count'),
        'last_update': health_data['last_updated']
    }
    
    return {
        'health_data': health_data,
        'health_score': health_score,
        'fire_data': fire_data,
        'air_data': air_data,
        'ocean_data': ocean_data,
        'weather_data': weather_data,
        'biodiversity_data': biodiversity_data
    }

def get_count(query):
    """Get a count from database safely"""
    result = execute_query(query)
    return result[0]['count'] if result and len(result) > 0 and result[0]['count'] is not None else 0

def get_provider_stats():
    """Get simplified provider statistics"""
    providers = {}
    provider_keys = ['nasa_firms', 'openaq', 'noaa_ocean', 'openweather', 'gbif', 'openmeteo', 'openmeteo_marine', 'ucdp', 'noaa_swpc']
    
    for key in provider_keys:
        stats = execute_query("""
            SELECT COUNT(*) as total_records, MAX(timestamp) as last_run
            FROM metric_data WHERE provider_key = %s
        """, (key,))
        
        if stats and len(stats) > 0:
            providers[key] = {
                'total_records': stats[0]['total_records'] or 0,
                'last_run': stats[0]['last_run'] or 'Never',
                'status': 'operational' if (stats[0]['total_records'] or 0) > 0 else 'no_data'
            }
        else:
            providers[key] = {
                'total_records': 0,
                'last_run': 'Never',
                'status': 'no_data'
            }
    
    return providers

def format_fire_data(fires):
    """
    Format fire data for map display

    Args:
        fires: List of fire records from database

    Returns:
        List[Dict]: Formatted fire data with numeric coordinates
    """
    from decimal import Decimal

    formatted = []
    for fire in fires:
        try:
            # Extract confidence from metadata
            confidence = 50  # Default if not available
            if fire.get('metadata'):
                metadata = fire['metadata']
                if isinstance(metadata, str):
                    import json
                    metadata = json.loads(metadata)
                if isinstance(metadata, dict):
                    # Confidence stored as 0-1 float, convert to percentage
                    conf_val = metadata.get('confidence', 0.5)
                    confidence = int(round(float(conf_val) * 100))

            formatted.append({
                'lat': float(fire['latitude']) if fire['latitude'] is not None else None,
                'lng': float(fire['longitude']) if fire['longitude'] is not None else None,
                'brightness': int(round(float(fire['brightness']))) if fire['brightness'] is not None else 0,
                'confidence': confidence,
                'acq_date': str(fire['acq_date'])
            })
        except (ValueError, TypeError) as e:
            print(f"⚠️ Error formatting fire data: {e}, fire={fire}")
            continue
    return formatted

def format_air_data(stations):
    """
    Format air quality data for map display

    Args:
        stations: List of air quality station records from database

    Returns:
        List[Dict]: Formatted air quality data with numeric coordinates and values
    """
    from decimal import Decimal

    formatted = []
    for station in stations:
        location = "Unknown Location"
        try:
            if station['metadata']:
                metadata = json.loads(station['metadata'])
                location = metadata.get('location', location)
        except:
            pass

        try:
            formatted.append({
                'lat': float(station['latitude']) if station['latitude'] is not None else None,
                'lng': float(station['longitude']) if station['longitude'] is not None else None,
                'pm25': round(float(station['value']), 1) if station['value'] is not None else None,
                'location': location
            })
        except (ValueError, TypeError) as e:
            print(f"⚠️ Error formatting air quality data: {e}, station={station}")
            continue

    return formatted

def format_ocean_data(stations):
    """
    Format ocean data for map display

    Args:
        stations: List of ocean station records from database

    Returns:
        List[Dict]: Formatted ocean data with numeric coordinates and values
    """
    from decimal import Decimal
    from datetime import datetime

    formatted = []
    for station in stations:
        name = "Ocean Station"
        try:
            if station['metadata']:
                metadata = json.loads(station['metadata'])
                name = metadata.get('station_name', name)
        except:
            pass

        # Format timestamp
        last_updated = "Unknown"
        if station.get('last_updated'):
            try:
                if isinstance(station['last_updated'], str):
                    last_updated = station['last_updated']
                else:
                    last_updated = station['last_updated'].strftime('%Y-%m-%d %H:%M UTC')
            except:
                pass

        try:
            formatted.append({
                'latitude': float(station['latitude']) if station['latitude'] is not None else None,
                'longitude': float(station['longitude']) if station['longitude'] is not None else None,
                'temperature': round(float(station['temperature']), 1) if station.get('temperature') is not None else None,
                'water_level': round(float(station['water_level']), 2) if station.get('water_level') is not None else None,
                'last_updated': last_updated,
                'name': name
            })
        except (ValueError, TypeError) as e:
            print(f"⚠️ Error formatting ocean data: {e}, station={station}")
            continue

    return formatted

def format_conflict_data(conflicts):
    """
    Format conflict data for map display

    Args:
        conflicts: List of conflict event records from database

    Returns:
        List[Dict]: Formatted conflict data with coordinates and metadata
    """
    formatted = []
    for conflict in conflicts:
        try:
            metadata = {}
            if conflict.get('metadata'):
                if isinstance(conflict['metadata'], str):
                    metadata = json.loads(conflict['metadata'])
                else:
                    metadata = conflict['metadata']

            formatted.append({
                'latitude': float(conflict['latitude']) if conflict['latitude'] is not None else None,
                'longitude': float(conflict['longitude']) if conflict['longitude'] is not None else None,
                'deaths': int(conflict.get('deaths', 0) or 0),
                'location': f"{metadata.get('region', 'Unknown')}, {metadata.get('country', '')}",
                'conflict_name': metadata.get('conflict_name', 'Unknown Conflict'),
                'violence_type': metadata.get('violence_type', 'unknown'),
                'side_a': metadata.get('side_a', ''),
                'side_b': metadata.get('side_b', ''),
                'date': str(conflict.get('timestamp', ''))[:10]
            })
        except (ValueError, TypeError) as e:
            print(f"⚠️ Error formatting conflict data: {e}")
            continue

    return formatted

def format_biodiversity_data(biodiversity):
    """
    Format biodiversity data for map display

    Args:
        biodiversity: List of biodiversity records from database

    Returns:
        List[Dict]: Formatted biodiversity data with coordinates and metadata
    """
    formatted = []
    for bio in biodiversity:
        try:
            metadata = {}
            if bio.get('metadata'):
                if isinstance(bio['metadata'], str):
                    metadata = json.loads(bio['metadata'])
                else:
                    metadata = bio['metadata']

            formatted.append({
                'latitude': float(bio['latitude']) if bio['latitude'] is not None else None,
                'longitude': float(bio['longitude']) if bio['longitude'] is not None else None,
                'observations': int(bio.get('observations', 0) or 0),
                'location': metadata.get('region_name', 'Unknown'),
                'ecosystem': metadata.get('ecosystem', 'unknown'),
                'unique_species': metadata.get('unique_species', 0),
                'region': metadata.get('region_name', '')
            })
        except (ValueError, TypeError) as e:
            print(f"⚠️ Error formatting biodiversity data: {e}")
            continue

    return formatted

def format_aurora_data(aurora_points, kp_data):
    """
    Format aurora forecast data for map display

    Args:
        aurora_points: List of aurora forecast points from database
        kp_data: Current Kp index data (can be None)

    Returns:
        Dict: Formatted aurora data with points and Kp index
    """
    formatted_points = []
    for point in aurora_points:
        try:
            formatted_points.append({
                'latitude': float(point['latitude']) if point['latitude'] is not None else None,
                'longitude': float(point['longitude']) if point['longitude'] is not None else None,
                'intensity': float(point.get('intensity', 0) or 0)
            })
        except (ValueError, TypeError) as e:
            print(f"⚠️ Error formatting aurora data: {e}")
            continue

    # Parse Kp metadata
    kp_info = None
    if kp_data:
        try:
            metadata = {}
            if kp_data.get('metadata'):
                if isinstance(kp_data['metadata'], str):
                    metadata = json.loads(kp_data['metadata'])
                else:
                    metadata = kp_data['metadata']

            kp_value = float(kp_data.get('kp', 0))
            kp_info = {
                'value': kp_value,
                'status': get_kp_status(kp_value),
                'timestamp': str(kp_data.get('timestamp', ''))
            }
        except (ValueError, TypeError):
            pass

    return {
        'points': formatted_points,
        'kp_index': kp_info,
        'point_count': len(formatted_points)
    }

def get_kp_status(kp: float) -> str:
    """Get human-readable Kp status"""
    if kp >= 8:
        return 'Extreme Storm'
    elif kp >= 7:
        return 'Severe Storm'
    elif kp >= 6:
        return 'Strong Storm'
    elif kp >= 5:
        return 'Minor Storm'
    elif kp >= 4:
        return 'Active'
    elif kp >= 3:
        return 'Unsettled'
    else:
        return 'Quiet'

def get_environmental_health_data():
    """Get current environmental health data from database"""
    try:
        # Fire data
        fire_data = execute_query("""
            SELECT COUNT(*) as fire_count, AVG(value) as avg_brightness
            FROM metric_data
            WHERE provider_key = 'nasa_firms'
            AND timestamp >= NOW() - INTERVAL '7 days'
        """)
        
        # Air quality data
        air_data = execute_query("""
            SELECT AVG(value) as avg_pm25, COUNT(*) as station_count
            FROM metric_data 
            WHERE provider_key = 'openaq' 
            AND metric_name = 'air_quality_pm25'
            AND timestamp >= NOW() - INTERVAL '7 days'
        """)
        
        # Ocean data - using Open-Meteo for global SST coverage
        ocean_data = execute_query("""
            SELECT
                AVG(value) as avg_temp,
                NULL as avg_water_level,
                COUNT(DISTINCT CONCAT(location_lat, ',', location_lng)) as temp_station_count,
                0 as water_level_station_count
            FROM metric_data
            WHERE provider_key = 'openmeteo_marine'
            AND metric_name = 'sea_surface_temperature'
            AND timestamp >= NOW() - INTERVAL '7 days'
        """)
        
        # Weather data
        weather_data = execute_query("""
            SELECT 
                AVG(CASE WHEN metric_name = 'temperature' THEN value END) as avg_temp,
                AVG(CASE WHEN metric_name = 'humidity' THEN value END) as avg_humidity,
                COUNT(DISTINCT CASE WHEN metric_name = 'temperature' THEN CONCAT(location_lat, ',', location_lng) END) as city_count
            FROM metric_data
            WHERE provider_key = 'openweather'
            AND timestamp >= NOW() - INTERVAL '24 hours'
        """)
        
        # Biodiversity data
        biodiversity_data = execute_query("""
            SELECT 
                AVG(CASE WHEN metric_name = 'species_observations' THEN value END) as avg_observations,
                COUNT(DISTINCT CASE WHEN metric_name = 'species_observations' THEN CONCAT(location_lat, ',', location_lng) END) as region_count
            FROM metric_data
            WHERE provider_key = 'gbif'
            AND timestamp >= NOW() - INTERVAL '7 days'
        """)
        
        return {
            'fires': {
                'count': get_nullable_count(fire_data, 'fire_count'),
                'avg_brightness': format_nullable_value(fire_data[0]['avg_brightness'] if fire_data and len(fire_data) > 0 else None, 1)
            },
            'air_quality': {
                'avg_pm25': format_nullable_value(air_data[0]['avg_pm25'] if air_data and len(air_data) > 0 else None, 2),
                'station_count': get_nullable_count(air_data, 'station_count')
            },
            'ocean_temperature': {
                'avg_temp': format_nullable_value(ocean_data[0]['avg_temp'] if ocean_data and len(ocean_data) > 0 else None, 1),
                'avg_water_level': format_nullable_value(ocean_data[0]['avg_water_level'] if ocean_data and len(ocean_data) > 0 else None, 2),
                'station_count': get_nullable_count(ocean_data, 'temp_station_count') or get_nullable_count(ocean_data, 'water_level_station_count')
            },
            'weather': {
                'avg_temp': format_nullable_value(weather_data[0]['avg_temp'] if weather_data and len(weather_data) > 0 else None, 1),
                'avg_humidity': format_nullable_value(weather_data[0]['avg_humidity'] if weather_data and len(weather_data) > 0 else None, 1),
                'city_count': get_nullable_count(weather_data, 'city_count')
            },
            'biodiversity': {
                'avg_observations': format_nullable_value(biodiversity_data[0]['avg_observations'] if biodiversity_data and len(biodiversity_data) > 0 else None, 1),
                'region_count': get_nullable_count(biodiversity_data, 'region_count')
            },
            'last_updated': datetime.utcnow().isoformat()
        }
    except Exception as e:
        # Return NULL data on error - no fake zeros
        return {
            'fires': {'count': None, 'avg_brightness': None},
            'air_quality': {'avg_pm25': None, 'station_count': None},
            'ocean_temperature': {'avg_temp': None, 'station_count': None},
            'weather': {'avg_temp': None, 'avg_humidity': None, 'city_count': None},
            'biodiversity': {'avg_observations': None, 'region_count': None},
            'last_updated': datetime.utcnow().isoformat(),
            'error': str(e)
        }

def calculate_environmental_health_score(health_data):
    """Calculate environmental health score (0-100) - returns None if insufficient data"""
    # Check if we have enough data to calculate a meaningful score
    fire_count = health_data['fires']['count']
    pm25 = health_data['air_quality']['avg_pm25']
    ocean_temp = health_data['ocean_temperature']['avg_temp']

    # If all critical metrics are NULL, we can't calculate a health score
    data_points = [x for x in [fire_count, pm25, ocean_temp] if x is not None]
    if len(data_points) == 0:
        return {
            'score': None,
            'status': 'NO_DATA',
            'color': '#6c757d'  # Gray for no data
        }

    score = 100  # Start with perfect score

    # Fire impact (up to -25 points) - only if data available
    if fire_count is not None:
        if fire_count > 1000:
            score -= 25
        elif fire_count > 500:
            score -= 15
        elif fire_count > 100:
            score -= 8

    # Air quality impact (up to -30 points) - only if data available
    if pm25 is not None:
        if pm25 > 75:  # Hazardous
            score -= 30
        elif pm25 > 55:  # Very unhealthy
            score -= 20
        elif pm25 > 35:  # Unhealthy
            score -= 12
        elif pm25 > 15:  # Moderate
            score -= 5

    # Ocean temperature impact (up to -15 points) - only if data available
    if ocean_temp is not None:
        if ocean_temp > 25:  # Very warm
            score -= 15
        elif ocean_temp > 23:  # Warm
            score -= 8
        elif ocean_temp < 15:  # Very cold
            score -= 10
        elif ocean_temp < 18:  # Cold
            score -= 5

    # Ensure score stays within bounds
    score = max(0, min(100, score))

    # Determine status - add "LIMITED_DATA" status if we're missing some metrics
    data_coverage = len(data_points) / 3  # 3 critical metrics
    if data_coverage < 0.67:  # Less than 2 out of 3 metrics
        status_suffix = "_LIMITED_DATA"
    else:
        status_suffix = ""

    if score >= 80:
        status = 'Excellent' + status_suffix
        color = '#28a745'
    elif score >= 60:
        status = 'Good' + status_suffix
        color = '#33a474'
    elif score >= 40:
        status = 'Moderate' + status_suffix
        color = '#ffc107'
    elif score >= 20:
        status = 'Poor' + status_suffix
        color = '#fd7e14'
    else:
        status = 'Critical' + status_suffix
        color = '#dc3545'

    return {
        'score': score,
        'status': status,
        'color': color,
        'data_coverage': round(data_coverage * 100, 0)
    }

def get_air_quality_status(pm25):
    """Get air quality status based on PM2.5"""
    if pm25 is None:
        return 'No Data'
    elif pm25 > 75:
        return 'Hazardous'
    elif pm25 > 55:
        return 'Very Unhealthy'
    elif pm25 > 35:
        return 'Unhealthy'
    elif pm25 > 15:
        return 'Moderate'
    else:
        return 'Good'

def get_ocean_status(temp):
    """Get ocean status based on temperature"""
    if temp is None:
        return 'No Data'
    elif temp > 25:
        return 'Warm'
    elif temp < 15:
        return 'Cool'
    else:
        return 'Normal'

# Data integrity helpers
def format_nullable_value(value, decimal_places=None):
    """
    Properly handle nullable values for strict data display
    Returns None for NULL/empty values, rounded numeric value for real data
    """
    from decimal import Decimal

    if value is None:
        return None
    if isinstance(value, (int, float, Decimal)) and value == 0:
        # Only return 0 if it's explicitly zero from database, not NULL
        return 0
    if isinstance(value, (int, float, Decimal)):
        # Convert to float first to handle Decimal types from PostgreSQL
        float_value = float(value)
        if decimal_places is not None:
            # Return a rounded float
            return round(float_value, decimal_places)
        return float_value
    return value

def get_nullable_count(query_result, field_name):
    """Get count that properly handles NULL vs 0"""
    if not query_result or len(query_result) == 0:
        return None
    value = query_result[0].get(field_name)
    return value if value is not None else None

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000) 
