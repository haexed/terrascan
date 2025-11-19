#!/usr/bin/env python3
"""
Open-Meteo Marine Data Fetcher
Fetches sea surface temperature and wave data from Open-Meteo API
Free API - no key required!
"""

import requests
from datetime import datetime
from typing import Dict, Any, List
from database.db import store_metric_data

def fetch_openmeteo_marine(locations: List[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Fetch marine data from Open-Meteo API

    Args:
        locations: List of dicts with 'lat', 'lon', 'name' keys
                  Uses default ocean points if None

    Returns:
        Dictionary with success status and message
    """
    if locations is None:
        locations = _get_default_ocean_points()

    base_url = "https://marine-api.open-meteo.com/v1/marine"

    records_stored = 0
    failed_locations = []

    for loc in locations:
        try:
            params = {
                'latitude': loc['lat'],
                'longitude': loc['lon'],
                'current': 'sea_surface_temperature,ocean_current_velocity,wave_height,wave_direction,wave_period',
                'timezone': 'UTC'
            }

            response = requests.get(base_url, params=params, timeout=30)
            response.raise_for_status()

            data = response.json()
            current = data.get('current', {})

            if not current:
                failed_locations.append(f"{loc['name']} (no data)")
                continue

            timestamp = current.get('time', datetime.utcnow().strftime('%Y-%m-%dT%H:%M'))

            # Store sea surface temperature
            sst = current.get('sea_surface_temperature')
            if sst is not None:
                store_metric_data(
                    timestamp=timestamp,
                    provider_key='openmeteo_marine',
                    dataset='marine',
                    metric_name='sea_surface_temperature',
                    value=float(sst),
                    unit='celsius',
                    location_lat=loc['lat'],
                    location_lng=loc['lon'],
                    metadata={
                        'location_name': loc['name'],
                        'source': 'open-meteo'
                    }
                )
                records_stored += 1

            # Store wave height
            wave_height = current.get('wave_height')
            if wave_height is not None:
                store_metric_data(
                    timestamp=timestamp,
                    provider_key='openmeteo_marine',
                    dataset='marine',
                    metric_name='wave_height',
                    value=float(wave_height),
                    unit='meters',
                    location_lat=loc['lat'],
                    location_lng=loc['lon'],
                    metadata={
                        'location_name': loc['name'],
                        'wave_direction': current.get('wave_direction'),
                        'wave_period': current.get('wave_period'),
                        'source': 'open-meteo'
                    }
                )
                records_stored += 1

            # Store ocean current velocity
            current_velocity = current.get('ocean_current_velocity')
            if current_velocity is not None:
                store_metric_data(
                    timestamp=timestamp,
                    provider_key='openmeteo_marine',
                    dataset='marine',
                    metric_name='ocean_current_velocity',
                    value=float(current_velocity),
                    unit='m/s',
                    location_lat=loc['lat'],
                    location_lng=loc['lon'],
                    metadata={
                        'location_name': loc['name'],
                        'source': 'open-meteo'
                    }
                )
                records_stored += 1

        except requests.exceptions.RequestException as e:
            failed_locations.append(f"{loc['name']} (API error)")
            continue
        except Exception as e:
            failed_locations.append(f"{loc['name']} (error: {str(e)[:50]})")
            continue

    if records_stored == 0:
        return {
            'success': False,
            'message': f'No marine data retrieved. Failed: {", ".join(failed_locations)}',
            'records_stored': 0
        }

    msg = f'Successfully fetched {records_stored} marine measurements from {len(locations) - len(failed_locations)} locations'
    if failed_locations:
        msg += f'. Failed: {", ".join(failed_locations)}'

    return {
        'success': True,
        'message': msg,
        'records_stored': records_stored
    }

def _get_default_ocean_points() -> List[Dict[str, Any]]:
    """
    Get default ocean monitoring points globally
    Spread across major oceans for global coverage
    """
    return [
        # Atlantic Ocean
        {'lat': 25.0, 'lon': -40.0, 'name': 'North Atlantic'},
        {'lat': -15.0, 'lon': -25.0, 'name': 'South Atlantic'},
        {'lat': 40.0, 'lon': -30.0, 'name': 'North Atlantic (Azores)'},

        # Pacific Ocean
        {'lat': 0.0, 'lon': -140.0, 'name': 'Central Pacific'},
        {'lat': 20.0, 'lon': -155.0, 'name': 'Hawaii Region'},
        {'lat': -10.0, 'lon': 165.0, 'name': 'South Pacific'},
        {'lat': 35.0, 'lon': 140.0, 'name': 'Japan Coast'},
        {'lat': -35.0, 'lon': -120.0, 'name': 'Southeast Pacific'},

        # Indian Ocean
        {'lat': -10.0, 'lon': 70.0, 'name': 'Central Indian Ocean'},
        {'lat': -30.0, 'lon': 80.0, 'name': 'South Indian Ocean'},

        # Arctic/Antarctic
        {'lat': 70.0, 'lon': 0.0, 'name': 'Norwegian Sea'},
        {'lat': -60.0, 'lon': 0.0, 'name': 'Southern Ocean'},

        # Mediterranean & Regional Seas
        {'lat': 35.0, 'lon': 18.0, 'name': 'Mediterranean'},
        {'lat': 55.0, 'lon': 10.0, 'name': 'North Sea'},
        {'lat': 25.0, 'lon': 55.0, 'name': 'Arabian Sea'},

        # Caribbean & Gulf
        {'lat': 18.0, 'lon': -65.0, 'name': 'Caribbean'},
        {'lat': 25.0, 'lon': -90.0, 'name': 'Gulf of Mexico'},

        # Coral Triangle (biodiversity hotspot)
        {'lat': 0.0, 'lon': 125.0, 'name': 'Coral Triangle'},

        # Additional coverage
        {'lat': 45.0, 'lon': -125.0, 'name': 'Pacific Northwest'},
        {'lat': -20.0, 'lon': 115.0, 'name': 'Western Australia'},
    ]

if __name__ == "__main__":
    result = fetch_openmeteo_marine()
    print(f"Result: {result}")
