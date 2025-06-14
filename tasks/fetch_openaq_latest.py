#!/usr/bin/env python3
"""
OpenAQ Air Quality Data Fetcher
Fetches latest air quality data from OpenAQ API
"""

import os
import requests
import json
from datetime import datetime
from typing import Dict, Any, List, Optional
from database.db import store_metric_data

def fetch_openaq_latest(limit: int = 1000, parameter: str = 'pm25') -> Dict[str, Any]:
    """
    Fetch latest air quality data from OpenAQ API
    
    Args:
        limit: Maximum number of measurements to fetch
        parameter: Air quality parameter ('pm25', 'pm10', 'o3', 'no2', 'so2', 'co')
    
    Returns:
        Dictionary with success status and message
    """
    api_key = os.getenv('OPENAQ_API_KEY')
    
    if not api_key:
        return {
            'success': False,
            'message': 'OpenAQ API key not configured. Set OPENAQ_API_KEY environment variable.',
            'records_stored': 0
        }
    
    # OpenAQ API v2 endpoint
    url = 'https://api.openaq.org/v2/latest'
    
    headers = {
        'X-API-Key': api_key,
        'Accept': 'application/json'
    }
    
    params = {
        'limit': min(limit, 10000),  # API limit
        'parameter': parameter,
        'has_geo': 'true'  # Only include measurements with coordinates
    }
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        
        if 'results' not in data or not data['results']:
            return {
                'success': False,
                'message': f'No air quality data available from OpenAQ API for parameter: {parameter}',
                'records_stored': 0
            }
        
        results = data['results']
        records_stored = 0
        current_time = datetime.utcnow().isoformat()
        
        # Process each measurement
        for result in results:
            try:
                # Extract latest measurement for the parameter
                measurements = result.get('measurements', [])
                for measurement in measurements:
                    if measurement.get('parameter') == parameter:
                        # Get coordinates
                        coordinates = result.get('coordinates', {})
                        if not coordinates:
                            continue
                        
                        # Store as metric data
                        store_metric_data(
                            timestamp=measurement.get('lastUpdated', current_time),
                            provider_key='openaq',
                            dataset='air_quality',
                            metric_name=f'air_quality_{parameter}',
                            value=float(measurement.get('value')),
                            unit=measurement.get('unit'),
                            location_lat=float(coordinates.get('latitude')),
                            location_lng=float(coordinates.get('longitude')),
                            metadata={
                                'parameter': measurement.get('parameter'),
                                'location': result.get('location'),
                                'city': result.get('city'),
                                'country': result.get('country'),
                                'source_name': 'OpenAQ'
                            }
                        )
                        records_stored += 1
                        break  # Only store one measurement per location
                        
            except (KeyError, TypeError, ValueError) as e:
                continue  # Skip malformed records
        
        return {
            'success': True,
            'message': f'Successfully fetched {records_stored} air quality measurements for {parameter} from OpenAQ',
            'records_stored': records_stored
        }
        
    except requests.exceptions.RequestException as e:
        return {
            'success': False,
            'message': f'Failed to fetch OpenAQ data: {str(e)}',
            'records_stored': 0
        }
    except Exception as e:
        return {
            'success': False,
            'message': f'Error processing OpenAQ data: {str(e)}',
            'records_stored': 0
        }

if __name__ == "__main__":
    # Test the function
    result = fetch_openaq_latest()
    print(f"Result: {result}") 
