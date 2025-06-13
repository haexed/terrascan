#!/usr/bin/env python3
"""
Version information for ECO WATCH TERRA SCAN
"""

VERSION = "2.2.3"
BUILD_DATE = "2024-12-19"
DESCRIPTION = "Environmental Health Monitoring Dashboard - Debug Cleanup"

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

if __name__ == "__main__":
    print(f"ECO WATCH TERRA SCAN v{VERSION}")
    print(f"Build Date: {BUILD_DATE}")
    print(f"Description: {DESCRIPTION}") 
