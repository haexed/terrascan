import os
import requests
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from database.db import store_metric_data

def fetch_noaa_ocean_data(product: str = 'water_temperature', 
                         time_range: int = 24,
                         stations: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Fetch ocean data from NOAA CO-OPS API
    
    Args:
        product: Data product ('water_temperature', 'water_level', 'air_temperature')
        time_range: Hours of data to fetch (max 744 for hourly data) 
        stations: List of station IDs, uses defaults if None
    
    Returns:
        Dictionary with success status and message
    """
    if stations is None:
        stations = _get_default_stations()
    
    # NOAA CO-OPS API endpoint
    base_url = 'https://api.tidesandcurrents.noaa.gov/api/prod/datagetter'
    
    # Calculate time range
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(hours=time_range)
    
    records_stored = 0
    failed_stations = []
    
    for station_id in stations:
        try:
            params = {
                'product': product,
                'application': 'NOS.COOPS.TAC.WL',
                'begin_date': start_time.strftime('%Y%m%d %H:%M'),
                'end_date': end_time.strftime('%Y%m%d %H:%M'),
                'datum': 'MLLW',
                'station': station_id,
                'time_zone': 'GMT',
                'units': 'metric',
                'interval': 'h',  # hourly data
                'format': 'json'
            }
            
            response = requests.get(base_url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if 'data' not in data or not data['data']:
                failed_stations.append(f"{station_id} (no data)")
                continue
            
            # Get station metadata
            metadata = data.get('metadata', {})
            station_name = metadata.get('name', f'Station {station_id}')
            lat = metadata.get('lat')
            lon = metadata.get('lon')
            
            # Process data points
            for point in data['data']:
                try:
                    # Store as metric data
                    store_metric_data(
                        timestamp=point.get('t'),
                        provider_key='noaa_ocean',
                        dataset='oceanographic',
                        metric_name=product,
                        value=float(point.get('v')),
                        unit='celsius' if product == 'water_temperature' else 'meters',
                        location_lat=float(lat) if lat else None,
                        location_lng=float(lon) if lon else None,
                        metadata={
                            'station_id': station_id,
                            'station_name': station_name,
                            'product': product,
                            'quality': point.get('q', 'good')
                        }
                    )
                    records_stored += 1
                except (ValueError, TypeError) as e:
                    continue  # Skip malformed records
                    
        except requests.exceptions.RequestException as e:
            failed_stations.append(f"{station_id} (API error: {str(e)})")
            continue
        except Exception as e:
            failed_stations.append(f"{station_id} (processing error: {str(e)})")
            continue
    
    # Build result message
    if records_stored == 0:
        return {
            'success': False,
            'message': f'No ocean data retrieved from NOAA stations. Failed stations: {", ".join(failed_stations)}',
            'records_stored': 0
        }
    
    success_msg = f'Successfully fetched {records_stored} {product} measurements from {len(stations) - len(failed_stations)} NOAA stations'
    if failed_stations:
        success_msg += f'. Failed: {", ".join(failed_stations)}'
    
    return {
        'success': True,
        'message': success_msg,
        'records_stored': records_stored
    }

def _get_default_stations() -> List[str]:
    """
    Get default NOAA station IDs for major coastal areas
    """
    return [
        '8518750',  # The Battery, NY
        '8571421',  # Lewes, DE  
        '8665530',  # Charleston, SC
        '8724580',  # Key West, FL
        '8760922',  # St. Petersburg, FL
        '8771013',  # Galveston Pier 21, TX
        '9410170',  # San Diego, CA
        '9414290',  # San Francisco, CA
        '9447130',  # Seattle, WA
        '1612340',  # Honolulu, HI
        '8461490',  # New London, CT
        '8467150'   # Bridgeport, CT
    ]



if __name__ == "__main__":
    # Test the function
    result = fetch_noaa_ocean_data()
    print(f"Result: {result}") 
