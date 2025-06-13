#!/usr/bin/env python3
"""
Setup weather data collection tasks in the database
"""

from database.db import execute_query, init_database
from database.config_manager import set_provider_config

def setup_weather_tasks():
    """Add weather data collection tasks to the database"""
    
    print("🌡️ Setting up weather data collection tasks...")
    
    try:
        # Initialize database if needed
        init_database()
        
        # Set up OpenWeatherMap provider configuration
        print("⚙️ Configuring OpenWeatherMap provider...")
        
        # Note: User will need to add their API key
        set_provider_config('openweather', 'api_key', '', 'str', 'OpenWeatherMap API key (get from openweathermap.org)')
        set_provider_config('openweather', 'timeout_seconds', 30, 'int', 'API request timeout in seconds')
        set_provider_config('openweather', 'rate_limit_delay', 0.1, 'float', 'Delay between API calls in seconds')
        
        # Add current weather task
        print("📊 Adding current weather task...")
        execute_query("""
            INSERT OR REPLACE INTO task 
            (name, description, task_type, command, cron_schedule, provider, dataset, parameters, active, created_date, updated_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        """, [
            'openweather_current',
            'Collect current weather data from OpenWeatherMap for major cities worldwide',
            'fetch_data',
            'tasks.fetch_weather',
            '0 */2 * * *',  # Every 2 hours
            'openweather',
            'weather',
            '{"product": "current"}',
            1
        ])
        
        # Add weather alerts task
        print("🚨 Adding weather alerts task...")
        execute_query("""
            INSERT OR REPLACE INTO task 
            (name, description, task_type, command, cron_schedule, provider, dataset, parameters, active, created_date, updated_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        """, [
            'openweather_alerts',
            'Collect weather alerts and warnings from OpenWeatherMap',
            'fetch_data',
            'tasks.fetch_weather',
            '0 */1 * * *',  # Every hour
            'openweather',
            'weather',
            '{"product": "alerts"}',
            1
        ])
        
        # Add comprehensive weather task (runs less frequently)
        print("🌍 Adding comprehensive weather task...")
        execute_query("""
            INSERT OR REPLACE INTO task 
            (name, description, task_type, command, cron_schedule, provider, dataset, parameters, active, created_date, updated_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        """, [
            'openweather_comprehensive',
            'Collect comprehensive weather data including current conditions and alerts',
            'fetch_data',
            'tasks.fetch_weather',
            '0 */6 * * *',  # Every 6 hours
            'openweather',
            'weather',
            '{"product": "all"}',
            1
        ])
        
        # Verify tasks were created
        tasks = execute_query("SELECT name, description, active FROM task WHERE provider = 'openweather' ORDER BY name")
        
        print("\n✅ Weather tasks setup completed!")
        print("\n📋 Created Tasks:")
        for task in tasks:
            status = "🟢 ACTIVE" if task['active'] else "🔴 INACTIVE"
            print(f"   • {task['name']}: {task['description']} ({status})")
        
        print("\n🔑 IMPORTANT: Add your OpenWeatherMap API key!")
        print("   1. Sign up at https://openweathermap.org/api")
        print("   2. Get your free API key (1,000 calls/day)")
        print("   3. Add it to your .env file:")
        print("      OPENWEATHER_API_KEY=your_api_key_here")
        print("   4. Or configure it via the system:")
        print("      from database.config_manager import set_provider_config")
        print("      set_provider_config('openweather', 'api_key', 'your_key', 'str', 'API key')")
        
        print("\n🌡️ Weather Data Types:")
        print("   • Temperature (°C)")
        print("   • Humidity (%)")
        print("   • Wind Speed (m/s)")
        print("   • Atmospheric Pressure (hPa)")
        print("   • Weather Alerts (government warnings)")
        
        print("\n🌍 Coverage:")
        print("   • 24 major cities worldwide")
        print("   • All continents represented")
        print("   • Real-time weather conditions")
        print("   • Government weather alerts")
        
        return True
        
    except Exception as e:
        print(f"❌ Error setting up weather tasks: {str(e)}")
        return False

if __name__ == "__main__":
    success = setup_weather_tasks()
    if not success:
        exit(1)
    
    print("\n🚀 Ready to collect weather data!")
    print("   Run: python -c \"from tasks.fetch_weather import fetch_weather_data; print(fetch_weather_data())\"") 
