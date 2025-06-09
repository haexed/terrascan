#!/usr/bin/env python3
"""
NOAA Ocean Service Data Fetcher
Fetches oceanographic data from NOAA Tides and Currents API
"""

import requests
import sys
import os
from datetime import datetime, timedelta
from typing import Dict, Any, List

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from database.db import store_metric_data
from database.config_manager import get_provider_config, get_dataset_config, get_system_config

def fetch_noaa_ocean(
    product: str = 'water_level',
    time_range: int = 24,
    stations: List[str] = None,
    units: str = 'metric'
) -> Dict[str, Any]:
    """
    Fetch oceanographic data from NOAA Ocean Service
    
    Args:
        product: Data product ('water_level', 'water_temperature', 'air_temperature', 'wind', 'air_pressure', 'conductivity', 'visibility')
        time_range: Hours of data to fetch (default: 24)
        stations: List of station IDs to fetch from (if None, uses default stations)
        units: Units system ('metric' or 'english')
    
    Returns:
        Dict with execution results
    """
    
    # Get configuration from database
    base_url = get_provider_config('noaa_ocean', 'base_url', 'https://tidesandcurrents.noaa.gov/api/datagetter')
    timeout = get_provider_config('noaa_ocean', 'timeout_seconds', 30)
    simulation_mode = get_system_config('simulation_mode', True)
    
    if simulation_mode:
        # For demo purposes, simulate the data
        return _simulate_noaa_ocean_data(product, time_range, stations or _get_default_stations())
    
    # Use default stations if none provided
    if not stations:
        stations = _get_default_stations()
    
    try:
        print(f"🌊 Fetching NOAA Ocean data: {product}, {time_range}h from {len(stations)} stations")
        
        all_records = []
        records_stored = 0
        
        # Calculate time range
        end_time = datetime.now()
        begin_time = end_time - timedelta(hours=time_range)
        
        for station_id in stations:
            try:
                # Build API parameters
                params = {
                    'product': product,
                    'application': 'Terrascan',
                    'begin_date': begin_time.strftime('%Y%m%d %H:%M'),
                    'end_date': end_time.strftime('%Y%m%d %H:%M'),
                    'station': station_id,
                    'time_zone': 'gmt',
                    'units': units,
                    'format': 'json'
                }
                
                response = requests.get(base_url, params=params, timeout=timeout)
                response.raise_for_status()
                
                data = response.json()
                
                if 'data' not in data or not data['data']:
                    print(f"⚠️ No data available for station {station_id}")
                    continue
                
                # Get station metadata
                metadata_info = data.get('metadata', {})
                station_name = metadata_info.get('name', f'Station {station_id}')
                lat = float(metadata_info.get('lat', 0))
                lng = float(metadata_info.get('lon', 0))
                
                # Process each data point
                for record in data['data']:
                    try:
                        timestamp = record.get('t')  # Time
                        value_str = record.get('v')  # Value
                        
                        if not timestamp or not value_str:
                            continue
                        
                        # Parse timestamp
                        timestamp_dt = datetime.strptime(timestamp, '%Y-%m-%d %H:%M')
                        timestamp_iso = timestamp_dt.isoformat()
                        
                        # Parse value
                        value = float(value_str)
                        
                        # Determine metric name and unit based on product
                        metric_name, unit = _get_metric_info(product, units)
                        
                        # Store as metric data
                        store_metric_data(
                            timestamp=timestamp_iso,
                            provider_key='noaa_ocean',
                            dataset='oceanographic',
                            metric_name=metric_name,
                            value=value,
                            unit=unit,
                            location_lat=lat,
                            location_lng=lng,
                            metadata={
                                'station_id': station_id,
                                'station_name': station_name,
                                'product': product,
                                'quality': record.get('q', ''),  # Quality flag
                                'sigma': record.get('s', ''),    # Sigma (standard deviation)
                                'flags': record.get('f', ''),    # Flags
                                'state': metadata_info.get('state', ''),
                                'port_name': metadata_info.get('portname', ''),
                            }
                        )
                        records_stored += 1
                        
                    except (ValueError, KeyError, TypeError) as e:
                        print(f"⚠️ Skipping invalid record from station {station_id}: {e}")
                        continue
                
                print(f"  ✓ Station {station_id} ({station_name}): {len(data['data'])} records")
                
            except requests.RequestException as e:
                print(f"⚠️ Failed to fetch data from station {station_id}: {e}")
                continue
            except Exception as e:
                print(f"⚠️ Error processing station {station_id}: {e}")
                continue
        
        output_msg = f"Successfully fetched {product} data from {len(stations)} NOAA stations, stored {records_stored} records"
        print(f"✅ {output_msg}")
        
        return {
            'output': output_msg,
            'records_processed': records_stored,
            'cost_cents': 0  # NOAA Ocean Service is free
        }
        
    except Exception as e:
        raise Exception(f"Error fetching NOAA Ocean data: {e}")

def _get_default_stations() -> List[str]:
    """
    Get default NOAA station IDs for major coastal locations
    """
    return [
        '8518750',  # The Battery, New York
        '8443970',  # Boston, Massachusetts
        '8571421',  # Lamberts Point, Norfolk, Virginia
        '8661070',  # Springmaid Pier, South Carolina
        '8720030',  # Daytona Beach Shores, Florida
        '8724580',  # Key West, Florida
        '8761724',  # Port Isabel, Texas
        '8771450',  # Galveston Pier 21, Texas
        '9414290',  # San Francisco, California
        '9447130',  # Seattle, Washington
        '1612340',  # Honolulu, Hawaii
        '9751364',  # Ketchikan, Alaska
    ]

def _get_metric_info(product: str, units: str) -> tuple:
    """
    Get metric name and unit based on NOAA product type
    """
    if product == 'water_level':
        return 'water_level', 'meters' if units == 'metric' else 'feet'
    elif product == 'water_temperature':
        return 'water_temperature', 'celsius' if units == 'metric' else 'fahrenheit'
    elif product == 'air_temperature':
        return 'air_temperature', 'celsius' if units == 'metric' else 'fahrenheit'
    elif product == 'wind':
        return 'wind_speed', 'mps' if units == 'metric' else 'mph'
    elif product == 'air_pressure':
        return 'air_pressure', 'mbar' if units == 'metric' else 'inches'
    elif product == 'conductivity':
        return 'conductivity', 'mS/cm'
    elif product == 'visibility':
        return 'visibility', 'km' if units == 'metric' else 'miles'
    else:
        return f'ocean_{product}', 'unknown'

def _simulate_noaa_ocean_data(product: str, time_range: int, stations: List[str]) -> Dict[str, Any]:
    """
    Simulate NOAA Ocean data for testing when API is not available
    """
    import random
    
    print(f"🌊 Simulating NOAA Ocean data: {product}, {time_range}h from {len(stations)} stations")
    
    records_stored = 0
    current_time = datetime.now()
    
    # Station locations (approximate)
    station_locations = {
        '8518750': {'name': 'The Battery, NY', 'lat': 40.7, 'lng': -74.0, 'state': 'NY'},
        '8443970': {'name': 'Boston, MA', 'lat': 42.3, 'lng': -71.1, 'state': 'MA'},
        '8571421': {'name': 'Norfolk, VA', 'lat': 36.8, 'lng': -76.3, 'state': 'VA'},
        '8661070': {'name': 'Springmaid Pier, SC', 'lat': 33.7, 'lng': -78.9, 'state': 'SC'},
        '8720030': {'name': 'Daytona Beach, FL', 'lat': 29.2, 'lng': -81.0, 'state': 'FL'},
        '8724580': {'name': 'Key West, FL', 'lat': 24.6, 'lng': -81.8, 'state': 'FL'},
        '8761724': {'name': 'Port Isabel, TX', 'lat': 26.1, 'lng': -97.2, 'state': 'TX'},
        '8771450': {'name': 'Galveston, TX', 'lat': 29.3, 'lng': -94.8, 'state': 'TX'},
        '9414290': {'name': 'San Francisco, CA', 'lat': 37.8, 'lng': -122.5, 'state': 'CA'},
        '9447130': {'name': 'Seattle, WA', 'lat': 47.6, 'lng': -122.3, 'state': 'WA'},
        '1612340': {'name': 'Honolulu, HI', 'lat': 21.3, 'lng': -157.9, 'state': 'HI'},
        '9751364': {'name': 'Ketchikan, AK', 'lat': 55.3, 'lng': -131.6, 'state': 'AK'},
    }
    
    # Simulate hourly data for each station
    for station_id in stations:
        if station_id not in station_locations:
            continue
            
        station_info = station_locations[station_id]
        
        # Generate data for each hour in time range
        for hour_offset in range(time_range):
            timestamp = current_time - timedelta(hours=hour_offset)
            timestamp_iso = timestamp.isoformat()
            
            # Generate realistic values based on product type
            if product == 'water_level':
                # Simulate tidal patterns
                tidal_cycle = 2 * 3.14159 * (hour_offset / 12.4)  # Semi-diurnal tide
                base_level = 0.0
                amplitude = random.uniform(0.5, 2.0)  # meters
                value = base_level + amplitude * math.sin(tidal_cycle) + random.uniform(-0.1, 0.1)
                unit = 'meters'
            elif product == 'water_temperature':
                # Seasonal and daily variation
                seasonal_base = 15 + 10 * math.sin((datetime.now().timetuple().tm_yday / 365.0) * 2 * 3.14159)
                daily_variation = 2 * math.sin((hour_offset / 24.0) * 2 * 3.14159)
                value = seasonal_base + daily_variation + random.uniform(-2, 2)
                unit = 'celsius'
            elif product == 'air_temperature':
                value = random.uniform(10, 30) + 5 * math.sin((hour_offset / 24.0) * 2 * 3.14159)
                unit = 'celsius'
            elif product == 'wind':
                value = random.uniform(0, 25)  # wind speed
                unit = 'mps'
            elif product == 'air_pressure':
                value = random.uniform(1010, 1025)  # typical sea level pressure
                unit = 'mbar'
            else:
                value = random.uniform(0, 100)
                unit = 'unknown'
            
            metric_name, _ = _get_metric_info(product, 'metric')
            
            store_metric_data(
                timestamp=timestamp_iso,
                provider_key='noaa_ocean',
                dataset='oceanographic',
                metric_name=metric_name,
                value=value,
                unit=unit,
                location_lat=station_info['lat'],
                location_lng=station_info['lng'],
                metadata={
                    'station_id': station_id,
                    'station_name': station_info['name'],
                    'product': product,
                    'state': station_info['state'],
                    'simulated': True
                }
            )
            records_stored += 1
    
    output_msg = f"Simulated {records_stored} {product} measurements from {len(stations)} NOAA stations"
    print(f"✅ {output_msg}")
    
    return {
        'output': output_msg,
        'records_processed': records_stored,
        'cost_cents': 0
    }

# Need to import math for simulation
import math

if __name__ == "__main__":
    # Test the function
    result = fetch_noaa_ocean()
    print(f"Result: {result}") 
