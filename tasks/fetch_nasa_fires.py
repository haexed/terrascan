#!/usr/bin/env python3
"""
NASA FIRMS Fire Data Fetcher
Fetches active fire data from NASA FIRMS API
"""

import os
import requests
from datetime import datetime, timedelta
from typing import Dict, Any, List
from database.db import batch_store_metric_data, get_latest_timestamp

def fetch_nasa_fires(region: str = 'WORLD', days: int = 7) -> Dict[str, Any]:
    """
    Fetch fire detection data from NASA FIRMS API
    
    Args:
        region: Geographic region code ('WORLD', 'NA', 'SA', etc.)
        days: Number of days to look back (1-10)
    
    Returns:
        Dictionary with success status and message
    """
    api_key = os.getenv('NASA_FIRMS_API_KEY')
    
    if not api_key:
        return {
            'success': False,
            'message': 'NASA FIRMS API key not configured. Set NASA_FIRMS_API_KEY environment variable.',
            'records_stored': 0
        }
    
    # Validate days parameter
    if days < 1 or days > 10:
        days = 7
    
    # NASA FIRMS API endpoint for MODIS data
    url = f"https://firms.modaps.eosdis.nasa.gov/api/active_fire/csv/{api_key}/MODIS_NRT/{region}/{days}"
    
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        # Check if we have data
        content = response.text.strip()
        if not content or 'Error' in content:
            return {
                'success': False,
                'message': f'No fire data available from NASA FIRMS API for {region}',
                'records_stored': 0
            }
        
        # Parse CSV data
        lines = content.split('\n')
        if len(lines) < 2:  # Should have header + at least one data row
            return {
                'success': False,
                'message': f'No fire detections found for {region} in the last {days} days',
                'records_stored': 0
            }
            
        header = lines[0].split(',')
        
        # Check latest data we have to avoid re-fetching
        latest_timestamp = get_latest_timestamp('nasa_firms', 'fire_brightness')
        print(f"🔍 Latest NASA FIRMS data: {latest_timestamp}")
        
        # Process each fire detection with actual timestamps
        fire_data_batch = []
        skipped_old = 0
        
        for line in lines[1:]:
            if line.strip():
                try:
                    values = line.split(',')
                    if len(values) >= 15:
                        # Extract key fields
                        lat = float(values[0])
                        lng = float(values[1])
                        brightness = float(values[2])
                        confidence = float(values[9]) / 100.0 if values[9] else 0.5
                        
                        # Build actual timestamp from fire detection time
                        acq_date = values[5]  # YYYY-MM-DD
                        acq_time = values[6]  # HHMM
                        
                        # Parse and format timestamp
                        hour = int(acq_time[:2]) if len(acq_time) >= 2 else 0
                        minute = int(acq_time[2:4]) if len(acq_time) >= 4 else 0
                        
                        fire_timestamp = f"{acq_date}T{hour:02d}:{minute:02d}:00"
                        
                        # Skip if we already have newer data
                        if latest_timestamp and fire_timestamp <= latest_timestamp:
                            skipped_old += 1
                            continue
                        
                        # Add to batch
                        fire_data_batch.append({
                            'provider_key': 'nasa_firms',
                            'metric_name': 'fire_brightness',
                            'value': brightness,
                            'unit': 'kelvin',
                            'location_lat': lat,
                            'location_lng': lng,
                            'timestamp': fire_timestamp,
                            'metadata': {
                                'confidence': confidence,
                                'satellite': values[7],
                                'instrument': values[8],
                                'daynight': values[13],
                                'type': values[14],
                                'scan': values[3],
                                'track': values[4],
                                'frp': values[12],
                                'acq_date': acq_date,
                                'acq_time': acq_time
                            }
                        })
                        
                except (ValueError, IndexError) as e:
                    continue  # Skip malformed records
        
        # Store all fire data in batch with deduplication
        if fire_data_batch:
            batch_result = batch_store_metric_data(fire_data_batch)
            records_stored = batch_result.get('processed', 0)
            
            message = f'NASA FIRMS: {records_stored} new fires processed'
            if skipped_old > 0:
                message += f', {skipped_old} duplicates skipped'
        else:
            records_stored = 0
            message = f'NASA FIRMS: No new fire data (skipped {skipped_old} existing records)'
        
        return {
            'success': True,
            'message': message,
            'records_stored': records_stored
        }
        
    except requests.exceptions.RequestException as e:
        return {
            'success': False,
            'message': f'Failed to fetch NASA FIRMS data: {str(e)}',
            'records_stored': 0
        }
    except Exception as e:
        return {
            'success': False,
            'message': f'Error processing NASA FIRMS data: {str(e)}', 
            'records_stored': 0
        }

if __name__ == "__main__":
    # Test the function
    result = fetch_nasa_fires()
    print(f"Result: {result}") 
