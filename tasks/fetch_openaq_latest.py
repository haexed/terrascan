#!/usr/bin/env python3
"""
OpenAQ Air Quality Data Fetcher
Fetches latest air quality data from OpenAQ API
"""

import requests
import sys
import os
from datetime import datetime
from typing import Dict, Any

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from database.db import store_metric_data
from database.config_manager import get_provider_config, get_dataset_config, get_system_config

def fetch_openaq_latest(limit: int = 100, parameter: str = 'pm25') -> Dict[str, Any]:
    """
    Fetch latest air quality data from OpenAQ
    
    Args:
        limit: Number of measurements to fetch (default: 100)
        parameter: Air quality parameter to fetch (pm25, pm10, o3, etc.)
    
    Returns:
        Dict with execution results
    """
    
    # Get configuration from database
    base_url = get_provider_config('openaq', 'base_url', 'https://api.openaq.org/v2')
    timeout = get_provider_config('openaq', 'timeout_seconds', 30)
    simulation_mode = get_system_config('simulation_mode', True)
    
    if simulation_mode:
        # For demo purposes, simulate the data
        return _simulate_openaq_data(limit, parameter)
    
    # Build API URL
    url = f"{base_url}/latest"
    params = {
        'limit': limit,
        'parameter': parameter,
        'sort': 'desc',
        'radius': 10000  # Include all locations
    }
    
    try:
        print(f"🌬️ Fetching air quality data from OpenAQ: {parameter}, limit {limit}")
        
        response = requests.get(url, params=params, timeout=timeout)
        response.raise_for_status()
        
        data = response.json()
        if 'results' not in data:
            return {
                'output': 'No air quality data available',
                'records_processed': 0,
                'cost_cents': 0
            }
        
        measurements = data['results']
        
        # Store air quality data in database
        records_stored = 0
        current_time = datetime.now().isoformat()
        
        for measurement in measurements:
            try:
                # Extract key fields
                lat = measurement.get('coordinates', {}).get('latitude')
                lng = measurement.get('coordinates', {}).get('longitude')
                value = measurement.get('value')
                unit = measurement.get('unit')
                
                if lat is None or lng is None or value is None:
                    continue
                
                # Store as metric data
                store_metric_data(
                    timestamp=measurement.get('date', {}).get('utc', current_time),
                    provider_key='openaq',
                    dataset='air_quality',
                    metric_name=f"air_quality_{parameter}",
                    value=float(value),
                    unit=unit,
                    location_lat=float(lat),
                    location_lng=float(lng),
                    metadata={
                        'parameter': measurement.get('parameter'),
                        'location': measurement.get('location'),
                        'city': measurement.get('city'),
                        'country': measurement.get('country'),
                        'source_name': measurement.get('sourceName'),
                        'mobile': measurement.get('mobile', False),
                        'last_updated': measurement.get('date', {}).get('utc')
                    }
                )
                records_stored += 1
                
            except (ValueError, KeyError, TypeError) as e:
                print(f"⚠️ Skipping invalid air quality record: {e}")
                continue
        
        output_msg = f"Successfully fetched {len(measurements)} air quality measurements, stored {records_stored} records"
        print(f"✅ {output_msg}")
        
        return {
            'output': output_msg,
            'records_processed': records_stored,
            'cost_cents': 0  # OpenAQ is free
        }
        
    except requests.RequestException as e:
        raise Exception(f"Failed to fetch OpenAQ data: {e}")
    except Exception as e:
        raise Exception(f"Error processing air quality data: {e}")

def _simulate_openaq_data(limit: int, parameter: str) -> Dict[str, Any]:
    """
    Simulate air quality data for testing when API is not available
    """
    import random
    
    print(f"🌬️ Simulating air quality data: {parameter}, limit {limit}")
    
    # Generate some fake air quality data
    current_time = datetime.now().isoformat()
    records_stored = 0
    
    # Simulate air quality measurements from different cities
    cities = [
        {'name': 'London', 'lat': 51.5074, 'lng': -0.1278, 'country': 'GB'},
        {'name': 'Paris', 'lat': 48.8566, 'lng': 2.3522, 'country': 'FR'},
        {'name': 'New York', 'lat': 40.7128, 'lng': -74.0060, 'country': 'US'},
        {'name': 'Beijing', 'lat': 39.9042, 'lng': 116.4074, 'country': 'CN'},
        {'name': 'Mumbai', 'lat': 19.0760, 'lng': 72.8777, 'country': 'IN'},
        {'name': 'São Paulo', 'lat': -23.5558, 'lng': -46.6396, 'country': 'BR'},
    ]
    
    # Generate random measurements for each city
    num_measurements = min(limit, len(cities) * 3)
    
    for i in range(num_measurements):
        city = random.choice(cities)
        
        # Add some randomness to location
        lat = city['lat'] + random.uniform(-0.1, 0.1)
        lng = city['lng'] + random.uniform(-0.1, 0.1)
        
        # Generate realistic air quality values based on parameter
        if parameter == 'pm25':
            value = random.uniform(5, 150)  # μg/m³
            unit = 'μg/m³'
        elif parameter == 'pm10':
            value = random.uniform(10, 200)  # μg/m³
            unit = 'μg/m³'
        elif parameter == 'o3':
            value = random.uniform(20, 180)  # μg/m³
            unit = 'μg/m³'
        elif parameter == 'no2':
            value = random.uniform(5, 100)  # μg/m³
            unit = 'μg/m³'
        else:
            value = random.uniform(1, 50)
            unit = 'μg/m³'
        
        store_metric_data(
            timestamp=current_time,
            provider_key='openaq',
            dataset='air_quality',
            metric_name=f"air_quality_{parameter}",
            value=value,
            unit=unit,
            location_lat=lat,
            location_lng=lng,
            metadata={
                'parameter': parameter,
                'location': f"Simulated Station {i+1}",
                'city': city['name'],
                'country': city['country'],
                'source_name': 'Simulation',
                'mobile': False,
                'simulated': True
            }
        )
        records_stored += 1
    
    output_msg = f"Simulated {records_stored} air quality measurements for {parameter}"
    print(f"✅ {output_msg}")
    
    return {
        'output': output_msg,
        'records_processed': records_stored,
        'cost_cents': 0
    }

if __name__ == "__main__":
    # Test the function
    result = fetch_openaq_latest()
    print(f"Result: {result}") 
