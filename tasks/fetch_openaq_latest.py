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

def fetch_openaq_latest(limit: int = 200, parameter: str = 'pm25') -> Dict[str, Any]:
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
    
    # Simulate air quality measurements from major cities worldwide
    cities = [
        # North America
        {'name': 'New York', 'lat': 40.7128, 'lng': -74.0060, 'country': 'US'},
        {'name': 'Los Angeles', 'lat': 34.0522, 'lng': -118.2437, 'country': 'US'},
        {'name': 'Chicago', 'lat': 41.8781, 'lng': -87.6298, 'country': 'US'},
        {'name': 'Houston', 'lat': 29.7604, 'lng': -95.3698, 'country': 'US'},
        {'name': 'Phoenix', 'lat': 33.4484, 'lng': -112.0740, 'country': 'US'},
        {'name': 'Philadelphia', 'lat': 39.9526, 'lng': -75.1652, 'country': 'US'},
        {'name': 'San Antonio', 'lat': 29.4241, 'lng': -98.4936, 'country': 'US'},
        {'name': 'San Diego', 'lat': 32.7157, 'lng': -117.1611, 'country': 'US'},
        {'name': 'Dallas', 'lat': 32.7767, 'lng': -96.7970, 'country': 'US'},
        {'name': 'San Francisco', 'lat': 37.7749, 'lng': -122.4194, 'country': 'US'},
        {'name': 'Seattle', 'lat': 47.6062, 'lng': -122.3321, 'country': 'US'},
        {'name': 'Denver', 'lat': 39.7392, 'lng': -104.9903, 'country': 'US'},
        {'name': 'Toronto', 'lat': 43.6532, 'lng': -79.3832, 'country': 'CA'},
        {'name': 'Montreal', 'lat': 45.5017, 'lng': -73.5673, 'country': 'CA'},
        {'name': 'Vancouver', 'lat': 49.2827, 'lng': -123.1207, 'country': 'CA'},
        {'name': 'Mexico City', 'lat': 19.4326, 'lng': -99.1332, 'country': 'MX'},
        
        # Europe
        {'name': 'London', 'lat': 51.5074, 'lng': -0.1278, 'country': 'GB'},
        {'name': 'Paris', 'lat': 48.8566, 'lng': 2.3522, 'country': 'FR'},
        {'name': 'Berlin', 'lat': 52.5200, 'lng': 13.4050, 'country': 'DE'},
        {'name': 'Madrid', 'lat': 40.4168, 'lng': -3.7038, 'country': 'ES'},
        {'name': 'Rome', 'lat': 41.9028, 'lng': 12.4964, 'country': 'IT'},
        {'name': 'Amsterdam', 'lat': 52.3676, 'lng': 4.9041, 'country': 'NL'},
        {'name': 'Vienna', 'lat': 48.2082, 'lng': 16.3738, 'country': 'AT'},
        {'name': 'Stockholm', 'lat': 59.3293, 'lng': 18.0686, 'country': 'SE'},
        {'name': 'Copenhagen', 'lat': 55.6761, 'lng': 12.5683, 'country': 'DK'},
        {'name': 'Oslo', 'lat': 59.9139, 'lng': 10.7522, 'country': 'NO'},
        {'name': 'Helsinki', 'lat': 60.1699, 'lng': 24.9384, 'country': 'FI'},
        {'name': 'Warsaw', 'lat': 52.2297, 'lng': 21.0122, 'country': 'PL'},
        {'name': 'Prague', 'lat': 50.0755, 'lng': 14.4378, 'country': 'CZ'},
        {'name': 'Budapest', 'lat': 47.4979, 'lng': 19.0402, 'country': 'HU'},
        {'name': 'Zurich', 'lat': 47.3769, 'lng': 8.5417, 'country': 'CH'},
        
        # Asia
        {'name': 'Tokyo', 'lat': 35.6762, 'lng': 139.6503, 'country': 'JP'},
        {'name': 'Beijing', 'lat': 39.9042, 'lng': 116.4074, 'country': 'CN'},
        {'name': 'Shanghai', 'lat': 31.2304, 'lng': 121.4737, 'country': 'CN'},
        {'name': 'Guangzhou', 'lat': 23.1291, 'lng': 113.2644, 'country': 'CN'},
        {'name': 'Shenzhen', 'lat': 22.5431, 'lng': 114.0579, 'country': 'CN'},
        {'name': 'Mumbai', 'lat': 19.0760, 'lng': 72.8777, 'country': 'IN'},
        {'name': 'Delhi', 'lat': 28.7041, 'lng': 77.1025, 'country': 'IN'},
        {'name': 'Bangalore', 'lat': 12.9716, 'lng': 77.5946, 'country': 'IN'},
        {'name': 'Chennai', 'lat': 13.0827, 'lng': 80.2707, 'country': 'IN'},
        {'name': 'Kolkata', 'lat': 22.5726, 'lng': 88.3639, 'country': 'IN'},
        {'name': 'Seoul', 'lat': 37.5665, 'lng': 126.9780, 'country': 'KR'},
        {'name': 'Singapore', 'lat': 1.3521, 'lng': 103.8198, 'country': 'SG'},
        {'name': 'Bangkok', 'lat': 13.7563, 'lng': 100.5018, 'country': 'TH'},
        {'name': 'Jakarta', 'lat': -6.2088, 'lng': 106.8456, 'country': 'ID'},
        {'name': 'Manila', 'lat': 14.5995, 'lng': 120.9842, 'country': 'PH'},
        {'name': 'Kuala Lumpur', 'lat': 3.1390, 'lng': 101.6869, 'country': 'MY'},
        {'name': 'Ho Chi Minh City', 'lat': 10.8231, 'lng': 106.6297, 'country': 'VN'},
        {'name': 'Hanoi', 'lat': 21.0285, 'lng': 105.8542, 'country': 'VN'},
        
        # Middle East & Africa
        {'name': 'Dubai', 'lat': 25.2048, 'lng': 55.2708, 'country': 'AE'},
        {'name': 'Riyadh', 'lat': 24.7136, 'lng': 46.6753, 'country': 'SA'},
        {'name': 'Istanbul', 'lat': 41.0082, 'lng': 28.9784, 'country': 'TR'},
        {'name': 'Tehran', 'lat': 35.6892, 'lng': 51.3890, 'country': 'IR'},
        {'name': 'Cairo', 'lat': 30.0444, 'lng': 31.2357, 'country': 'EG'},
        {'name': 'Lagos', 'lat': 6.5244, 'lng': 3.3792, 'country': 'NG'},
        {'name': 'Johannesburg', 'lat': -26.2041, 'lng': 28.0473, 'country': 'ZA'},
        {'name': 'Cape Town', 'lat': -33.9249, 'lng': 18.4241, 'country': 'ZA'},
        {'name': 'Nairobi', 'lat': -1.2921, 'lng': 36.8219, 'country': 'KE'},
        
        # South America
        {'name': 'São Paulo', 'lat': -23.5558, 'lng': -46.6396, 'country': 'BR'},
        {'name': 'Rio de Janeiro', 'lat': -22.9068, 'lng': -43.1729, 'country': 'BR'},
        {'name': 'Buenos Aires', 'lat': -34.6118, 'lng': -58.3960, 'country': 'AR'},
        {'name': 'Lima', 'lat': -12.0464, 'lng': -77.0428, 'country': 'PE'},
        {'name': 'Bogotá', 'lat': 4.7110, 'lng': -74.0721, 'country': 'CO'},
        {'name': 'Santiago', 'lat': -33.4489, 'lng': -70.6693, 'country': 'CL'},
        
        # Oceania
        {'name': 'Sydney', 'lat': -33.8688, 'lng': 151.2093, 'country': 'AU'},
        {'name': 'Melbourne', 'lat': -37.8136, 'lng': 144.9631, 'country': 'AU'},
        {'name': 'Brisbane', 'lat': -27.4698, 'lng': 153.0251, 'country': 'AU'},
        {'name': 'Perth', 'lat': -31.9505, 'lng': 115.8605, 'country': 'AU'},
        {'name': 'Auckland', 'lat': -36.8485, 'lng': 174.7633, 'country': 'NZ'},
    ]
    
    # Generate random measurements for each city (2-4 stations per city)
    num_measurements = min(limit, len(cities) * 2)
    
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
