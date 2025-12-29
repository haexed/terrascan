#!/usr/bin/env python3
"""
NOAA Space Weather Aurora Fetcher
Fetches aurora forecast data from NOAA SWPC OVATION model
Free API - no key required!
"""

import requests
from datetime import datetime
from typing import Dict, Any
from database.db import store_metric_data, execute_query

# NOAA SWPC endpoints
AURORA_URL = "https://services.swpc.noaa.gov/json/ovation_aurora_latest.json"
KP_INDEX_URL = "https://services.swpc.noaa.gov/products/noaa-planetary-k-index.json"

def fetch_noaa_aurora(**kwargs) -> Dict[str, Any]:
    """
    Fetch aurora forecast and Kp index from NOAA Space Weather Prediction Center

    The OVATION model provides aurora probability/intensity on a 1-degree grid.
    We filter to only store points with significant aurora activity (>= threshold).

    Returns:
        Dictionary with success status and message
    """
    try:
        records_stored = 0

        # Fetch Kp index first (geomagnetic activity indicator)
        kp_response = requests.get(KP_INDEX_URL, timeout=30)
        kp_response.raise_for_status()
        kp_data = kp_response.json()

        # Get latest Kp value (skip header row)
        if len(kp_data) > 1:
            latest_kp = kp_data[-1]  # Most recent reading
            kp_value = float(latest_kp[1])
            kp_time = latest_kp[0]

            store_metric_data(
                timestamp=kp_time.replace(' ', 'T') + 'Z',
                provider_key='noaa_swpc',
                dataset='space_weather',
                metric_name='kp_index',
                value=kp_value,
                unit='index',
                location_lat=None,
                location_lng=None,
                metadata={
                    'a_running': float(latest_kp[2]),
                    'station_count': int(latest_kp[3]),
                    'source': 'NOAA SWPC',
                    'description': 'Planetary K-index (0-9 scale)'
                }
            )
            records_stored += 1

        # Fetch aurora forecast data
        aurora_response = requests.get(AURORA_URL, timeout=60)
        aurora_response.raise_for_status()
        aurora_data = aurora_response.json()

        observation_time = aurora_data.get('Observation Time', datetime.utcnow().isoformat())
        forecast_time = aurora_data.get('Forecast Time', observation_time)
        coordinates = aurora_data.get('coordinates', [])

        # Filter and store only significant aurora points (intensity >= 5)
        # This reduces ~65,000 points to a manageable number
        aurora_threshold = 5
        aurora_points = []

        for coord in coordinates:
            lon, lat, intensity = coord
            if intensity >= aurora_threshold:
                aurora_points.append({
                    'lon': lon if lon <= 180 else lon - 360,  # Convert 0-360 to -180-180
                    'lat': lat,
                    'intensity': intensity
                })

        # Clear old aurora data before inserting new (it's a forecast, not historical)
        execute_query("""
            DELETE FROM metric_data
            WHERE provider_key = 'noaa_swpc'
            AND metric_name = 'aurora_forecast'
        """)

        # Store aurora points
        for point in aurora_points:
            store_metric_data(
                timestamp=forecast_time,
                provider_key='noaa_swpc',
                dataset='space_weather',
                metric_name='aurora_forecast',
                value=float(point['intensity']),
                unit='probability',
                location_lat=point['lat'],
                location_lng=point['lon'],
                metadata={
                    'observation_time': observation_time,
                    'forecast_time': forecast_time,
                    'source': 'NOAA SWPC OVATION Model'
                }
            )
            records_stored += 1

        # Determine aurora visibility status based on Kp
        kp_status = get_kp_status(kp_value) if 'kp_value' in dir() else 'Unknown'

        return {
            'success': True,
            'message': f'Fetched aurora data: {len(aurora_points)} active points (intensity >= {aurora_threshold}), Kp index: {kp_value:.1f} ({kp_status})',
            'records_stored': records_stored,
            'kp_index': kp_value if 'kp_value' in dir() else None,
            'aurora_points': len(aurora_points)
        }

    except requests.exceptions.RequestException as e:
        return {
            'success': False,
            'message': f'API request failed: {str(e)}',
            'records_stored': 0
        }
    except Exception as e:
        return {
            'success': False,
            'message': f'Error: {str(e)}',
            'records_stored': 0
        }


def get_kp_status(kp: float) -> str:
    """Get human-readable Kp status"""
    if kp >= 8:
        return 'Extreme Storm'
    elif kp >= 7:
        return 'Severe Storm'
    elif kp >= 6:
        return 'Strong Storm'
    elif kp >= 5:
        return 'Minor Storm'
    elif kp >= 4:
        return 'Active'
    elif kp >= 3:
        return 'Unsettled'
    else:
        return 'Quiet'


if __name__ == "__main__":
    result = fetch_noaa_aurora()
    print(f"Result: {result}")
