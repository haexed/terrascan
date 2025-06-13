#!/usr/bin/env python3
"""
ECO WATCH TERRA SCAN
Simple environmental health dashboard
"""

import sys
import os
import json
from datetime import datetime, timedelta
from flask import Flask, render_template, jsonify, make_response
from dotenv import load_dotenv
import sqlite3
from database.db import execute_query

# Load environment variables
load_dotenv()

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from database.db import init_database, execute_query
from tasks.runner import TaskRunner
from version import get_version

def create_app():
    """Create and configure the Flask application"""
    app = Flask(__name__, 
                static_folder='static',
                static_url_path='/static')
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'eco-watch-terra-scan-2024')
    
    # Initialize database on startup
    init_database()
    
    # Add version to all templates
    @app.context_processor
    def inject_version():
        return {'version': get_version()}

# Cache-busting decorator for main pages
def no_cache(f):
    """Decorator to prevent browser caching of dynamic content"""
    def decorated_function(*args, **kwargs):
        response = make_response(f(*args, **kwargs))
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
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
        
        response = make_response(render_template('index.html',
                                               health_data=health_data,
                                               health_score=health_score))
        
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
        
        return render_template('dashboard.html', 
                             health_data=health_data,
                             health_score=health_score)
                             
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

@app.route('/system')
@no_cache
def system():
    """TERRASCAN - System status and data provider information"""
    try:
        # Get system statistics
        total_records = execute_query("SELECT COUNT(*) as count FROM metric_data")[0]['count'] or 0
        active_tasks = execute_query("SELECT COUNT(*) as count FROM task WHERE active = 1")[0]['count'] or 0
        recent_runs_count = execute_query("SELECT COUNT(*) as count FROM task_log WHERE started_at > datetime('now', '-24 hours')")[0]['count'] or 0
        
        system_status = {
            'total_records': total_records,
            'active_tasks': active_tasks,
            'recent_runs': recent_runs_count
        }
        
        # Get provider statistics
        providers = {}
        
        # NASA FIRMS stats
        nasa_stats = execute_query("""
            SELECT COUNT(*) as total_records, MAX(timestamp) as last_run
            FROM metric_data
            WHERE provider_key = 'nasa_firms'
        """)[0]
        providers['nasa_firms'] = {
            'total_records': nasa_stats['total_records'] or 0,
            'last_run': nasa_stats['last_run'] or 'Never',
            'status': 'operational' if (nasa_stats['total_records'] or 0) > 0 else 'no_data'
        }
        
        # OpenAQ stats
        openaq_stats = execute_query("""
            SELECT COUNT(*) as total_records, MAX(timestamp) as last_run
            FROM metric_data 
            WHERE provider_key = 'openaq'
        """)[0]
        providers['openaq'] = {
            'total_records': openaq_stats['total_records'] or 0,
            'last_run': openaq_stats['last_run'] or 'Never',
            'status': 'operational' if (openaq_stats['total_records'] or 0) > 0 else 'no_data'
        }
        
        # NOAA Ocean stats
        noaa_stats = execute_query("""
            SELECT COUNT(*) as total_records, MAX(timestamp) as last_run
            FROM metric_data
            WHERE provider_key = 'noaa_ocean'
        """)[0]
        providers['noaa_ocean'] = {
            'total_records': noaa_stats['total_records'] or 0,
            'last_run': noaa_stats['last_run'] or 'Never',
            'status': 'operational' if (noaa_stats['total_records'] or 0) > 0 else 'no_data'
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
        
        # Get database size
        import os
        try:
            db_path = os.path.join(os.path.dirname(__file__), '..', 'database', 'terrascan.db')
            if os.path.exists(db_path):
                size_bytes = os.path.getsize(db_path)
                database_size = f"{size_bytes / (1024*1024):.1f} MB" if size_bytes else "0.0 MB"
            else:
                database_size = "Unknown"
        except Exception as e:
            database_size = f"Error: {e}"
        
        # Check if simulation mode is enabled
        from database.config_manager import get_system_config
        simulation_mode = get_system_config('simulation_mode', True)
        
        return render_template('system.html',
                             system_status=system_status,
                             providers=providers,
                             recent_runs=recent_runs,
                             data_breakdown=data_breakdown,
                             database_size=database_size,
                             simulation_mode=simulation_mode)
                             
    except Exception as e:
        return f"TERRASCAN System Error: {e}", 500

def get_environmental_health_data():
    """Get current environmental health data from database"""
    try:
        # Get recent fire data (last 7 days) - using existing metric_data table
        fire_data = execute_query("""
            SELECT COUNT(*) as fire_count, AVG(value) as avg_brightness
            FROM metric_data 
            WHERE provider_key = 'nasa_firms' 
            AND timestamp >= datetime('now', '-7 days')
        """)
        
        # Get recent air quality data (last 7 days)
        air_data = execute_query("""
            SELECT AVG(value) as avg_pm25, COUNT(*) as station_count
            FROM metric_data 
            WHERE provider_key = 'openaq' 
            AND metric_name = 'air_quality_pm25'
            AND timestamp >= datetime('now', '-7 days')
        """)
        
        # Get recent ocean temperature data (last 7 days)  
        ocean_data = execute_query("""
            SELECT AVG(value) as avg_temp, COUNT(*) as station_count
            FROM metric_data
            WHERE provider_key = 'noaa_ocean'
            AND metric_name = 'water_temperature'
            AND timestamp >= datetime('now', '-7 days')
        """)
        
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
            'last_updated': datetime.utcnow().isoformat()
        }
    except Exception as e:
        # Return empty data on error
        return {
            'fires': {'count': 0, 'avg_brightness': 0},
            'air_quality': {'avg_pm25': 0, 'station_count': 0},
            'ocean_temperature': {'avg_temp': 0, 'station_count': 0},
            'last_updated': datetime.utcnow().isoformat(),
            'error': str(e)
        }

def calculate_environmental_health_score(health_data):
    """Calculate environmental health score (0-100)"""
    score = 100  # Start with perfect score
    
    # Fire impact (up to -30 points)
    fire_count = health_data['fires']['count']
    if fire_count > 1000:
        score -= 30
    elif fire_count > 500:
        score -= 20
    elif fire_count > 100:
        score -= 10
    
    # Air quality impact (up to -40 points)  
    pm25 = health_data['air_quality']['avg_pm25']
    if pm25 > 75:  # Hazardous
        score -= 40
    elif pm25 > 55:  # Very unhealthy
        score -= 30
    elif pm25 > 35:  # Unhealthy
        score -= 20
    elif pm25 > 15:  # Moderate
        score -= 10
    
    # Ocean temperature impact (up to -20 points)
    ocean_temp = health_data['ocean_temperature']['avg_temp']
    if ocean_temp > 25:  # Very warm
        score -= 20
    elif ocean_temp > 23:  # Warm
        score -= 10
    elif ocean_temp < 15:  # Very cold
        score -= 15
    elif ocean_temp < 18:  # Cold
        score -= 5
    
    # Ensure score stays within bounds
    score = max(0, min(100, score))
    
    # Determine status based on score
    if score >= 80:
        status = 'EXCELLENT'
        color = '#28a745'  # Green
    elif score >= 60:
        status = 'GOOD'
        color = '#33a474'  # Deep green
    elif score >= 40:
        status = 'MODERATE'
        color = '#ffc107'  # Yellow
    elif score >= 20:
        status = 'POOR'
        color = '#fd7e14'  # Orange
    else:
        status = 'CRITICAL'
        color = '#dc3545'  # Red
    
    return {
        'score': score,
        'status': status,
        'color': color
    }

@app.route('/api/map-data')
@no_cache
def api_map_data():
    """API endpoint to get environmental data for map visualization"""
    try:
        # Get fire data with coordinates
        fires = execute_query("""
            SELECT location_lat as latitude, location_lng as longitude,
                   value as brightness, 
                   CAST(SUBSTR(metadata, INSTR(metadata, '"confidence":') + 13, 2) AS INTEGER) as confidence,
                   DATE(timestamp) as acq_date
            FROM metric_data 
            WHERE provider_key = 'nasa_firms' 
            AND timestamp > datetime('now', '-24 hours')
            AND location_lat IS NOT NULL 
            AND location_lng IS NOT NULL
            AND value > 300
            ORDER BY timestamp DESC
            LIMIT 500
        """)
        
        # Get air quality data with coordinates
        air_quality = execute_query("""
            SELECT location_lat as latitude, location_lng as longitude,
                   AVG(value) as value,
                   metadata,
                   MAX(timestamp) as last_updated
            FROM metric_data 
            WHERE provider_key = 'openaq' 
            AND metric_name = 'air_quality_pm25'
            AND timestamp > datetime('now', '-7 days')
            AND location_lat IS NOT NULL 
            AND location_lng IS NOT NULL
            GROUP BY location_lat, location_lng
            ORDER BY value DESC
            LIMIT 200
        """)
        
        # Get ocean data with coordinates
        ocean_stations = execute_query("""
            SELECT location_lat as latitude, location_lng as longitude,
                   AVG(CASE WHEN metric_name = 'water_temperature' THEN value END) as temperature,
                   AVG(CASE WHEN metric_name = 'water_level' THEN value END) as water_level,
                   metadata,
                   MAX(timestamp) as last_updated
                FROM metric_data 
            WHERE provider_key = 'noaa_ocean' 
            AND date(timestamp) > date('now', '-7 days')
            AND location_lat IS NOT NULL 
            AND location_lng IS NOT NULL
            GROUP BY location_lat, location_lng
            LIMIT 20
        """)
        
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

@app.route('/health')
def health_check():
    """Simple health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat()
    })

@app.errorhandler(404)
def not_found(error):
    return "ECO WATCH TERRA SCAN - Page not found", 404

@app.errorhandler(500)
def internal_error(error):
    return "ECO WATCH TERRA SCAN - Internal error", 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 
