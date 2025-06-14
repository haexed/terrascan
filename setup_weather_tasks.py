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
        
        # Weather monitoring tasks (OpenWeatherMap)
        tasks = [
            ('openweather_current', 
             'Current weather monitoring for 24 major cities using OpenWeatherMap API',
             'fetch_data',
             'tasks.fetch_openweathermap_weather.fetch_weather_data', 
             '0 */2 * * *', 
             'openweather', 
             'weather',
             '{"product": "current"}'),
            
            ('openweather_alerts', 
             'Weather alerts and severe weather monitoring using OpenWeatherMap API',
             'fetch_data',
             'tasks.fetch_openweathermap_weather.fetch_weather_data', 
             '0 */1 * * *', 
             'openweather', 
             'alerts',
             '{"product": "alerts"}'),
            
            ('openweather_comprehensive', 
             'Comprehensive weather data collection including forecasts and historical data',
             'fetch_data',
             'tasks.fetch_openweathermap_weather.fetch_weather_data', 
             '0 */4 * * *', 
             'openweather', 
             'comprehensive',
             '{"product": "all"}'),
        ]
        
        # Add tasks to the database
        for task in tasks:
            print(f"📊 Adding {task[0]} task...")
            execute_query("""
                INSERT OR REPLACE INTO task 
                (name, description, task_type, command, cron_schedule, provider, dataset, parameters, active, created_date, updated_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            """, task)
        
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
        
        print(f"\n🧪 Manual test command:")
        print(f"   Run: python -c \"from tasks.fetch_openweathermap_weather import fetch_weather_data; print(fetch_weather_data())\"")
        
        return True
        
    except Exception as e:
        print(f"❌ Error setting up weather tasks: {str(e)}")
        return False

if __name__ == "__main__":
    success = setup_weather_tasks()
    if not success:
        exit(1)
    
    print("\n🚀 Ready to collect weather data!")
    print("   Run: python -c \"from tasks.fetch_openweathermap_weather import fetch_weather_data; print(fetch_weather_data())\"") 
