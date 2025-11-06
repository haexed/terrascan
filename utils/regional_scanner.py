#!/usr/bin/env python3
"""
Regional Scanner - Smart lazy-loading for Terrascan
Handles "scan as you go" functionality for map exploration
"""

from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from database.db import execute_query, get_db_connection


class RegionalScanner:
    """
    Manages regional data scanning and caching
    Coordinates between map requests and data fetchers
    """

    # Data freshness requirements (hours)
    FRESHNESS_REQUIREMENTS = {
        'fires': 3,         # Fast-moving, refresh often
        'air': 12,          # Moderate, twice daily
        'ocean': 168,       # Slow-changing, weekly
        'weather': 6,       # Regular updates
        'species': 720      # Very stable, monthly
    }

    def __init__(self):
        self.conn = None

    def check_region_cached(self, bbox: Dict[str, float], zoom: int,
                           layers: List[str]) -> Dict:
        """
        Check if a region has cached data that's fresh enough

        Args:
            bbox: {'north': float, 'south': float, 'east': float, 'west': float}
            zoom: Map zoom level
            layers: List of layer names to check ['fires', 'air', 'ocean']

        Returns:
            {
                'cached': bool,
                'layers_available': [...],
                'layers_needed': [...],
                'freshness_status': {...}
            }
        """
        # Query for overlapping regions
        query = """
            SELECT * FROM check_region_overlap(
                %s, %s, %s, %s, %s, %s
            )
        """

        # Get maximum age requirement from the layers being requested
        max_age_hours = max([self.FRESHNESS_REQUIREMENTS.get(layer, 24)
                            for layer in layers])

        results = execute_query(query, (
            bbox['north'], bbox['south'], bbox['east'],
            bbox['west'], zoom, max_age_hours
        ))

        if not results or len(results) == 0:
            return {
                'cached': False,
                'layers_available': [],
                'layers_needed': layers,
                'freshness_status': {},
                'reason': 'no_cached_regions'
            }

        # Check which layers are available and fresh
        available_layers = set()
        freshness_status = {}

        for region in results:
            cached_layers = region.get('layers_scanned', []) or []
            last_updated = region.get('last_updated')

            for layer in cached_layers:
                if layer in layers:
                    # Check if this layer is still fresh enough
                    required_freshness = self.FRESHNESS_REQUIREMENTS.get(layer, 24)
                    age_hours = (datetime.utcnow() - last_updated).total_seconds() / 3600

                    if age_hours <= required_freshness:
                        available_layers.add(layer)
                        freshness_status[layer] = {
                            'fresh': True,
                            'age_hours': round(age_hours, 1),
                            'max_age': required_freshness
                        }
                    else:
                        freshness_status[layer] = {
                            'fresh': False,
                            'age_hours': round(age_hours, 1),
                            'max_age': required_freshness,
                            'reason': 'stale_data'
                        }

        layers_needed = [l for l in layers if l not in available_layers]

        return {
            'cached': len(layers_needed) == 0,
            'layers_available': list(available_layers),
            'layers_needed': layers_needed,
            'freshness_status': freshness_status,
            'cached_regions': len(results)
        }

    def record_scan(self, bbox: Dict[str, float], zoom: int,
                   layers: List[str], data_points: int,
                   triggered_by: str = 'user') -> int:
        """
        Record a completed scan in the database

        Returns:
            scan_id: ID of the recorded scan
        """
        query = """
            INSERT INTO scanned_regions (
                bbox_north, bbox_south, bbox_east, bbox_west,
                zoom_level, layers_scanned, data_points_cached,
                scan_triggered_by, first_scanned, last_updated
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
            RETURNING id
        """

        results = execute_query(query, (
            bbox['north'], bbox['south'], bbox['east'], bbox['west'],
            zoom, layers, data_points, triggered_by
        ))

        return results[0]['id'] if results else None

    def update_scan(self, scan_id: int, additional_data_points: int):
        """Update an existing scan with more data points"""
        query = """
            UPDATE scanned_regions
            SET data_points_cached = data_points_cached + %s,
                last_updated = NOW()
            WHERE id = %s
        """
        execute_query(query, (additional_data_points, scan_id))

    def get_cached_data(self, bbox: Dict[str, float], layers: List[str]) -> Dict:
        """
        Retrieve cached data for a region from metric_data table

        Returns:
            {
                'fires': [...],
                'air': [...],
                'ocean': [...],
                etc.
            }
        """
        data = {}

        layer_queries = {
            'fires': """
                SELECT location_lat as latitude, location_lng as longitude,
                       value as brightness, timestamp as acq_date, metadata
                FROM metric_data
                WHERE provider_key = 'nasa_firms'
                AND location_lat BETWEEN %s AND %s
                AND location_lng BETWEEN %s AND %s
                AND timestamp > NOW() - INTERVAL '24 hours'
                AND value > 300
                ORDER BY timestamp DESC
                LIMIT 1000
            """,
            'air': """
                SELECT location_lat as latitude, location_lng as longitude,
                       AVG(value) as value, MAX(metadata) as metadata,
                       MAX(timestamp) as last_updated
                FROM metric_data
                WHERE provider_key = 'openaq'
                AND metric_name = 'air_quality_pm25'
                AND location_lat BETWEEN %s AND %s
                AND location_lng BETWEEN %s AND %s
                AND timestamp > NOW() - INTERVAL '7 days'
                GROUP BY location_lat, location_lng
                ORDER BY value DESC
                LIMIT 500
            """,
            'ocean': """
                SELECT location_lat as latitude, location_lng as longitude,
                       AVG(CASE WHEN metric_name = 'water_temperature' THEN value END) as temperature,
                       MAX(metadata) as metadata
                FROM metric_data
                WHERE provider_key = 'noaa_ocean'
                AND location_lat BETWEEN %s AND %s
                AND location_lng BETWEEN %s AND %s
                AND timestamp > NOW() - INTERVAL '7 days'
                GROUP BY location_lat, location_lng
                LIMIT 100
            """
        }

        for layer in layers:
            if layer in layer_queries:
                result = execute_query(
                    layer_queries[layer],
                    (bbox['south'], bbox['north'], bbox['west'], bbox['east'])
                )
                data[layer] = result or []

        return data

    def get_scan_statistics(self) -> Dict:
        """Get global scanning statistics"""
        query = "SELECT * FROM get_scan_statistics()"
        results = execute_query(query)
        return results[0] if results else {}

    def get_popular_regions(self, limit: int = 10) -> List[Dict]:
        """Get most frequently scanned regions for prefetching"""
        query = """
            SELECT bbox_north, bbox_south, bbox_east, bbox_west,
                   COUNT(*) as scan_count,
                   MAX(last_updated) as most_recent_scan
            FROM scanned_regions
            GROUP BY bbox_north, bbox_south, bbox_east, bbox_west
            ORDER BY scan_count DESC
            LIMIT %s
        """
        return execute_query(query, (limit,)) or []


# Singleton instance
_scanner = None

def get_scanner() -> RegionalScanner:
    """Get the global scanner instance"""
    global _scanner
    if _scanner is None:
        _scanner = RegionalScanner()
    return _scanner
