#!/usr/bin/env python3
"""
Weather data collection from OpenWeatherMap One Call API 3.0
Collects current weather, forecasts, and weather alerts for major cities
"""

import requests
import json
import time
from datetime import datetime, timedelta
from database.db import execute_query
from database.config_manager import get_provider_config

def fetch_weather_data(product='current', **kwargs):
    """
    Fetch weather data from OpenWeatherMap One Call API 3.0
    
    Args:
        product: Type of weather data ('current', 'forecast', 'historical', 'alerts')
        **kwargs: Additional parameters like city coordinates
    
    Returns:
        dict: Task execution result with success status and data
    """
    
    try:
        # Get API configuration
        api_key = get_provider_config('openweather', 'api_key', None)
        timeout = get_provider_config('openweather', 'timeout_seconds', 30)
        
        if not api_key:
            return {
                'success': False,
                'error': 'OpenWeatherMap API key not configured',
                'records_processed': 0
            }
        
        # Major cities for weather monitoring (expanding your existing coverage)
        cities = [
            # North America
            {'name': 'New York', 'lat': 40.7128, 'lon': -74.0060, 'country': 'US'},
            {'name': 'Los Angeles', 'lat': 34.0522, 'lon': -118.2437, 'country': 'US'},
            {'name': 'Chicago', 'lat': 41.8781, 'lon': -87.6298, 'country': 'US'},
            {'name': 'Toronto', 'lat': 43.6532, 'lon': -79.3832, 'country': 'CA'},
            {'name': 'Mexico City', 'lat': 19.4326, 'lon': -99.1332, 'country': 'MX'},
            
            # Europe
            {'name': 'London', 'lat': 51.5074, 'lon': -0.1278, 'country': 'GB'},
            {'name': 'Paris', 'lat': 48.8566, 'lon': 2.3522, 'country': 'FR'},
            {'name': 'Berlin', 'lat': 52.5200, 'lon': 13.4050, 'country': 'DE'},
            {'name': 'Madrid', 'lat': 40.4168, 'lon': -3.7038, 'country': 'ES'},
            {'name': 'Rome', 'lat': 41.9028, 'lon': 12.4964, 'country': 'IT'},
            
            # Asia
            {'name': 'Tokyo', 'lat': 35.6762, 'lon': 139.6503, 'country': 'JP'},
            {'name': 'Beijing', 'lat': 39.9042, 'lon': 116.4074, 'country': 'CN'},
            {'name': 'Shanghai', 'lat': 31.2304, 'lon': 121.4737, 'country': 'CN'},
            {'name': 'Mumbai', 'lat': 19.0760, 'lon': 72.8777, 'country': 'IN'},
            {'name': 'Seoul', 'lat': 37.5665, 'lon': 126.9780, 'country': 'KR'},
            
            # Middle East & Africa
            {'name': 'Dubai', 'lat': 25.2048, 'lon': 55.2708, 'country': 'AE'},
            {'name': 'Cairo', 'lat': 30.0444, 'lon': 31.2357, 'country': 'EG'},
            {'name': 'Cape Town', 'lat': -33.9249, 'lon': 18.4241, 'country': 'ZA'},
            {'name': 'Nairobi', 'lat': -1.2921, 'lon': 36.8219, 'country': 'KE'},
            
            # South America
            {'name': 'São Paulo', 'lat': -23.5505, 'lon': -46.6333, 'country': 'BR'},
            {'name': 'Buenos Aires', 'lat': -34.6118, 'lon': -58.3960, 'country': 'AR'},
            {'name': 'Lima', 'lat': -12.0464, 'lon': -77.0428, 'country': 'PE'},
            
            # Oceania
            {'name': 'Sydney', 'lat': -33.8688, 'lon': 151.2093, 'country': 'AU'},
            {'name': 'Auckland', 'lat': -36.8485, 'lon': 174.7633, 'country': 'NZ'},
        ]
        
        records_processed = 0
        
        for city in cities:
            try:
                # Build API URL for One Call API 3.0
                base_url = "https://api.openweathermap.org/data/3.0/onecall"
                
                params = {
                    'lat': city['lat'],
                    'lon': city['lon'],
                    'appid': api_key,
                    'units': 'metric',  # Celsius, m/s, etc.
                    'exclude': 'minutely'  # Skip minute-by-minute data to save quota
                }
                
                # Make API request
                response = requests.get(base_url, params=params, timeout=timeout)
                response.raise_for_status()
                
                data = response.json()
                
                # Process current weather
                if 'current' in data and product in ['current', 'all']:
                    current = data['current']
                    
                    # Store current temperature
                    execute_query("""
                        INSERT INTO metric_data 
                        (provider_key, metric_name, value, unit, timestamp, location_lat, location_lng, metadata)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, [
                        'openweather',
                        'temperature',
                        current['temp'],
                        'celsius',
                        datetime.fromtimestamp(current['dt']).isoformat(),
                        city['lat'],
                        city['lon'],
                        json.dumps({
                            'city': city['name'],
                            'country': city['country'],
                            'feels_like': current.get('feels_like'),
                            'humidity': current.get('humidity'),
                            'pressure': current.get('pressure'),
                            'weather': current.get('weather', [{}])[0].get('description', ''),
                            'wind_speed': current.get('wind_speed'),
                            'wind_deg': current.get('wind_deg'),
                            'clouds': current.get('clouds'),
                            'uvi': current.get('uvi'),
                            'visibility': current.get('visibility')
                        })
                    ])
                    
                    # Store humidity
                    if 'humidity' in current:
                        execute_query("""
                            INSERT INTO metric_data 
                            (provider_key, metric_name, value, unit, timestamp, location_lat, location_lng, metadata)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        """, [
                            'openweather',
                            'humidity',
                            current['humidity'],
                            'percent',
                            datetime.fromtimestamp(current['dt']).isoformat(),
                            city['lat'],
                            city['lon'],
                            json.dumps({
                                'city': city['name'],
                                'country': city['country'],
                                'temperature': current.get('temp')
                            })
                        ])
                    
                    # Store wind speed
                    if 'wind_speed' in current:
                        execute_query("""
                            INSERT INTO metric_data 
                            (provider_key, metric_name, value, unit, timestamp, location_lat, location_lng, metadata)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        """, [
                            'openweather',
                            'wind_speed',
                            current['wind_speed'],
                            'meters_per_second',
                            datetime.fromtimestamp(current['dt']).isoformat(),
                            city['lat'],
                            city['lon'],
                            json.dumps({
                                'city': city['name'],
                                'country': city['country'],
                                'wind_direction': current.get('wind_deg'),
                                'wind_gust': current.get('wind_gust')
                            })
                        ])
                    
                    # Store atmospheric pressure
                    if 'pressure' in current:
                        execute_query("""
                            INSERT INTO metric_data 
                            (provider_key, metric_name, value, unit, timestamp, location_lat, location_lng, metadata)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        """, [
                            'openweather',
                            'atmospheric_pressure',
                            current['pressure'],
                            'hpa',
                            datetime.fromtimestamp(current['dt']).isoformat(),
                            city['lat'],
                            city['lon'],
                            json.dumps({
                                'city': city['name'],
                                'country': city['country'],
                                'sea_level': True
                            })
                        ])
                    
                    records_processed += 4  # temp, humidity, wind, pressure
                
                # Process weather alerts
                if 'alerts' in data and product in ['alerts', 'all']:
                    for alert in data['alerts']:
                        execute_query("""
                            INSERT INTO metric_data 
                            (provider_key, metric_name, value, unit, timestamp, location_lat, location_lng, metadata)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        """, [
                            'openweather',
                            'weather_alert',
                            1,  # Alert present
                            'boolean',
                            datetime.fromtimestamp(alert['start']).isoformat(),
                            city['lat'],
                            city['lon'],
                            json.dumps({
                                'city': city['name'],
                                'country': city['country'],
                                'event': alert.get('event'),
                                'sender': alert.get('sender_name'),
                                'description': alert.get('description', '')[:500],  # Truncate long descriptions
                                'start': alert.get('start'),
                                'end': alert.get('end'),
                                'tags': alert.get('tags', [])
                            })
                        ])
                        records_processed += 1
                
                # Small delay to respect API rate limits
                time.sleep(0.1)
                
            except requests.exceptions.RequestException as e:
                print(f"Error fetching weather data for {city['name']}: {str(e)}")
                continue
            except Exception as e:
                print(f"Error processing weather data for {city['name']}: {str(e)}")
                continue
        
        return {
            'success': True,
            'records_processed': records_processed,
            'message': f'Successfully collected weather data for {len(cities)} cities'
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'records_processed': 0
        }

if __name__ == "__main__":
    # Test the weather data collection
    result = fetch_weather_data(product='current')
    print(f"Weather data collection result: {result}") 
