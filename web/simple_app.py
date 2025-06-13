import os
import sqlite3
from datetime import datetime, timedelta
from flask import Flask, render_template, jsonify
from database.db import execute_query, init_database, populate_sample_data

def create_app():
    """Create and configure the Flask application"""
    app = Flask(__name__)
    app.secret_key = os.environ.get('SECRET_KEY', 'eco-watch-terra-scan-2024')
    
    # Initialize database and populate sample data if needed
    init_database()
    populate_sample_data()
    
    @app.route('/')
    def dashboard():
        """Main environmental health dashboard"""
        try:
            # Get environmental health data
            health_data = get_environmental_health_data()
            
            # Calculate environmental health score
            health_score = calculate_environmental_health_score(health_data)
            
            # Transform data to match template expectations
            fire_data = {
                'active_fires': health_data['fires']['count'],
                'avg_brightness': health_data['fires']['avg_brightness'],
                'status': 'ACTIVE MONITORING' if health_data['fires']['count'] > 0 else 'NO ACTIVITY',
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
            return f"Dashboard error: {str(e)}", 500
    
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
    
    @app.route('/about')
    def about():
        """About page with project information"""
        return render_template('about.html')
    
    @app.route('/map')
    def map_view():
        """Interactive world map with environmental data layers"""
        try:
            # Get current environmental data for health score widget
            health_data = get_environmental_health_data()
            health_score = calculate_environmental_health_score(health_data)
            
            return render_template('map.html',
                                 health_data=health_data,
                                 health_score=health_score)
        except Exception as e:
            return f"Map error: {str(e)}", 500
    
    @app.route('/system')
    def system():
        """System status and data provider information"""
        try:
            # Get system statistics
            total_records = execute_query("SELECT COUNT(*) as count FROM metric_data")[0]['count'] or 0
            
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
            
            system_status = {
                'total_records': total_records,
                'version': '2.2.1',
                'database_size': f"{total_records:,} records"
            }
            
            return render_template('system.html',
                                 system_status=system_status,
                                 providers=providers)
        except Exception as e:
            return f"System error: {str(e)}", 500
    
    return app

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
    app.run(debug=True) 
