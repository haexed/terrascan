#!/usr/bin/env python3
"""TERRASCAN
Advanced environmental data monitoring and analysis platform
"""

import os
import sys
from web.app import create_app
from database.config_manager import get_system_config, set_system_config

def main():
    """Main application entry point"""
    
    print("🌍 TERRASCAN")
    print("=" * 50)
    print("Environmental Health Monitoring Dashboard")
    print("Real-time tracking of fires, air quality, and ocean data")
    print("=" * 50)
    
    # Initialize database and configurations
    from setup_configs import setup_system_configs
    if not setup_system_configs():
        print("❌ Failed to initialize system configurations")
        sys.exit(1)
    
    # Get version info
    version = get_system_config('version', 'Unknown')
    print(f"✅ System initialized (version: {version})")
    
    # Create Flask application
    app = create_app()
    
    # Get port from environment or use default
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    print(f"🚀 Starting server on port {port}")
    print(f"🌐 Dashboard will be available at: http://localhost:{port}")
    print("📊 Monitor environmental health in real-time")
    print("-" * 50)
    
    # Start the application
    app.run(host='0.0.0.0', port=port, debug=debug)

if __name__ == "__main__":
    main() 
