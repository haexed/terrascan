#!/usr/bin/env python3
"""
OpenAQ Air Quality Data Fetcher
Fetches latest air quality data from OpenAQ API v3
"""

import os
import requests
import json
from datetime import datetime
from typing import Dict, Any, List, Optional
from database.db import store_metric_data

def fetch_openaq_latest(limit: int = 1000, parameter: str = 'pm25', bbox: Dict[str, float] = None) -> Dict[str, Any]:
    """
    Fetch latest air quality data from OpenAQ API v3

    Args:
        limit: Maximum number of measurements to fetch
        parameter: Air quality parameter ('pm25', 'pm10', 'o3', 'no2', 'so2', 'co')
        bbox: Optional bounding box {'south': float, 'west': float, 'north': float, 'east': float}

    Returns:
        Dictionary with success status and message
    """
    # Prefer WAQI (World Air Quality Index) - more reliable free tier
    waqi_token = os.getenv('WORLD_AQI_API_KEY')
    if waqi_token:
        return _fetch_from_waqi(waqi_token, limit, bbox)

    # Fallback to OpenAQ if configured
    api_key = os.getenv('OPENAQ_API_KEY')
    if api_key:
        return _fetch_from_openaq_v3(api_key, limit, parameter, bbox)

    return {
        'success': False,
        'message': 'No air quality API configured. Set WORLD_AQI_API_KEY or OPENAQ_API_KEY environment variable.',
        'records_stored': 0
    }

def _fetch_from_waqi(token: str, limit: int, bbox: Dict[str, float] = None) -> Dict[str, Any]:
    """Fetch air quality from World AQI (aqicn.org) - more reliable free tier"""

    # WAQI doesn't have a bulk endpoint, so we'll query major cities
    # For bbox queries, we'd need their map bounds API

    if bbox:
        # Use map bounds query
        url = f"https://api.waqi.info/map/bounds/?token={token}&latlng={bbox['south']},{bbox['west']},{bbox['north']},{bbox['east']}"
    else:
        # Get global data using world bbox
        # WAQI map bounds API returns all stations in the bounding box
        url = f"https://api.waqi.info/map/bounds/?token={token}&latlng=-60,-180,60,180"

    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        data = response.json()

        if data.get('status') != 'ok':
            return {
                'success': False,
                'message': f'WAQI API error: {data.get("data", "Unknown error")}',
                'records_stored': 0
            }

        records_stored = 0
        stations = data.get('data', []) if isinstance(data.get('data'), list) else [data.get('data')]

        for station in stations[:limit]:
            if not isinstance(station, dict):
                continue

            # Get coordinates
            lat = station.get('lat')
            lon = station.get('lon')

            if lat is None or lon is None:
                continue

            # Get AQI value (if no PM2.5 specific, use overall AQI as proxy)
            aqi_value = station.get('aqi')
            if aqi_value is None or aqi_value == '-':
                continue

            # Convert AQI string to number
            try:
                aqi_num = float(aqi_value)
            except (ValueError, TypeError):
                continue

            # Rough conversion: AQI to PM2.5 (µg/m³)
            # AQI 0-50 = PM2.5 0-12, AQI 51-100 = PM2.5 12-35, etc.
            if aqi_num <= 50:
                pm25_estimate = aqi_num * 12 / 50
            elif aqi_num <= 100:
                pm25_estimate = 12 + (aqi_num - 50) * 23 / 50
            elif aqi_num <= 150:
                pm25_estimate = 35 + (aqi_num - 100) * 20 / 50
            else:
                pm25_estimate = 55 + (aqi_num - 150) * 95 / 100

            # Store measurement
            store_metric_data(
                timestamp=station.get('station', {}).get('time', datetime.utcnow().isoformat()),
                provider_key='openaq',
                dataset='air_quality',
                metric_name='air_quality_pm25',
                value=float(pm25_estimate),
                unit='µg/m³ (estimated)',
                location_lat=float(lat),
                location_lng=float(lon),
                metadata={
                    'station_name': station.get('station', {}).get('name'),
                    'aqi': aqi_value,
                    'source_name': 'World AQI (WAQI)'
                }
            )
            records_stored += 1

        return {
            'success': True,
            'message': f'Successfully fetched {records_stored} air quality measurements from WAQI',
            'records_stored': records_stored
        }

    except Exception as e:
        return {
            'success': False,
            'message': f'Failed to fetch WAQI data: {str(e)}',
            'records_stored': 0
        }

def _fetch_from_openaq_v3(api_key: str, limit: int, parameter: str, bbox: Dict[str, float] = None) -> Dict[str, Any]:
    """Fallback: Try OpenAQ v3 (limited free tier)"""

    url = 'https://api.openaq.org/v3/locations'

    headers = {
        'X-API-Key': api_key,
        'Accept': 'application/json'
    }

    param_id_map = {'pm25': 2, 'pm10': 1, 'o3': 3, 'no2': 4, 'so2': 5, 'co': 6}
    param_id = param_id_map.get(parameter, 2)

    params = {
        'limit': min(limit, 100),  # Free tier is very limited
        'radius': 25000,  # 25km radius search
        'coordinates': '0,0'  # Will be overridden if bbox provided
    }

    if bbox:
        center_lat = (bbox['north'] + bbox['south']) / 2
        center_lng = (bbox['east'] + bbox['west']) / 2
        params['coordinates'] = f"{center_lat},{center_lng}"

    try:
        response = requests.get(url, headers=headers, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()

        if 'results' not in data:
            return {
                'success': False,
                'message': 'OpenAQ v3 API returned no results (free tier may be exhausted)',
                'records_stored': 0
            }

        return {
            'success': False,
            'message': 'OpenAQ v3 free tier is limited. Please set WORLD_AQI_API_KEY for air quality data.',
            'records_stored': 0
        }

    except Exception as e:
        return {
            'success': False,
            'message': f'OpenAQ v3 error: {str(e)}. Recommend using WORLD_AQI_API_KEY instead.',
            'records_stored': 0
        }

if __name__ == "__main__":
    # Test the function
    result = fetch_openaq_latest()
    print(f"Result: {result}")
