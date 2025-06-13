#!/usr/bin/env python3
"""
ECO WATCH TERRA SCAN - Environmental Health Dashboard
Simple startup script for the environmental monitoring dashboard
"""

import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(__file__))

# Import version info
from version import get_version

def main():
    """Main startup function"""
    print(f"🌍 Starting ECO WATCH TERRA SCAN v{get_version()}...")
    
    # Initialize database
    print("📁 Initializing database...")
    from database.db import init_database
    init_database()
    
    # Test database connection
    print("🔍 Testing database connection...")
    from database.db import execute_query
    try:
        result = execute_query("SELECT COUNT(*) as count FROM metric_data")
        records = result[0]['count'] if result else 0
        print(f"✅ Found {records} environmental measurements in database")
    except Exception as e:
        print(f"⚠️ Database test: {e}")
    
    # Test environmental data availability (skip in production for faster boot)
    is_production = os.getenv('RAILWAY_ENVIRONMENT_NAME') == 'production'
    
    if not is_production:
        print("🧪 Testing environmental data collection...")
        from tasks.runner import TaskRunner
        runner = TaskRunner()
        
        # Quick test of data fetching
        try:
            result = runner.run_task('nasa_fires_global', triggered_by='startup_test')
            if result['success']:
                print(f"✅ Environmental data systems operational!")
            else:
                print(f"⚠️ Data collection test: {result.get('error', 'Unknown error')}")
        except Exception as e:
            print(f"⚠️ Data collection test failed: {e}")
    else:
        print("🚀 Production mode: Skipping startup tests for faster boot")
    
    # Start web dashboard
    print("\n🌐 Starting ECO WATCH TERRA SCAN Dashboard...")
    print("📊 Dashboard available at: http://localhost:5000")
    print("🔄 Auto-refresh every 15 minutes")
    print("🌍 Live environmental health monitoring")
    print("\n⏸️ Press Ctrl+C to stop the dashboard\n")
    
    # Import and run the Flask app
    from web.app import app
    app.run(debug=True, host='0.0.0.0', port=5000)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Shutting down ECO WATCH TERRA SCAN...")
    except Exception as e:
        print(f"❌ Error starting ECO WATCH: {e}")
        import traceback
        traceback.print_exc() 
