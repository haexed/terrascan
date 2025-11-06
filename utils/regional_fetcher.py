#!/usr/bin/env python3
"""
Regional Fetcher - Coordinates fetching data for specific regions
Calls the appropriate task fetchers with bbox parameters
"""

from typing import Dict, List
import importlib


class RegionalFetcher:
    """Fetches environmental data for specific geographic regions"""

    # Mapping of layer names to fetcher modules and functions
    LAYER_FETCHERS = {
        'fires': {
            'module': 'tasks.fetch_nasa_fires',
            'function': 'fetch_nasa_fires',
            'params': {'days': 3}  # Recent fires only for regional scans
        },
        'air': {
            'module': 'tasks.fetch_openaq_latest',
            'function': 'fetch_openaq_latest',
            'params': {'limit': 500}
        },
        # Add more as we enhance them
        # 'ocean': {
        #     'module': 'tasks.fetch_noaa_ocean',
        #     'function': 'fetch_noaa_ocean',
        #     'params': {}
        # },
    }

    def fetch_region(self, bbox: Dict[str, float], layers: List[str]) -> Dict:
        """
        Fetch data for a specific region

        Args:
            bbox: Bounding box with north, south, east, west
            layers: List of layer names to fetch

        Returns:
            {
                'fires': {'success': bool, 'records': int, ...},
                'air': {...},
                'total_records': int
            }
        """
        results = {}
        total_records = 0

        for layer in layers:
            if layer not in self.LAYER_FETCHERS:
                results[layer] = {
                    'success': False,
                    'error': f'Unknown layer: {layer}',
                    'records_stored': 0
                }
                continue

            fetcher_config = self.LAYER_FETCHERS[layer]

            try:
                # Dynamically import the fetcher module
                module = importlib.import_module(fetcher_config['module'])
                fetch_function = getattr(module, fetcher_config['function'])

                # Call fetcher with bbox and additional params
                params = {**fetcher_config['params'], 'bbox': bbox}
                result = fetch_function(**params)

                results[layer] = result
                total_records += result.get('records_stored', 0)

            except Exception as e:
                results[layer] = {
                    'success': False,
                    'error': str(e),
                    'records_stored': 0
                }

        results['total_records'] = total_records
        return results


# Singleton instance
_fetcher = None


def get_regional_fetcher() -> RegionalFetcher:
    """Get the global fetcher instance"""
    global _fetcher
    if _fetcher is None:
        _fetcher = RegionalFetcher()
    return _fetcher
