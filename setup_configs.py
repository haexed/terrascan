#!/usr/bin/env python3
"""
Setup initial configurations for Terrascan providers and datasets
"""

from database.config_manager import set_provider_config, set_dataset_config, set_system_config

def setup_nasa_firms_config():
    """Setup NASA FIRMS provider configurations"""
    print("🛰️ Setting up NASA FIRMS configuration...")
    
    # Provider-level configurations
    set_provider_config('nasa_firms', 'base_url', 'https://firms.modaps.eosdis.nasa.gov/api/area/csv', 'string', 
                       'Base URL for NASA FIRMS API')
    set_provider_config('nasa_firms', 'api_key_required', True, 'bool', 
                       'Whether API key is required for this provider')
    set_provider_config('nasa_firms', 'rate_limit_per_hour', 100, 'int', 
                       'Maximum requests per hour')
    set_provider_config('nasa_firms', 'timeout_seconds', 30, 'int', 
                       'Request timeout in seconds')
    
    # Dataset-specific configurations
    set_dataset_config('nasa_firms', 'active_fires', 'satellite_sources', 
                      ['VIIRS_NOAA20_NRT', 'VIIRS_SNPP_NRT', 'MODIS_A', 'MODIS_T'], 'json',
                      'Available satellite data sources')
    set_dataset_config('nasa_firms', 'active_fires', 'default_source', 'VIIRS_SNPP_NRT', 'string',
                      'Default satellite source to use')
    set_dataset_config('nasa_firms', 'active_fires', 'default_days', 1, 'int',
                      'Default number of days to fetch')
    set_dataset_config('nasa_firms', 'active_fires', 'max_days', 10, 'int',
                      'Maximum days that can be requested')

def setup_openaq_config():
    """Setup OpenAQ provider configurations"""
    print("🌬️ Setting up OpenAQ configuration...")
    
    # Provider-level configurations
    set_provider_config('openaq', 'base_url', 'https://api.openaq.org/v2', 'string',
                       'Base URL for OpenAQ API')
    set_provider_config('openaq', 'api_key_required', False, 'bool',
                       'OpenAQ API is free and doesn\'t require keys')
    set_provider_config('openaq', 'rate_limit_per_hour', 1000, 'int',
                       'OpenAQ rate limit')
    set_provider_config('openaq', 'timeout_seconds', 30, 'int',
                       'Request timeout in seconds')
    
    # Dataset configurations
    set_dataset_config('openaq', 'air_quality', 'available_parameters', 
                      ['pm25', 'pm10', 'o3', 'no2', 'so2', 'co'], 'json',
                      'Available air quality parameters')
    set_dataset_config('openaq', 'air_quality', 'default_parameter', 'pm25', 'string',
                      'Default parameter to fetch')
    set_dataset_config('openaq', 'air_quality', 'max_locations', 1000, 'int',
                      'Maximum locations to fetch per request')

def setup_system_config():
    """Setup system-wide configurations"""
    print("⚙️ Setting up system configuration...")
    
    set_system_config('default_timeout', 30, 'int', 'Default HTTP timeout for all requests')
    set_system_config('max_concurrent_tasks', 5, 'int', 'Maximum concurrent task executions')
    set_system_config('data_retention_days', 365, 'int', 'How long to keep data (days)')
    set_system_config('enable_cost_tracking', True, 'bool', 'Track API costs and usage')
    set_system_config('simulation_mode', True, 'bool', 'Use simulated data when API keys missing')

def setup_provider_specific_endpoints():
    """Setup specific endpoints for different operations"""
    print("🔗 Setting up provider endpoints...")
    
    # NASA FIRMS specific endpoints
    nasa_endpoints = {
        'area_csv': '/api/area/csv/{source}/{area_extent}/{day_range}',
        'country_csv': '/api/country/csv/{source}/{country_code}/{day_range}',
        'area_shapefile': '/api/area/shp/{source}/{area_extent}/{day_range}'
    }
    set_provider_config('nasa_firms', 'endpoints', nasa_endpoints, 'json',
                       'Available API endpoints for NASA FIRMS')
    
    # OpenAQ endpoints
    openaq_endpoints = {
        'latest': '/latest',
        'measurements': '/measurements',
        'locations': '/locations',
        'cities': '/cities',
        'countries': '/countries'
    }
    set_provider_config('openaq', 'endpoints', openaq_endpoints, 'json',
                       'Available API endpoints for OpenAQ')

def main():
    """Setup all configurations"""
    print("🌍 Setting up Terrascan configurations...")
    
    try:
        setup_nasa_firms_config()
        setup_openaq_config()
        setup_system_config()
        setup_provider_specific_endpoints()
        
        print("✅ Configuration setup completed successfully!")
        print()
        print("📋 Configuration Summary:")
        print("  • NASA FIRMS: Configured with satellite sources and rate limits")
        print("  • OpenAQ: Configured with air quality parameters")
        print("  • System: Default timeouts and operational settings")
        print("  • Endpoints: API endpoint mappings for all providers")
        print()
        print("🔧 Usage in code:")
        print("  from database.config_manager import get_provider_config")
        print("  api_url = get_provider_config('nasa_firms', 'base_url')")
        
    except Exception as e:
        print(f"❌ Error setting up configurations: {e}")
        raise

if __name__ == "__main__":
    main() 
