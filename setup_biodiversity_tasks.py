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
            'Collect species observations from GBIF for major biodiversity hotspots worldwide',
            'fetch_data',
            'tasks.fetch_biodiversity',
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
            'gbif_comprehensive',
            'Collect comprehensive biodiversity data including species observations and diversity metrics',
            'fetch_data',
            'tasks.fetch_biodiversity',
            '0 */12 * * *',  # Every 12 hours
            'gbif',
            'biodiversity',
            '{"product": "all"}',
            1
        ])
        
        # Test the biodiversity data collection
        print("🧪 Testing biodiversity data collection...")
        from tasks.fetch_biodiversity import fetch_biodiversity_data
        
        result = fetch_biodiversity_data(product='species_observations')
        
        if result['success']:
            print(f"✅ Test successful! Collected {result['records_processed']} records")
        else:
            print(f"❌ Test failed: {result.get('error', 'Unknown error')}")
        
        # Verify tasks were created
        tasks = execute_query("SELECT name, description, active FROM task WHERE provider = 'gbif' ORDER BY name")
        
        print("\n✅ Biodiversity tasks setup completed!")
        print("\n📋 Created Tasks:")
        for task in tasks:
            status = "🟢 ACTIVE" if task['active'] else "🔴 INACTIVE"
            print(f"   • {task['name']}: {task['description']} ({status})")
        
        print("\n🌿 Biodiversity Data Types:")
        print("   • Species Observations (count)")
        print("   • Species Diversity (unique species count)")
        print("   • Ecosystem Health Index (calculated)")
        print("   • Threatened Species Count (conservation status)")
        
        print("\n🌍 Coverage:")
        print("   • 18 major biodiversity hotspots worldwide")
        print("   • Amazon Rainforest, African Savannas, Asian Forests")
        print("   • North American National Parks, European Forests")
        print("   • Australian Ecosystems, Arctic Tundra, Marine Islands")
        print("   • Real-time species observation data")
        
        print("\n🆓 GBIF API Benefits:")
        print("   • Completely FREE - no API key required!")
        print("   • 2+ billion species observations")
        print("   • Global coverage from research institutions")
        print("   • High-quality, verified biodiversity data")
        
        # Check current biodiversity data
        biodiversity_stats = execute_query("""
            SELECT COUNT(*) as total_records, 
                   COUNT(DISTINCT metric_name) as metric_types,
                   AVG(value) as avg_observations
            FROM metric_data 
            WHERE provider_key = 'gbif'
        """)
        
        if biodiversity_stats and biodiversity_stats[0]['total_records'] > 0:
            stats = biodiversity_stats[0]
            print(f"\n📊 Current Biodiversity Data:")
            print(f"   • {stats['total_records']} total records")
            print(f"   • {stats['metric_types']} metric types")
            print(f"   • {stats['avg_observations']:.1f} average observations per region")
        
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
