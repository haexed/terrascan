"""
TERRASCAN Utilities Package
Common utilities for the environmental monitoring platform
"""

# Version information
VERSION = "3.1.1"
BUILD_DATE = "2025-06-16"
DESCRIPTION = "Environmental Health Monitoring Dashboard - Python/PostgreSQL Platform"

__version__ = VERSION


def get_version():
    """Get current version string"""
    return VERSION


def get_build_info():
    """Get build information"""
    return {
        'version': VERSION,
        'build_date': BUILD_DATE,
        'description': DESCRIPTION
    }


# Import commonly used utilities for easy access
from .datetime_utils import (
    format_datetime_utc,
    format_date_only,
    format_time_only,
    format_iso,
    time_ago,
    current_utc,
    current_utc_formatted,
    register_template_filters
)

# Make these available at package level
__all__ = [
    'VERSION',
    'BUILD_DATE', 
    'DESCRIPTION',
    'get_version',
    'get_build_info',
    'format_datetime_utc',
    'format_date_only',
    'format_time_only',
    'format_iso',
    'time_ago',
    'current_utc',
    'current_utc_formatted',
    'register_template_filters'
] 
