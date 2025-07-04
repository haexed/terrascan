#!/usr/bin/env python3
"""
TERRASCAN Production Setup for Railway
Sets up PostgreSQL database and all environmental monitoring tasks
"""

import os
import sys
import psycopg2
from datetime import datetime

def setup_railway_production():
    """Complete production setup for Railway deployment"""
    
    print("🚀 TERRASCAN Production Setup for Railway")
    print("=" * 60)
    
    # Check if we're in Railway environment
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL not found - not in Railway environment")
        print("📋 Railway Setup Instructions:")
        print("1. Go to your Railway project dashboard")
        print("2. Add PostgreSQL service: railway add postgresql")
        print("3. Set environment variables:")
        print("   - DATABASE_URL (auto-generated by Railway)")
        print("   - OPENWEATHER_API_KEY (get from openweathermap.org)")
        print("   - NASA_FIRMS_API_KEY (get from firms.modaps.eosdis.nasa.gov)")
        return False
    
    try:
        # Connect to PostgreSQL
        print("🔗 Connecting to Railway PostgreSQL...")
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        # Create all necessary tables
        print("📊 Creating database schema...")
        
        # System configuration table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS system_config (
                key VARCHAR(255) PRIMARY KEY,
                value TEXT,
                data_type VARCHAR(50) DEFAULT 'string',
                description TEXT,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Provider configuration table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS provider_config (
                provider VARCHAR(100),
                key VARCHAR(255),
                value TEXT,
                data_type VARCHAR(50) DEFAULT 'string',
                description TEXT,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (provider, key)
            )
        """)
        
        # Tasks table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS task (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) UNIQUE NOT NULL,
                description TEXT,
                task_type VARCHAR(100),
                command TEXT,
                cron_schedule VARCHAR(100),
                provider VARCHAR(100),
                dataset VARCHAR(100),
                parameters TEXT,
                active BOOLEAN DEFAULT TRUE,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Task logs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS task_log (
                id SERIAL PRIMARY KEY,
                task_id INTEGER REFERENCES task(id),
                status VARCHAR(50),
                started_at TIMESTAMP,
                completed_at TIMESTAMP,
                duration_seconds DECIMAL(10,3),
                records_processed INTEGER DEFAULT 0,
                error_message TEXT,
                triggered_by VARCHAR(100),
                trigger_parameters TEXT
            )
        """)
        
        # Main environmental data table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS metric_data (
                id SERIAL PRIMARY KEY,
                provider_key VARCHAR(100),
                metric_name VARCHAR(255),
                value DECIMAL(15,6),
                unit VARCHAR(50),
                location_lat DECIMAL(10,7),
                location_lng DECIMAL(10,7),
                timestamp TIMESTAMP,
                metadata TEXT,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create indexes for performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_metric_data_provider ON metric_data(provider_key)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_metric_data_timestamp ON metric_data(timestamp)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_metric_data_location ON metric_data(location_lat, location_lng)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_task_log_task_id ON task_log(task_id)")
        
        print("✅ Database schema created successfully")
        
        # Insert system configuration
        print("⚙️ Setting up system configuration...")
        
        system_configs = [
            ('version', '2.5.0', 'string', 'Current system version'),
            ('simulation_mode', 'false', 'boolean', 'Enable simulation mode for testing'),
            ('data_retention_days', '30', 'int', 'Number of days to retain environmental data'),
            ('max_records_per_provider', '10000', 'int', 'Maximum records per data provider'),
            ('auto_refresh_interval', '900', 'int', 'Auto-refresh interval in seconds (15 minutes)'),
        ]
        
        for key, value, data_type, description in system_configs:
            cursor.execute("""
                INSERT INTO system_config (key, value, data_type, description)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (key) DO UPDATE SET
                    value = EXCLUDED.value,
                    data_type = EXCLUDED.data_type,
                    description = EXCLUDED.description,
                    updated_date = CURRENT_TIMESTAMP
            """, (key, value, data_type, description))
        
        # Insert provider configurations
        print("🔧 Setting up provider configurations...")
        
        provider_configs = [
            # NASA FIRMS
            ('nasa_firms', 'timeout_seconds', '30', 'int', 'API request timeout'),
            ('nasa_firms', 'max_records', '1000', 'int', 'Maximum records per request'),
            ('nasa_firms', 'confidence_threshold', '75', 'int', 'Minimum confidence level for fire detection'),
            
            # OpenAQ
            ('openaq', 'timeout_seconds', '30', 'int', 'API request timeout'),
            ('openaq', 'max_locations', '100', 'int', 'Maximum locations per request'),
            ('openaq', 'parameter_filter', 'pm25', 'string', 'Air quality parameter to collect'),
            
            # NOAA Ocean
            ('noaa_ocean', 'timeout_seconds', '45', 'int', 'API request timeout'),
            ('noaa_ocean', 'max_stations', '20', 'int', 'Maximum stations to monitor'),
            ('noaa_ocean', 'data_interval', '6', 'int', 'Data collection interval in minutes'),
            
            # OpenWeatherMap
            ('openweather', 'timeout_seconds', '30', 'int', 'API request timeout'),
            ('openweather', 'rate_limit_delay', '0.1', 'float', 'Delay between API calls'),
            ('openweather', 'max_cities', '25', 'int', 'Maximum cities to monitor'),
            
            # GBIF Biodiversity
            ('gbif', 'timeout_seconds', '30', 'int', 'API request timeout'),
            ('gbif', 'rate_limit_delay', '0.2', 'float', 'Delay between API calls'),
            ('gbif', 'max_regions', '20', 'int', 'Maximum biodiversity regions'),
        ]
        
        for provider, key, value, data_type, description in provider_configs:
            cursor.execute("""
                INSERT INTO provider_config (provider, key, value, data_type, description)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (provider, key) DO UPDATE SET
                    value = EXCLUDED.value,
                    data_type = EXCLUDED.data_type,
                    description = EXCLUDED.description,
                    updated_date = CURRENT_TIMESTAMP
            """, (provider, key, value, data_type, description))
        
        # Insert all environmental monitoring tasks
        print("📋 Setting up environmental monitoring tasks...")
        
        tasks = [
            # NASA FIRMS Fire Monitoring
            ('nasa_fires_global', 'Collect global active fires from NASA FIRMS', 'fetch_data', 
             'tasks.fetch_nasa_fires.fetch_nasa_fires', '0 */2 * * *', 'nasa_firms', 'fires', 
             '{"region": "WORLD", "days": 7}'),
            
            # OpenAQ Air Quality
            ('openaq_latest', 'Get latest air quality measurements', 'fetch_data',
             'tasks.fetch_openaq_latest.fetch_openaq_latest', '0 * * * *', 'openaq', 'air_quality',
             '{}'),
            
            # NOAA Ocean Data
            ('noaa_ocean_water_level', 'Fetch water level data from NOAA Ocean Service', 'fetch_data',
             'tasks.fetch_noaa_ocean.fetch_water_level_data', '0 */3 * * *', 'noaa_ocean', 'ocean',
             '{}'),
            
            ('noaa_ocean_temperature', 'Fetch ocean temperature data from NOAA', 'fetch_data',
             'tasks.fetch_noaa_ocean.fetch_water_temperature_data', '30 */3 * * *', 'noaa_ocean', 'ocean',
             '{}'),
            
            # Weather monitoring tasks (OpenWeatherMap)
            ('openweather_current', 
             'tasks.fetch_openweathermap_weather.fetch_weather_data', 
             'Tasks weather monitoring for 24 major cities using OpenWeatherMap API',
             'tasks.fetch_openweathermap_weather.fetch_weather_data', '0 */2 * * *', 'openweather', 'weather',
             '{"product": "current"}'),
            
            # Biodiversity monitoring tasks (GBIF)
            ('gbif_species_observations', 
             'tasks.fetch_gbif_biodiversity.fetch_biodiversity_data', 
             'Global biodiversity monitoring using GBIF species observation data',
             'tasks.fetch_gbif_biodiversity.fetch_biodiversity_data', '0 */6 * * *', 'gbif', 'biodiversity',
             '{"product": "species_observations"}'),
        ]
        
        for name, description, task_type, command, cron_schedule, provider, dataset, parameters in tasks:
            cursor.execute("""
                INSERT INTO task (name, description, task_type, command, cron_schedule, provider, dataset, parameters, active)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (name) DO UPDATE SET
                    description = EXCLUDED.description,
                    task_type = EXCLUDED.task_type,
                    command = EXCLUDED.command,
                    cron_schedule = EXCLUDED.cron_schedule,
                    provider = EXCLUDED.provider,
                    dataset = EXCLUDED.dataset,
                    parameters = EXCLUDED.parameters,
                    active = EXCLUDED.active,
                    updated_date = CURRENT_TIMESTAMP
            """, (name, description, task_type, command, cron_schedule, provider, dataset, parameters, True))
        
        # Commit all changes
        conn.commit()
        
        print("✅ All environmental monitoring tasks configured")
        print("📊 Production database setup complete!")
        
        # Show summary
        cursor.execute("SELECT COUNT(*) FROM task WHERE active = true")
        task_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM system_config")
        config_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM provider_config")
        provider_count = cursor.fetchone()[0]
        
        print("\n🎯 Setup Summary:")
        print(f"   • {task_count} active environmental monitoring tasks")
        print(f"   • {config_count} system configuration entries")
        print(f"   • {provider_count} provider configuration entries")
        print(f"   • PostgreSQL database ready for production")
        
        print("\n🌍 Environmental Data Sources Configured:")
        print("   🔥 NASA FIRMS - Global fire monitoring")
        print("   🌬️ OpenAQ - Air quality measurements")
        print("   🌊 NOAA Ocean - Ocean temperature & water levels")
        print("   ⛈️ OpenWeatherMap - Weather data & alerts")
        print("   🦋 GBIF - Biodiversity & species observations")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Production setup failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def check_environment_variables():
    """Check required environment variables for production"""
    print("\n🔍 Checking environment variables...")
    
    required_vars = {
        'DATABASE_URL': 'PostgreSQL connection string (auto-generated by Railway)',
        'OPENWEATHER_API_KEY': 'OpenWeatherMap API key (get from openweathermap.org)',
        'NASA_FIRMS_API_KEY': 'NASA FIRMS API key (optional, has free tier)',
    }
    
    missing_vars = []
    for var, description in required_vars.items():
        if os.environ.get(var):
            print(f"   ✅ {var}: Set")
        else:
            print(f"   ❌ {var}: Missing - {description}")
            missing_vars.append(var)
    
    if missing_vars:
        print(f"\n⚠️ Missing {len(missing_vars)} required environment variables")
        print("📋 Railway Environment Setup:")
        print("1. Go to your Railway project dashboard")
        print("2. Click on 'Variables' tab")
        print("3. Add the missing environment variables")
        return False
    else:
        print("✅ All required environment variables are set")
        return True

if __name__ == "__main__":
    print("🚀 TERRASCAN Production Setup for Railway")
    print("=" * 60)
    
    # Check environment first
    if not check_environment_variables():
        print("\n❌ Environment setup incomplete")
        sys.exit(1)
    
    # Run production setup
    if setup_railway_production():
        print("\n🎉 TERRASCAN Production Setup Complete!")
        print("🌍 Your environmental monitoring platform is ready!")
        print("\n📋 Next Steps:")
        print("1. Deploy to Railway (git push)")
        print("2. Check https://your-app.railway.app/system")
        print("3. Verify all data sources are collecting")
        print("4. Monitor environmental health dashboard")
    else:
        print("\n❌ Production setup failed")
        sys.exit(1) 
