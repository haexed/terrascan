#!/usr/bin/env python3
"""
Terrascan Python System - Startup Script
Initialize database and start web interface
"""

import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(__file__))

# Import version info
from version import get_version

def main():
    """Main startup function"""
    print(f"🌍 Starting Terrascan Python System v{get_version()}...")
    
    # Initialize database
    print("📁 Initializing database...")
    from database.db import init_database
    init_database()
    
    # Test database connection
    print("🔍 Testing database connection...")
    from database.db import get_tasks
    tasks = get_tasks()
    print(f"✅ Found {len(tasks)} tasks in database")
    
    # Run a sample task to test the system (skip in production)
    is_production = os.getenv('RAILWAY_ENVIRONMENT_NAME') == 'production'
    
    if not is_production:
        print("🧪 Testing task system...")
        from tasks.runner import TaskRunner
        runner = TaskRunner()
        
        # Try to run the NASA fires task
        result = runner.run_task('nasa_fires_global', triggered_by='startup_test')
        
        if result['success']:
            print(f"✅ Test task completed successfully! Processed {result.get('records_processed', 0)} records")
        else:
            print(f"⚠️ Test task failed: {result['error']}")
    else:
        print("🚀 Production mode: Skipping startup test for faster boot")
    
    # Start web interface
    print("\n🌐 Starting web interface...")
    print("📊 Dashboard will be available at: http://localhost:5000")
    print("🔧 Task management at: http://localhost:5000/tasks")
    print("📈 Data exploration at: http://localhost:5000/data")
    print("📊 Metrics overview at: http://localhost:5000/metrics")
    print("🌐 Providers info at: http://localhost:5000/providers")
    print("🗂️ Database schema at: http://localhost:5000/schema")
    print("🖥️ System logs at: http://localhost:5000/system")
    print("\n⏸️ Press Ctrl+C to stop the server\n")
    
    # Import and run the Flask app
    from web.app import app
    app.run(debug=True, host='0.0.0.0', port=5000)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Shutting down Terrascan...")
    except Exception as e:
        print(f"❌ Error starting Terrascan: {e}")
        import traceback
        traceback.print_exc() 
