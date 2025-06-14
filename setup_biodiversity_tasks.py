#!/usr/bin/env python3
"""
Setup biodiversity data collection tasks in the database
"""

from database.db import execute_query, init_database
from database.config_manager import set_provider_config

def setup_biodiversity_tasks():
    """Add biodiversity data collection tasks to the database"""
    
    print("🌿 Setting up biodiversity data collection tasks...")
    
    try:
        # Initialize database if needed
        init_database()
        
        # Set up GBIF provider configuration (completely free!)
        print("⚙️ Configuring GBIF provider...")
        
        # GBIF API is completely free - no API key required!
        set_provider_config('gbif', 'timeout_seconds', 30, 'int', 'API request timeout in seconds')
        set_provider_config('gbif', 'rate_limit_delay', 0.2, 'float', 'Delay between API calls in seconds')
        set_provider_config('gbif', 'max_records_per_region', 100, 'int', 'Maximum records to fetch per biodiversity region')
        
        # Add species observations task
        print("🦋 Adding species observations task...")
        execute_query("""
            INSERT OR REPLACE INTO task 
            (name, description, task_type, command, cron_schedule, provider, dataset, parameters, active, created_date, updated_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        """, [
            'gbif_species_observations',
            'Global biodiversity monitoring using GBIF species observation data',
            'fetch_data',
            'tasks.fetch_gbif_biodiversity.fetch_biodiversity_data',
            '0 */6 * * *',  # Every 6 hours
            'gbif',
            'biodiversity',
            '{"product": "species_observations"}',
            1
        ])
        
        # Add comprehensive biodiversity task (runs less frequently)
        print("🌍 Adding comprehensive biodiversity task...")
        execute_query("""
            INSERT OR REPLACE INTO task 
            (name, description, task_type, command, cron_schedule, provider, dataset, parameters, active, created_date, updated_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        """, [
            'gbif_ecosystem_health',
            'Ecosystem health assessment using GBIF biodiversity metrics',
            'fetch_data',
            'tasks.fetch_gbif_biodiversity.fetch_biodiversity_data',
            '0 */12 * * *',  # Every 12 hours
            'gbif',
            'ecosystem_health',
            '{"product": "ecosystem_health"}',
            1
        ])
        
        # Test the biodiversity data collection
        print("\n🧪 Testing GBIF biodiversity data collection...")
        try:
            from tasks.fetch_gbif_biodiversity import fetch_biodiversity_data
            
            result = fetch_biodiversity_data(product='species_observations')
            if result['success']:
                print(f"   ✅ Success! Collected {result['records_processed']} biodiversity records")
            else:
                print(f"   ❌ Error: {result['error']}")
        except Exception as e:
            print(f"   ⚠️  Import error: {e}")
            print("   💡 Make sure GBIF API is accessible (no key required)")
        
        # Verify tasks were created
        tasks = execute_query("SELECT name, description, active FROM task WHERE provider = 'gbif' ORDER BY name")
        
        print(f"\n✅ Biodiversity monitoring tasks setup complete!")
        print(f"   📊 Tasks created: {len(tasks)}")
        print(f"   🌿 GBIF hotspots: 18 global biodiversity regions")
        print(f"   🔄 Frequency: Every 6-12 hours")
        print(f"   🆓 Cost: Free (GBIF requires no API key)")
        
        print(f"\n🧪 Manual test command:")
        print(f"   Run: python -c \"from tasks.fetch_gbif_biodiversity import fetch_biodiversity_data; print(fetch_biodiversity_data())\"")
        
        return True
        
    except Exception as e:
        print(f"❌ Error setting up biodiversity tasks: {str(e)}")
        return False

if __name__ == "__main__":
    success = setup_biodiversity_tasks()
    if not success:
        exit(1)
    
    print("\n🚀 Ready to monitor global biodiversity!")
    print("   Run: python -c \"from tasks.fetch_biodiversity import fetch_biodiversity_data; print(fetch_biodiversity_data())\"") 
