#!/usr/bin/env python3
"""
ECO WATCH TERRA SCAN
Simple environmental health dashboard
"""

import sys
import os
import json
from datetime import datetime, timedelta
from flask import Flask, render_template, jsonify
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from database.db import init_database, execute_query
from tasks.runner import TaskRunner
from version import get_version

# Create Flask app
app = Flask(__name__, 
            static_folder='static',
            static_url_path='/static')
app.config['SECRET_KEY'] = 'eco-watch-terra-scan'

# Initialize database on startup
init_database()

# Add version to all templates
@app.context_processor
def inject_version():
    return {'version': get_version()}

@app.route('/')
def dashboard():
    """ECO WATCH TERRA SCAN - Single dashboard showing environmental health"""
    try:
        # Get current environmental data
        fire_data = get_fire_status()
        air_data = get_air_quality_status()
        ocean_data = get_ocean_status()
        
        # Calculate overall environmental health score
        health_score = calculate_environmental_health(fire_data, air_data, ocean_data)
        
        return render_template('dashboard.html',
                             fire_data=fire_data,
                             air_data=air_data,
                             ocean_data=ocean_data,
                             health_score=health_score)
                             
    except Exception as e:
        return f"ECO WATCH Error: {e}", 500

def get_fire_status():
    """Get current fire situation"""
    try:
        # Get latest fire data from NASA FIRMS
        fires = execute_query("""
            SELECT COUNT(*) as active_fires,
                   AVG(value) as avg_brightness,
                   MAX(timestamp) as last_update
            FROM metric_data 
            WHERE provider_key = 'nasa_firms' 
            AND timestamp > datetime('now', '-24 hours')
        """)
        
        # Get recent fire locations for map
        fire_locations = execute_query("""
            SELECT location_lat, location_lng, value as brightness,
                   timestamp, metadata
            FROM metric_data 
            WHERE provider_key = 'nasa_firms' 
            AND timestamp > datetime('now', '-12 hours')
            AND location_lat IS NOT NULL
            ORDER BY timestamp DESC
            LIMIT 100
        """)
        
        if fires and fires[0]['active_fires'] > 0:
            status = "⚠️ ACTIVE" if fires[0]['active_fires'] > 50 else "🔥 MONITORING"
        else:
            status = "✅ QUIET"
        
        return {
            'status': status,
            'active_fires': fires[0]['active_fires'] if fires else 0,
            'avg_brightness': round(fires[0]['avg_brightness'], 1) if fires and fires[0]['avg_brightness'] else 0,
            'last_update': fires[0]['last_update'] if fires else 'Never',
            'locations': fire_locations
        }
    except Exception as e:
        return {
            'status': '❌ ERROR',
            'active_fires': 0,
            'avg_brightness': 0,
            'last_update': 'Error',
            'locations': [],
            'error': str(e)
        }

def get_air_quality_status():
    """Get current air quality"""
    try:
        # Get latest air quality data from OpenAQ
        air_quality = execute_query("""
            SELECT AVG(value) as avg_pm25,
                   COUNT(*) as measurements,
                   MAX(timestamp) as last_update
            FROM metric_data 
            WHERE provider_key = 'openaq' 
            AND metric_name = 'air_quality_pm25'
            AND timestamp > datetime('now', '-7 days')
        """)
        
        # Get air quality by location
        city_data = execute_query("""
            SELECT location_lat, location_lng, 
                   AVG(value) as pm25_level,
                   COUNT(*) as readings,
                   metadata
            FROM metric_data 
            WHERE provider_key = 'openaq' 
            AND metric_name = 'air_quality_pm25'
            AND timestamp > datetime('now', '-7 days')
            AND location_lat IS NOT NULL
            GROUP BY location_lat, location_lng
            ORDER BY pm25_level DESC
            LIMIT 20
        """)
        
        if air_quality and air_quality[0]['avg_pm25']:
            avg_pm25 = air_quality[0]['avg_pm25']
            if avg_pm25 <= 12:
                status = "✅ GOOD"
            elif avg_pm25 <= 35:
                status = "🟡 MODERATE"
            elif avg_pm25 <= 55:
                status = "🟠 UNHEALTHY"
            else:
                status = "🔴 DANGEROUS"
        else:
            status = "📊 NO DATA"
            avg_pm25 = 0
        
        return {
            'status': status,
            'avg_pm25': round(avg_pm25, 1) if avg_pm25 else 0,
            'measurements': air_quality[0]['measurements'] if air_quality else 0,
            'last_update': air_quality[0]['last_update'] if air_quality else 'Never',
            'cities': city_data
        }
    except Exception as e:
        return {
            'status': '❌ ERROR',
            'avg_pm25': 0,
            'measurements': 0,
            'last_update': 'Error',
            'cities': [],
            'error': str(e)
        }

def get_ocean_status():
    """Get current ocean conditions"""
    try:
        # Get latest ocean data from NOAA
        ocean_data = execute_query("""
            SELECT AVG(CASE WHEN metric_name = 'water_temperature' THEN value END) as avg_temp,
                   AVG(CASE WHEN metric_name = 'water_level' THEN value END) as avg_level,
                   COUNT(*) as measurements,
                   MAX(timestamp) as last_update
            FROM metric_data 
            WHERE provider_key = 'noaa_ocean' 
            AND timestamp > datetime('now', '-7 days')
        """)
        
        # Get station data
        stations = execute_query("""
            SELECT location_lat, location_lng,
                   AVG(CASE WHEN metric_name = 'water_temperature' THEN value END) as temperature,
                   AVG(CASE WHEN metric_name = 'water_level' THEN value END) as water_level,
                   metadata
            FROM metric_data 
            WHERE provider_key = 'noaa_ocean' 
            AND timestamp > datetime('now', '-7 days')
            AND location_lat IS NOT NULL
            GROUP BY location_lat, location_lng
            LIMIT 12
        """)
        
        if ocean_data and ocean_data[0] and ocean_data[0]['avg_temp']:
            avg_temp = ocean_data[0]['avg_temp']
            # Ocean temperature status (rough guidelines)
            if 15 <= avg_temp <= 25:
                status = "📊 NORMAL"
            elif avg_temp > 25:
                status = "🌡️ WARM"
            else:
                status = "🧊 COOL"
        else:
            status = "📊 NO DATA"
            avg_temp = 0
        
        return {
            'status': status,
            'avg_temp': round(avg_temp, 1) if avg_temp else 0,
            'avg_level': round(ocean_data[0]['avg_level'], 2) if ocean_data and ocean_data[0]['avg_level'] else 0,
            'measurements': ocean_data[0]['measurements'] if ocean_data else 0,
            'last_update': ocean_data[0]['last_update'] if ocean_data else 'Never',
            'stations': stations
        }
    except Exception as e:
        return {
            'status': '❌ ERROR',
            'avg_temp': 0,
            'avg_level': 0,
            'measurements': 0,
            'last_update': 'Error',
            'stations': [],
            'error': str(e)
        }

def calculate_environmental_health(fire_data, air_data, ocean_data):
    """Calculate overall environmental health score"""
    try:
        score = 100  # Start with perfect score
        status = "🟢 EXCELLENT"
        
        # Fire impact (0-30 points deduction)
        if fire_data['active_fires'] > 100:
            score -= 30
        elif fire_data['active_fires'] > 50:
            score -= 20
        elif fire_data['active_fires'] > 10:
            score -= 10
        
        # Air quality impact (0-40 points deduction)
        if air_data['avg_pm25'] > 55:
            score -= 40
        elif air_data['avg_pm25'] > 35:
            score -= 30
        elif air_data['avg_pm25'] > 25:
            score -= 20
        elif air_data['avg_pm25'] > 12:
            score -= 10
        
        # Ocean temperature impact (0-30 points deduction)
        if ocean_data['avg_temp'] > 28:
            score -= 20
        elif ocean_data['avg_temp'] > 26:
            score -= 10
        
        # Determine status based on score
        if score >= 85:
            status = "🟢 EXCELLENT"
        elif score >= 70:
            status = "🟡 GOOD"
        elif score >= 50:
            status = "🟠 MODERATE"
        elif score >= 30:
            status = "🔴 POOR"
        else:
            status = "🚨 CRITICAL"
        
        return {
            'score': max(0, score),
            'status': status,
            'factors': {
                'fires': fire_data['active_fires'],
                'air_quality': air_data['avg_pm25'],
                'ocean_temp': ocean_data['avg_temp']
            }
        }
    except Exception as e:
        return {
            'score': 0,
            'status': '❌ ERROR',
            'factors': {},
            'error': str(e)
        }

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
        
        # Ocean Data
        ocean_result = runner.run_task('noaa_ocean_water_level', triggered_by='dashboard_refresh')
        results.append({'task': 'ocean', 'success': ocean_result['success']})
        
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

@app.errorhandler(404)
def not_found(error):
    return "ECO WATCH TERRA SCAN - Page not found", 404

@app.errorhandler(500)
def internal_error(error):
    return "ECO WATCH TERRA SCAN - Internal error", 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 
