#!/usr/bin/env python3
"""
Provider metadata - the single source for how data providers are presented.

Metadata lives in the database: one row per provider in `provider_config`,
key = 'metadata', value = JSON. Seed or update it with `setup_providers.py`
(run automatically on startup via `setup_configs.py`).

Nothing outside this module should hardcode provider names, icons, URLs,
task names or freshness thresholds.
"""

import json
from typing import Any, Dict, List

from database.db import execute_query

METADATA_KEY = 'metadata'

# Used when a provider's metadata has no freshness_hours of its own
DEFAULT_FRESHNESS_HOURS = 24


def get_provider_metadata() -> List[Dict[str, Any]]:
    """All provider metadata from the database, ordered by sort_order.

    Returns:
        List[Dict]: one dict per provider, each with a 'provider_key' field.
    """
    rows = execute_query(
        "SELECT provider, value FROM provider_config WHERE key = %s",
        (METADATA_KEY,)
    )

    providers = []
    for row in rows or []:
        try:
            meta = json.loads(row['value'])
        except (ValueError, TypeError) as e:
            print(f"⚠️ Invalid provider metadata for '{row['provider']}': {e}")
            continue
        meta['provider_key'] = row['provider']
        providers.append(meta)

    providers.sort(key=lambda p: (p.get('sort_order', 999), p['provider_key']))
    return providers


def get_provider_map() -> Dict[str, Dict[str, Any]]:
    """Provider metadata keyed by provider_key."""
    return {p['provider_key']: p for p in get_provider_metadata()}


def get_provider_keys() -> List[str]:
    """Every known provider_key, in display order."""
    return [p['provider_key'] for p in get_provider_metadata()]


def get_provider_tasks() -> Dict[str, str]:
    """provider_key -> its primary collection task (the first one listed)."""
    return {
        p['provider_key']: p['tasks'][0]
        for p in get_provider_metadata()
        if p.get('tasks')
    }


def get_collection_tasks() -> List[str]:
    """Every collection task across all providers, in display order."""
    return [task for p in get_provider_metadata() for task in p.get('tasks', [])]


def get_freshness_thresholds() -> Dict[str, int]:
    """provider_key -> hours after which its data counts as stale."""
    return {
        p['provider_key']: p.get('freshness_hours', DEFAULT_FRESHNESS_HOURS)
        for p in get_provider_metadata()
    }
