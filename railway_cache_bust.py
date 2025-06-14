#!/usr/bin/env python3
"""
Railway Cache Busting Utility
Forces a fresh deployment by updating environment variables
"""

import os
import datetime

def add_cache_bust_env():
    """Add cache busting environment variable to force Railway rebuild"""
    
    timestamp = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
    cache_bust_var = f"CACHE_BUST_{timestamp}"
    
    print(f"🚀 Railway Cache Busting Strategy")
    print(f"📅 Timestamp: {timestamp}")
    print(f"🔧 Add this environment variable to your Railway service:")
    print(f"")
    print(f"Variable Name: {cache_bust_var}")
    print(f"Variable Value: {timestamp}")
    print(f"")
    print(f"✅ This will force Railway to:")
    print(f"   - Invalidate build cache")
    print(f"   - Rebuild from fresh layers")
    print(f"   - Deploy new container instance")
    print(f"")
    print(f"🎯 After adding the variable:")
    print(f"   1. Railway will auto-deploy")
    print(f"   2. Templates will be regenerated")
    print(f"   3. Cache will be cleared")
    print(f"")
    print(f"🗑️  Clean up: Remove the variable after successful deployment")

if __name__ == "__main__":
    add_cache_bust_env() 
