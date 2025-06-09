#!/usr/bin/env python3
"""
NASA FIRMS Fire Data Fetcher
Fetches active fire data from NASA FIRMS API
"""

import requests
import sys
import os
from datetime import datetime, timedelta
from typing import Dict, Any

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from database.db import store_metric_data
from database.config_manager import get_provider_config, get_dataset_config, get_system_config

def fetch_nasa_fires(region: str = 'WORLD', days: int = 1, source: str = 'MODIS_NRT') -> Dict[str, Any]:
    """
    Fetch active fire data from NASA FIRMS
    
    Args:
        region: Geographic region (WORLD, USA, etc.)
        days: Number of days back to fetch (1-10)
        source: Data source (MODIS_NRT, MODIS_SP, VIIRS_NOAA20_NRT, etc.)
    
    Returns:
        Dict with execution results
    """
    
    # Get configuration from database
    base_url = get_provider_config('nasa_firms', 'base_url', 'https://firms.modaps.eosdis.nasa.gov/api/active_fire/csv')
    timeout = get_provider_config('nasa_firms', 'timeout_seconds', 30)
    simulation_mode = get_system_config('simulation_mode', True)
    
    # Get API key from environment (you need to register at NASA FIRMS)
    api_key = os.getenv('NASA_FIRMS_API_KEY')
    if not api_key or simulation_mode:
        # For demo purposes, we'll simulate the data
        return _simulate_fire_data(region, days)
    
    # Build API URL
    url = f"{base_url}/{api_key}/{source}/{region}/{days}"
    
    try:
        print(f"🔥 Fetching fire data from NASA FIRMS: {region}, {days} days")
        
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        
        # Parse CSV data
        lines = response.text.strip().split('\n')
        if len(lines) < 2:
            return {
                'output': 'No fire data available',
                'records_processed': 0,
                'cost_cents': 0
            }
        
        headers = lines[0].split(',')
        fire_records = []
        
        for line in lines[1:]:
            if line.strip():
                values = line.split(',')
                if len(values) >= len(headers):
                    fire_records.append(dict(zip(headers, values)))
        
        # Store fire data in database
        records_stored = 0
        current_time = datetime.now().isoformat()
        
        for fire in fire_records:
            try:
                # Extract key fields
                lat = float(fire.get('latitude', 0))
                lng = float(fire.get('longitude', 0))
                brightness = float(fire.get('brightness', 0))
                confidence = float(fire.get('confidence', 50)) / 100.0
                
                # Store as metric data
                store_metric_data(
                    timestamp=current_time,
                    provider_key='nasa_firms',
                    dataset='active_fires',
                    metric_name='fire_brightness',
                    value=brightness,
                    unit='kelvin',
                    location_lat=lat,
                    location_lng=lng,
                    metadata={
                        'confidence': confidence,
                        'satellite': fire.get('satellite', ''),
                        'instrument': fire.get('instrument', ''),
                        'daynight': fire.get('daynight', ''),
                        'type': fire.get('type', ''),
                        'scan': fire.get('scan', ''),
                        'track': fire.get('track', ''),
                        'frp': fire.get('frp', ''),  # Fire Radiative Power
                        'acq_date': fire.get('acq_date', ''),
                        'acq_time': fire.get('acq_time', '')
                    }
                )
                records_stored += 1
                
            except (ValueError, KeyError) as e:
                print(f"⚠️ Skipping invalid fire record: {e}")
                continue
        
        output_msg = f"Successfully fetched {len(fire_records)} fire detections, stored {records_stored} records"
        print(f"✅ {output_msg}")
        
        return {
            'output': output_msg,
            'records_processed': records_stored,
            'cost_cents': 0  # NASA FIRMS is free
        }
        
    except requests.RequestException as e:
        raise Exception(f"Failed to fetch NASA FIRMS data: {e}")
    except Exception as e:
        raise Exception(f"Error processing fire data: {e}")

def _simulate_fire_data(region: str, days: int) -> Dict[str, Any]:
    """
    Simulate fire data for testing when API key is not available
    """
    import random
    
    print(f"🔥 Simulating fire data (no API key): {region}, {days} days")
    
    # Generate some fake fire data
    current_time = datetime.now().isoformat()
    records_stored = 0
    
    # Simulate different fire hotspots based on region
    if region == 'WORLD':
        fire_locations = [
            {'lat': -23.5, 'lng': -46.6, 'name': 'Brazil'},  # São Paulo area
            {'lat': 37.7, 'lng': -122.4, 'name': 'California'},  # San Francisco
            {'lat': -33.9, 'lng': 151.2, 'name': 'Australia'},  # Sydney area
            {'lat': 40.7, 'lng': -74.0, 'name': 'New York'},  # NYC (urban heat)
        ]
    else:
        fire_locations = [
            {'lat': 39.0, 'lng': -120.0, 'name': 'California'},
            {'lat': 45.0, 'lng': -114.0, 'name': 'Idaho'},
        ]
    
    for location in fire_locations:
        # Generate 5-15 random fires near each location
        num_fires = random.randint(5, 15)
        
        for _ in range(num_fires):
            # Add some randomness to location
            lat = location['lat'] + random.uniform(-2, 2)
            lng = location['lng'] + random.uniform(-2, 2)
            brightness = random.uniform(300, 400)  # Kelvin
            confidence = random.uniform(0.5, 1.0)
            
            store_metric_data(
                timestamp=current_time,
                provider_key='nasa_firms',
                dataset='active_fires',
                metric_name='fire_brightness',
                value=brightness,
                unit='kelvin',
                location_lat=lat,
                location_lng=lng,
                metadata={
                    'confidence': confidence,
                    'satellite': 'MODIS',
                    'instrument': 'MODIS',
                    'daynight': 'D' if random.random() > 0.3 else 'N',
                    'type': 0,
                    'simulated': True,
                    'region': location['name']
                }
            )
            records_stored += 1
    
    output_msg = f"Simulated {records_stored} fire detections for {region}"
    print(f"✅ {output_msg}")
    
    return {
        'output': output_msg,
        'records_processed': records_stored,
        'cost_cents': 0
    }

if __name__ == "__main__":
    # Test the function
    result = fetch_nasa_fires()
    print(f"Result: {result}") 
