#!/usr/bin/env python3
"""
Test script to verify ocean temperature SQL fix
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from database.db import execute_query

def test_ocean_queries():
    """Test both old and new SQL queries"""
    
    print("🧪 Testing Ocean Temperature SQL Queries")
    print("=" * 50)
    
    # Test 1: Old query (broken)
    print("\n1️⃣ OLD QUERY (datetime - broken):")
    try:
        old_result = execute_query("""
            SELECT AVG(CASE WHEN metric_name = 'water_temperature' THEN value END) as avg_temp,
                   COUNT(*) as measurements
            FROM metric_data 
            WHERE provider_key = 'noaa_ocean' 
            AND timestamp > datetime('now', '-7 days')
        """)
        print(f"   Result: {old_result[0] if old_result else 'No data'}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 2: New query (fixed)
    print("\n2️⃣ NEW QUERY (date - fixed):")
    try:
        new_result = execute_query("""
            SELECT AVG(CASE WHEN metric_name = 'water_temperature' THEN value END) as avg_temp,
                   COUNT(*) as measurements
            FROM metric_data 
            WHERE provider_key = 'noaa_ocean' 
            AND date(timestamp) > date('now', '-7 days')
        """)
        print(f"   Result: {new_result[0] if new_result else 'No data'}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 3: Simple query (all data)
    print("\n3️⃣ ALL TEMPERATURE DATA:")
    try:
        all_result = execute_query("""
            SELECT COUNT(*) as total_temps,
                   AVG(value) as avg_temp,
                   MIN(timestamp) as oldest,
                   MAX(timestamp) as newest
            FROM metric_data 
            WHERE provider_key = 'noaa_ocean' 
            AND metric_name = 'water_temperature'
        """)
        print(f"   Result: {all_result[0] if all_result else 'No data'}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 4: Test the actual get_ocean_status function
    print("\n4️⃣ ACTUAL get_ocean_status() FUNCTION:")
    try:
        from web.app import get_ocean_status
        ocean_status = get_ocean_status()
        print(f"   avg_temp: {ocean_status['avg_temp']}°C")
        print(f"   status: {ocean_status['status']}")
        print(f"   measurements: {ocean_status['measurements']}")
    except Exception as e:
        print(f"   Error: {e}")

if __name__ == "__main__":
    test_ocean_queries() 
