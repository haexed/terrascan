#!/usr/bin/env python3
"""
Conflict data collection from UCDP (Uppsala Conflict Data Program)
Collects georeferenced conflict events, battle deaths, and violence metrics
Free API - No key required
"""

import requests
import json
from datetime import datetime, timedelta
from database.db import store_metric_data, get_latest_timestamp
from database.config_manager import get_provider_config

def fetch_ucdp_conflicts(product='conflict_events', **kwargs):
    """
    Fetch conflict data from UCDP API

    Args:
        product: Type of conflict data ('conflict_events', 'battle_deaths', 'all')
        **kwargs: Additional parameters

    Returns:
        dict: Task execution result with success status and data
    """

    try:
        timeout = get_provider_config('ucdp', 'timeout_seconds', 30)

        # UCDP GED (Georeferenced Event Dataset) API
        # Version 25.1 is current as of 2025
        base_url = "https://ucdpapi.pcr.uu.se/api/gedevents/25.1"

        records_processed = 0
        total_deaths = 0
        total_events = 0

        # Get events from last 365 days (UCDP updates annually but has recent data)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365)

        # Fetch recent conflict events globally
        params = {
            'pagesize': 1000,  # Max allowed
            'StartDate': start_date.strftime('%Y-%m-%d'),
            'EndDate': end_date.strftime('%Y-%m-%d')
        }

        print(f"Fetching UCDP conflict events from {start_date.date()} to {end_date.date()}...")

        response = requests.get(base_url, params=params, timeout=timeout)
        response.raise_for_status()

        data = response.json()

        if 'Result' in data and data['Result']:
            events = data['Result']
            total_events = len(events)

            print(f"Retrieved {total_events} conflict events")

            # Process each event
            for event in events:
                try:
                    # Extract event data
                    event_id = event.get('id', 0)
                    latitude = event.get('latitude')
                    longitude = event.get('longitude')

                    if not latitude or not longitude:
                        continue

                    # Deaths estimates (best, low, high)
                    deaths_best = event.get('best', 0) or 0
                    deaths_low = event.get('low', 0) or 0
                    deaths_high = event.get('high', 0) or 0
                    total_deaths += deaths_best

                    # Event metadata
                    event_date = event.get('date_start', '')
                    country = event.get('country', 'Unknown')
                    region = event.get('region', 'Unknown')

                    # Type of violence: 1=state-based, 2=non-state, 3=one-sided
                    violence_type = event.get('type_of_violence', 0)
                    violence_labels = {
                        1: 'state_conflict',
                        2: 'non_state_conflict',
                        3: 'one_sided_violence'
                    }
                    violence_label = violence_labels.get(violence_type, 'unknown')

                    # Actors involved
                    side_a = event.get('side_a', 'Unknown')
                    side_b = event.get('side_b', 'Unknown')

                    # Conflict name
                    conflict_name = event.get('conflict_name', 'Unknown Conflict')

                    # Source information
                    source_article = event.get('source_article', '')

                    # Use event date if available, otherwise current time
                    if event_date:
                        timestamp = event_date
                    else:
                        timestamp = datetime.now().isoformat()

                    # Store as conflict event metric
                    store_metric_data(
                        timestamp=timestamp,
                        provider_key='ucdp',
                        dataset='conflicts',
                        metric_name='conflict_event',
                        value=deaths_best,  # Deaths as primary value
                        unit='deaths',
                        location_lat=float(latitude),
                        location_lng=float(longitude),
                        metadata={
                            'event_id': event_id,
                            'conflict_name': conflict_name,
                            'violence_type': violence_label,
                            'side_a': side_a,
                            'side_b': side_b,
                            'deaths_low': deaths_low,
                            'deaths_high': deaths_high,
                            'country': country,
                            'region': region,
                            'source': source_article[:200] if source_article else ''
                        }
                    )

                    records_processed += 1

                except Exception as e:
                    print(f"Error processing event {event.get('id', 'unknown')}: {e}")
                    continue

            # Also store summary metrics
            # Active conflicts count (unique conflict names)
            unique_conflicts = len(set(e.get('conflict_name', '') for e in events if e.get('conflict_name')))

            store_metric_data(
                timestamp=datetime.now().isoformat(),
                provider_key='ucdp',
                dataset='conflicts',
                metric_name='active_conflicts',
                value=unique_conflicts,
                unit='conflicts',
                location_lat=0,
                location_lng=0,
                metadata={
                    'total_events': total_events,
                    'total_deaths': total_deaths,
                    'period_days': 365,
                    'region': 'Global'
                }
            )
            records_processed += 1

            # Countries with conflicts
            conflict_countries = len(set(e.get('country', '') for e in events if e.get('country')))

            store_metric_data(
                timestamp=datetime.now().isoformat(),
                provider_key='ucdp',
                dataset='conflicts',
                metric_name='conflict_countries',
                value=conflict_countries,
                unit='countries',
                location_lat=0,
                location_lng=0,
                metadata={
                    'countries': list(set(e.get('country', '') for e in events if e.get('country')))[:20],
                    'region': 'Global'
                }
            )
            records_processed += 1

        print(f"UCDP: Processed {records_processed} records, {total_events} events, {total_deaths} estimated deaths")

        return {
            'success': True,
            'records_processed': records_processed,
            'message': f'Collected {total_events} conflict events with {total_deaths} estimated deaths from {start_date.date()} to {end_date.date()}'
        }

    except requests.exceptions.Timeout:
        return {
            'success': False,
            'records_processed': 0,
            'error': 'UCDP API timeout'
        }
    except requests.exceptions.RequestException as e:
        return {
            'success': False,
            'records_processed': 0,
            'error': f'UCDP API error: {str(e)}'
        }
    except Exception as e:
        return {
            'success': False,
            'records_processed': 0,
            'error': f'Unexpected error: {str(e)}'
        }


if __name__ == '__main__':
    # Test the fetcher
    result = fetch_ucdp_conflicts()
    print(f"\nResult: {result}")
