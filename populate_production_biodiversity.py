#!/usr/bin/env python3
"""
Populate production database with biodiversity data
"""

from database.db import execute_query, execute_insert, init_database
from database.config_manager import set_provider_config
from tasks.fetch_biodiversity import fetch_biodiversity_data

def populate_production_biodiversity():
    """Populate production with biodiversity data and tasks"""
    
    print("🌿 Populating production with biodiversity data...")
    
    try:
        # Initialize database if needed
        init_database()
        
        # Set up GBIF provider configuration
        print("⚙️ Configuring GBIF provider...")
        set_provider_config('gbif', 'timeout_seconds', 30, 'int', 'API request timeout in seconds')
        set_provider_config('gbif', 'rate_limit_delay', 0.2, 'float', 'Delay between API calls in seconds')
        
        # Add biodiversity tasks if they don't exist
        print("📋 Setting up biodiversity tasks...")
        
        # Check if tasks exist
        existing_tasks = execute_query("SELECT name FROM task WHERE provider = 'gbif'")
        task_names = [task['name'] for task in existing_tasks]
        
        if 'gbif_species_observations' not in task_names:
            execute_insert("""
                INSERT INTO task 
                (name, description, task_type, command, cron_schedule, provider, dataset, parameters, active, created_date, updated_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            """, (
                'gbif_species_observations',
                'Collect species observations from GBIF for major biodiversity hotspots worldwide',
                'fetch_data',
                'tasks.fetch_biodiversity',
                '0 */6 * * *',  # Every 6 hours
                'gbif',
                'biodiversity',
                '{"product": "species_observations"}',
                1
            ))
            print("✅ Added gbif_species_observations task")
        
        if 'gbif_comprehensive' not in task_names:
            execute_insert("""
                INSERT INTO task 
                (name, description, task_type, command, cron_schedule, provider, dataset, parameters, active, created_date, updated_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            """, (
                'gbif_comprehensive',
                'Collect comprehensive biodiversity data including species observations and diversity metrics',
                'fetch_data',
                'tasks.fetch_biodiversity',
                '0 */12 * * *',  # Every 12 hours
                'gbif',
                'biodiversity',
                '{"product": "all"}',
                1
            ))
            print("✅ Added gbif_comprehensive task")
        
        # Check current biodiversity data
        biodiversity_count = execute_query("SELECT COUNT(*) as count FROM metric_data WHERE provider_key = 'gbif'")
        current_count = biodiversity_count[0]['count'] if biodiversity_count else 0
        
        print(f"📊 Current biodiversity records: {current_count}")
        
        if current_count < 10:
            print("🔄 Collecting fresh biodiversity data...")
            result = fetch_biodiversity_data(product='species_observations')
            
            if result['success']:
                print(f"✅ Successfully collected {result['records_processed']} biodiversity records!")
                
                # Show what we collected
                biodiversity_stats = execute_query("""
                    SELECT 
                        metric_name,
                        COUNT(*) as count,
                        AVG(value) as avg_value,
                        MIN(value) as min_value,
                        MAX(value) as max_value
                    FROM metric_data 
                    WHERE provider_key = 'gbif'
                    GROUP BY metric_name
                """)
                
                print("\n📈 Biodiversity Data Summary:")
                for stat in biodiversity_stats:
                    print(f"   • {stat['metric_name']}: {stat['count']} records")
                    print(f"     Average: {stat['avg_value']:.1f}, Range: {stat['min_value']:.0f}-{stat['max_value']:.0f}")
                
            else:
                print(f"❌ Failed to collect biodiversity data: {result.get('error', 'Unknown error')}")
        else:
            print("✅ Biodiversity data already present")
        
        # Verify the data is accessible for the dashboard
        print("\n🔍 Verifying dashboard data access...")
        
        dashboard_data = execute_query("""
            SELECT 
                AVG(CASE WHEN metric_name = 'species_observations' THEN value END) as avg_observations,
                AVG(CASE WHEN metric_name = 'species_diversity' THEN value END) as avg_diversity,
                COUNT(DISTINCT CASE WHEN metric_name = 'species_observations' THEN location_lat || ',' || location_lng END) as region_count,
                SUM(CASE WHEN metric_name = 'species_observations' THEN value ELSE 0 END) as total_observations
            FROM metric_data
            WHERE provider_key = 'gbif'
            AND timestamp >= datetime('now', '-7 days')
        """)
        
        if dashboard_data and dashboard_data[0]['avg_observations']:
            data = dashboard_data[0]
            print("✅ Dashboard data ready:")
            print(f"   • Average observations: {data['avg_observations']:.1f}")
            print(f"   • Average diversity: {data['avg_diversity']:.1f}")
            print(f"   • Regions monitored: {data['region_count']}")
            print(f"   • Total observations: {data['total_observations']}")
        else:
            print("⚠️ Dashboard data not accessible - may need fresh data collection")
        
        print("\n🌍 Biodiversity hotspots being monitored:")
        regions = execute_query("""
            SELECT DISTINCT JSON_EXTRACT(metadata, '$.region') as region,
                           JSON_EXTRACT(metadata, '$.ecosystem') as ecosystem,
                           COUNT(*) as records
            FROM metric_data 
            WHERE provider_key = 'gbif'
            GROUP BY JSON_EXTRACT(metadata, '$.region')
            ORDER BY records DESC
        """)
        
        for region in regions[:10]:  # Show top 10
            print(f"   • {region['region']} ({region['ecosystem']}): {region['records']} records")
        
        return True
        
    except Exception as e:
        print(f"❌ Error populating biodiversity data: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = populate_production_biodiversity()
    if success:
        print("\n🚀 Production biodiversity data ready!")
        print("   The dashboard should now show live biodiversity metrics!")
    else:
        print("\n❌ Failed to populate production biodiversity data")
        exit(1) 
