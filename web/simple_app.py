import os
import sqlite3
from datetime import datetime, timedelta
from flask import Flask, render_template, jsonify
from database.db import execute_query, init_database

def create_app():
    """Create and configure the Flask application"""
    app = Flask(__name__)
    app.secret_key = os.environ.get('SECRET_KEY', 'eco-watch-terra-scan-2024')
    
    # Initialize database
    init_database()
    
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
