#!/usr/bin/env python3
"""
Setup initial system configurations for the Terrascan platform.
"""

import os
import sys
from database.database_config import get_database_config, set_system_config, get_system_config

def setup_system_configs():
    """Set up initial system configurations"""
    
    print("🔧 Setting up system configurations...")
    
    try:
        # Get database configuration
        db_config = get_database_config()
        print(f"✅ Database configured: {db_config['database_path']}")
        
        # Set version information
        version = "2.0.0"
        set_system_config('version', version, 'str', 'Current system version')
        print(f"✅ Version set to: {version}")
        
        # Set startup timestamp
        from datetime import datetime
        startup_time = datetime.now().isoformat()
        set_system_config('last_startup', startup_time, 'str', 'Last system startup time')
        print(f"✅ Startup time recorded: {startup_time}")
        
        # Set platform info
        platform_info = f"{sys.platform} ({os.name})"
        set_system_config('platform', platform_info, 'str', 'Operating system platform')
        print(f"✅ Platform info: {platform_info}")
        
        print("\n🎉 System configurations completed successfully!")
        print("\n📋 Configuration Summary:")
        print(f"   • Version: {version}")
        print(f"   • Database: {db_config['database_path']}")
        print(f"   • Platform: {platform_info}")
        print(f"   • Startup: {startup_time}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error setting up configurations: {str(e)}")
        return False

if __name__ == "__main__":
    success = setup_system_configs()
    if not success:
        sys.exit(1) 
