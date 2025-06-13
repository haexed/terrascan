#!/usr/bin/env python3
"""
Production debug script for ocean temperature issue
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from database.db import execute_query
import sqlite3

def debug_production_ocean():
    """Comprehensive debug for production ocean temperature issue"""
    
    print("🔍 PRODUCTION OCEAN TEMPERATURE DEBUG")
    print("=" * 60)
    
    # Environment info
    print(f"\n🌍 ENVIRONMENT:")
    print(f"   RAILWAY_ENVIRONMENT: {os.getenv('RAILWAY_ENVIRONMENT_NAME', 'Not set')}")
    print(f"   DATABASE_URL: {'SET' if os.getenv('DATABASE_URL') else 'NOT_SET'}")
    
    # Database info
    print(f"\n📁 DATABASE INFO:")
    try:
        db_info = execute_query("SELECT sqlite_version() as version")
        print(f"   SQLite Version: {db_info[0]['version']}")
        
        total_records = execute_query("SELECT COUNT(*) as count FROM metric_data")[0]['count']
        print(f"   Total Records: {total_records}")
        
        ocean_records = execute_query("SELECT COUNT(*) as count FROM metric_data WHERE provider_key = 'noaa_ocean'")[0]['count']
        print(f"   Ocean Records: {ocean_records}")
        
        temp_records = execute_query("SELECT COUNT(*) as count FROM metric_data WHERE provider_key = 'noaa_ocean' AND metric_name = 'water_temperature'")[0]['count']
        print(f"   Temperature Records: {temp_records}")
        
    except Exception as e:
        print(f"   Error: {e}")
    
    # Time and date functions
    print(f"\n⏰ TIME FUNCTIONS:")
    try:
        time_info = execute_query("""
            SELECT 
                datetime('now') as sqlite_now,
                date('now') as sqlite_date,
                datetime('now', '-7 days') as seven_days_ago_dt,
                date('now', '-7 days') as seven_days_ago_d
        """)[0]
        
        for key, value in time_info.items():
            print(f"   {key}: {value}")
            
    except Exception as e:
        print(f"   Error: {e}")
    
    # Sample temperature data
    print(f"\n🌡️ SAMPLE TEMPERATURE DATA:")
    try:
        samples = execute_query("""
            SELECT value, timestamp, location_lat, location_lng
            FROM metric_data 
            WHERE provider_key = 'noaa_ocean' 
            AND metric_name = 'water_temperature'
            ORDER BY timestamp DESC 
            LIMIT 5
        """)
        
        for i, sample in enumerate(samples):
            print(f"   {i+1}. {sample['value']}°C at {sample['timestamp']} ({sample['location_lat']}, {sample['location_lng']})")
            
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test different date queries
    print(f"\n🧪 QUERY TESTS:")
    
    queries = [
        ("datetime('now', '-7 days')", "timestamp > datetime('now', '-7 days')"),
        ("date('now', '-7 days')", "date(timestamp) > date('now', '-7 days')"),
        ("Simple date", "timestamp > '2025-06-06'"),
        ("No date filter", "1=1")
    ]
    
    for name, condition in queries:
        try:
            result = execute_query(f"""
                SELECT 
                    COUNT(*) as count,
                    AVG(CASE WHEN metric_name = 'water_temperature' THEN value END) as avg_temp
                FROM metric_data 
                WHERE provider_key = 'noaa_ocean' 
                AND {condition}
            """)[0]
            
            print(f"   {name}: {result['count']} records, avg_temp = {result['avg_temp']}")
            
        except Exception as e:
            print(f"   {name}: Error - {e}")
    
    # Test the actual function
    print(f"\n🎯 ACTUAL FUNCTION TEST:")
    try:
        from web.app import get_ocean_status
        ocean_status = get_ocean_status()
        print(f"   get_ocean_status() result:")
        for key, value in ocean_status.items():
            print(f"     {key}: {value}")
            
    except Exception as e:
        print(f"   Error: {e}")
    
    # Configuration check
    print(f"\n⚙️ CONFIGURATION:")
    try:
        from database.config_manager import get_system_config
        simulation_mode = get_system_config('simulation_mode', None)
        print(f"   simulation_mode: {simulation_mode}")
        
    except Exception as e:
        print(f"   Error: {e}")

if __name__ == "__main__":
    debug_production_ocean() 
