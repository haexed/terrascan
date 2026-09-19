#!/usr/bin/env python3
"""
Seed provider metadata into the database.

This file is the only place provider display metadata is written down. Every
page (footer, /about, /system) and every provider list in the app reads it back
out of `provider_config` via `database/providers.py`.

Idempotent - re-running upserts. Called on startup from setup_configs.py.
"""

import sys

from database.config_manager import set_provider_config
from database.providers import METADATA_KEY

# Keys match the real provider_key values written into metric_data by the tasks.
PROVIDERS = {
    'nasa_firms': {
        'name': 'NASA FIRMS',
        'icon': '🔥',
        'url': 'https://firms.modaps.eosdis.nasa.gov/',
        'tagline': 'Fire Information for Resource Management System',
        'description': 'Real-time fire detection from MODIS and VIIRS satellites.',
        'coverage': 'Global satellite monitoring',
        'update_frequency': 'Every 2 hours',
        'metrics': 'Active fire detections, brightness, confidence',
        'record_label': 'fire detections',
        'tasks': ['nasa_fires_global'],
        'freshness_hours': 3,
        'in_footer': True,
        'sort_order': 1,
    },
    'openaq': {
        'name': 'OpenAQ',
        'icon': '🌬️',
        'url': 'https://openaq.org/',
        'tagline': 'Open Air Quality Data Platform',
        'description': 'Air pollution data aggregated from 10,000+ monitoring stations in 100+ countries.',
        'coverage': '65+ major cities worldwide',
        'update_frequency': 'Every hour',
        'metrics': 'PM2.5, PM10, NO2, O3',
        'record_label': 'air quality measurements',
        'tasks': ['openaq_latest'],
        'freshness_hours': 12,
        'in_footer': True,
        'sort_order': 2,
    },
    'noaa_ocean': {
        'name': 'NOAA Ocean Service',
        'icon': '🌊',
        'url': 'https://tidesandcurrents.noaa.gov/',
        'tagline': 'Ocean and Coastal Data',
        'description': 'Tides and Currents provides real-time water levels and temperatures from coastal monitoring stations.',
        'coverage': '12 major coastal stations',
        'update_frequency': 'Every 3 hours',
        'metrics': 'Water temperature, water level',
        'record_label': 'oceanographic measurements',
        'tasks': ['noaa_ocean_temperature', 'noaa_ocean_water_level'],
        'freshness_hours': 24,
        'in_footer': True,
        'sort_order': 3,
    },
    'openmeteo_marine': {
        'name': 'Open-Meteo',
        'icon': '🌐',
        'url': 'https://open-meteo.com/',
        'tagline': 'Free Weather & Marine API',
        'description': 'Global ocean data including sea surface temperature, waves and currents. Licensed under CC-BY 4.0.',
        'coverage': '20 global ocean points',
        'update_frequency': 'Every 3 hours',
        'metrics': 'Sea surface temp, waves, currents',
        'record_label': 'marine measurements',
        'tasks': ['openmeteo_marine'],
        'freshness_hours': 24,
        'in_footer': True,
        'sort_order': 4,
    },
    'noaa_swpc': {
        'name': 'NOAA Space Weather',
        'icon': '🌌',
        'url': 'https://www.swpc.noaa.gov/',
        'tagline': 'Space Weather Prediction Center',
        'description': 'Aurora forecasts and geomagnetic activity data via the OVATION model.',
        'coverage': 'Global aurora forecast grid',
        'update_frequency': 'Every hour',
        'metrics': 'Aurora probability, Kp index',
        'record_label': 'aurora readings',
        'tasks': ['noaa_aurora'],
        'freshness_hours': 1,
        'in_footer': True,
        'sort_order': 5,
    },
    'ucdp': {
        'name': 'UCDP',
        'icon': '⚔️',
        'url': 'https://ucdp.uu.se/',
        'tagline': 'Uppsala Conflict Data Program',
        'description': 'Georeferenced data on armed conflicts and organized violence worldwide.',
        'coverage': 'Global conflict events',
        'update_frequency': 'Weekly',
        'metrics': 'Conflict events, fatalities',
        'record_label': 'conflict events',
        'tasks': ['ucdp_conflicts'],
        'freshness_hours': 168,
        'in_footer': True,
        'sort_order': 6,
    },
    'gbif': {
        'name': 'GBIF',
        'icon': '🦋',
        'url': 'https://www.gbif.org/',
        'tagline': 'Global Biodiversity Information Facility',
        'description': 'Species observation data from biodiversity hotspots around the world.',
        'coverage': '18 biodiversity hotspots',
        'update_frequency': 'Every 6 hours',
        'metrics': 'Species observations, diversity indices',
        'record_label': 'biodiversity records',
        'tasks': ['gbif_species_observations'],
        'freshness_hours': 168,
        'in_footer': True,
        'sort_order': 7,
    },
    'openweather': {
        'name': 'OpenWeatherMap',
        'icon': '⛈️',
        'url': 'https://openweathermap.org/',
        'tagline': 'Global Weather Data Network',
        'description': 'Temperature, humidity, wind, pressure and weather alerts from cities worldwide. Requires an API key.',
        'coverage': '24 major cities worldwide',
        'update_frequency': 'Every 2 hours',
        'metrics': 'Temperature, humidity, wind, pressure, alerts',
        'record_label': 'weather measurements',
        'tasks': ['openweather_current'],
        'freshness_hours': 6,
        'in_footer': True,
        'sort_order': 8,
    },
}


def setup_provider_metadata(verbose: bool = True) -> bool:
    """Write every provider's metadata into provider_config. Idempotent."""
    try:
        for provider_key, meta in PROVIDERS.items():
            set_provider_config(
                provider_key, METADATA_KEY, meta, 'json',
                'Display metadata (name, icon, coverage, tasks, freshness)'
            )
        if verbose:
            print(f"✅ Provider metadata seeded ({len(PROVIDERS)} providers)")
        return True
    except Exception as e:
        print(f"❌ Error seeding provider metadata: {e}")
        return False


if __name__ == "__main__":
    if not setup_provider_metadata():
        sys.exit(1)
