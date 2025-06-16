#!/usr/bin/env python3
"""
TERRASCAN - Environmental Health Dashboard
Clean, maintainable Flask application
"""

import os
import json
from datetime import datetime
from flask import Flask, render_template, jsonify, make_response
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import database and utilities
from database.db import init_database, execute_query
from tasks.runner import TaskRunner
from utils import get_version, register_template_filters

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
        """Homepage with environmental dashboard"""
        try:
            data = prepare_dashboard_data()
            return render_template('index.html', **data)
        except Exception as e:
            return f"Error: {e}", 500

    @app.route('/dashboard')
    @no_cache  
    def dashboard():
        """Dashboard page (same as index)"""
        try:
            data = prepare_dashboard_data()
            return render_template('dashboard.html', **data)
        except Exception as e:
            return f"Error: {e}", 500

    @app.route('/map')
    @no_cache
    def map_view():
        """Interactive map page"""
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
            # Get tasks and recent runs
            all_tasks = execute_query("""
                SELECT id, name, description, command, active, cron_schedule, 
                       created_date, updated_date, parameters
                FROM task ORDER BY name
            """)
            
            recent_runs = execute_query("""
                SELECT tl.*, t.name as task_name, t.description as task_description
                FROM task_log tl 
                JOIN task t ON tl.task_id = t.id 
                ORDER BY tl.started_at DESC LIMIT 50
            """)
            
            # Simple stats
            stats = {
                'total_tasks': len(all_tasks),
                'active_tasks': len([t for t in all_tasks if t['active']]),
                'recent_runs': len(recent_runs)
            }
            
            return render_template('tasks.html',
                                 tasks=all_tasks,
                                 recent_runs=recent_runs,
                                 stats=stats)
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
            
            return render_template('system.html',
                                 system_status=system_status,
                                 providers=providers,
                                 recent_runs=recent_runs,
                                 data_breakdown=data_breakdown,
                                 simulation_mode=False,
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
                       value as brightness, DATE(timestamp) as acq_date
                FROM metric_data 
                WHERE provider_key = 'nasa_firms' 
                AND timestamp > NOW() - INTERVAL '24 hours'
                AND location_lat IS NOT NULL AND location_lng IS NOT NULL
                AND value > 300
                ORDER BY timestamp DESC LIMIT 500
            """)
            
            # Get air quality data
            air_quality = execute_query("""
                SELECT location_lat as latitude, location_lng as longitude,
                       AVG(value) as value, MAX(metadata) as metadata
                FROM metric_data 
                WHERE provider_key = 'openaq' 
                AND metric_name = 'air_quality_pm25'
                AND timestamp > NOW() - INTERVAL '7 days'
                AND location_lat IS NOT NULL AND location_lng IS NOT NULL
                GROUP BY location_lat, location_lng
                ORDER BY value DESC LIMIT 200
            """)
            
            # Get ocean data
            ocean_stations = execute_query("""
                SELECT location_lat as latitude, location_lng as longitude,
                       AVG(CASE WHEN metric_name = 'water_temperature' THEN value END) as temperature,
                       MAX(metadata) as metadata
                FROM metric_data 
                WHERE provider_key = 'noaa_ocean' 
                AND timestamp > NOW() - INTERVAL '7 days'
                AND location_lat IS NOT NULL AND location_lng IS NOT NULL
                GROUP BY location_lat, location_lng LIMIT 20
            """)
            
            return jsonify({
                'success': True,
                'fires': format_fire_data(fires or []),
                'air_quality': format_air_data(air_quality or []),
                'ocean': format_ocean_data(ocean_stations or [])
            })
            
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})

    @app.route('/api/refresh')
    def api_refresh():
        """Refresh environmental data"""
        try:
            runner = TaskRunner()
            
            # Run key tasks
            tasks = ['nasa_fires_global', 'openaq_latest', 'noaa_ocean_water_level']
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
                SELECT id, name, description, command, active, cron_schedule, 
                       created_date, updated_date, parameters
                FROM task ORDER BY name
            """)
            return jsonify({'success': True, 'tasks': tasks})
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
    
    # Prepare individual data sections
    fire_data = {
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
        'city_count': health_data['weather']['city_count'],
        'last_update': health_data['last_updated']
    }
    
    biodiversity_data = {
        'avg_observations': health_data['biodiversity']['avg_observations'],
        'region_count': health_data['biodiversity']['region_count'],
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
    provider_keys = ['nasa_firms', 'openaq', 'noaa_ocean', 'openweather', 'gbif']
    
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
    """Format fire data for map"""
    return [{
        'latitude': fire['latitude'],
        'longitude': fire['longitude'],
        'brightness': fire['brightness'],
        'confidence': 75,  # Default confidence
        'acq_date': fire['acq_date']
    } for fire in fires]

def format_air_data(stations):
    """Format air quality data for map"""
    formatted = []
    for station in stations:
        location = "Unknown Location"
        try:
            if station['metadata']:
                metadata = json.loads(station['metadata'])
                location = metadata.get('location', location)
        except:
            pass
        
        formatted.append({
            'latitude': station['latitude'],
            'longitude': station['longitude'],
            'value': round(station['value'], 1),
            'location': location
        })
    
    return formatted

def format_ocean_data(stations):
    """Format ocean data for map"""
    formatted = []
    for station in stations:
        name = "Ocean Station"
        try:
            if station['metadata']:
                metadata = json.loads(station['metadata'])
                name = metadata.get('station_name', name)
        except:
            pass
        
        formatted.append({
            'latitude': station['latitude'],
            'longitude': station['longitude'],
            'temperature': round(station['temperature'], 1) if station['temperature'] else 20.0,
            'name': name
        })
    
    return formatted

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
        
        # Ocean data
        ocean_data = execute_query("""
            SELECT AVG(value) as avg_temp, COUNT(*) as station_count
            FROM metric_data
            WHERE provider_key = 'noaa_ocean'
            AND metric_name = 'water_temperature'
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
                'count': fire_data[0]['fire_count'] if fire_data and len(fire_data) > 0 else 0,
                'avg_brightness': round(fire_data[0]['avg_brightness'] or 0, 1) if fire_data and len(fire_data) > 0 else 0
            },
            'air_quality': {
                'avg_pm25': round(air_data[0]['avg_pm25'] or 0, 1) if air_data and len(air_data) > 0 else 0,
                'station_count': air_data[0]['station_count'] if air_data and len(air_data) > 0 else 0
            },
            'ocean_temperature': {
                'avg_temp': round(ocean_data[0]['avg_temp'] or 0, 1) if ocean_data and len(ocean_data) > 0 else 0,
                'station_count': ocean_data[0]['station_count'] if ocean_data and len(ocean_data) > 0 else 0
            },
            'weather': {
                'avg_temp': round(weather_data[0]['avg_temp'] or 0, 1) if weather_data and len(weather_data) > 0 else 0,
                'avg_humidity': round(weather_data[0]['avg_humidity'] or 0, 1) if weather_data and len(weather_data) > 0 else 0,
                'city_count': weather_data[0]['city_count'] if weather_data and len(weather_data) > 0 else 0
            },
            'biodiversity': {
                'avg_observations': round(biodiversity_data[0]['avg_observations'] or 0, 1) if biodiversity_data and len(biodiversity_data) > 0 else 0,
                'region_count': biodiversity_data[0]['region_count'] if biodiversity_data and len(biodiversity_data) > 0 else 0
            },
            'last_updated': datetime.utcnow().isoformat()
        }
    except Exception as e:
        # Return empty data on error
        return {
            'fires': {'count': 0, 'avg_brightness': 0},
            'air_quality': {'avg_pm25': 0, 'station_count': 0},
            'ocean_temperature': {'avg_temp': 0, 'station_count': 0},
            'weather': {'avg_temp': 0, 'avg_humidity': 0, 'city_count': 0},
            'biodiversity': {'avg_observations': 0, 'region_count': 0},
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
        score -= 15
    elif fire_count > 100:
        score -= 8
    
    # Air quality impact (up to -30 points)  
    pm25 = health_data['air_quality']['avg_pm25']
    if pm25 > 75:  # Hazardous
        score -= 30
    elif pm25 > 55:  # Very unhealthy
        score -= 20
    elif pm25 > 35:  # Unhealthy
        score -= 12
    elif pm25 > 15:  # Moderate
        score -= 5
    
    # Ocean temperature impact (up to -15 points)
    ocean_temp = health_data['ocean_temperature']['avg_temp']
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
    
    # Determine status
    if score >= 80:
        status = 'EXCELLENT'
        color = '#28a745'
    elif score >= 60:
        status = 'GOOD'
        color = '#33a474'
    elif score >= 40:
        status = 'MODERATE'
        color = '#ffc107'
    elif score >= 20:
        status = 'POOR'
        color = '#fd7e14'
    else:
        status = 'CRITICAL'
        color = '#dc3545'
    
    return {
        'score': score,
        'status': status,
        'color': color
    }

def get_air_quality_status(pm25):
    """Get air quality status based on PM2.5"""
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
