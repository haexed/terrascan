"""
Configuration Manager for Terrascan
Handles dynamic configuration storage and retrieval from database
Compatible with both SQLite (local) and PostgreSQL (production)
"""

import os
import json
from typing import Dict, Any, Optional
from database.db import execute_query, execute_insert, IS_PRODUCTION

class ConfigManager:
    """Manages configuration for providers, datasets, and system settings"""
    
    def __init__(self):
        self.init_config_tables()
    
    def init_config_tables(self):
        """Initialize configuration tables (handled by main db.py init)"""
        # Tables are created by the main database initialization
        # This is just a placeholder for compatibility
        pass
    
    def get_provider_config(self, provider_key: str, config_key: str, default=None) -> Any:
        """Get provider-specific configuration"""
        try:
            if IS_PRODUCTION:
                query = """
                    SELECT value, data_type 
                    FROM provider_config 
                    WHERE provider = %s AND key = %s
                """
            else:
                query = """
                    SELECT value, data_type 
                    FROM provider_config 
                    WHERE provider = ? AND key = ?
                """
            
            results = execute_query(query, (provider_key, config_key))
            
            if results:
                result = results[0]
                return self._parse_config_value(result['value'], result['data_type'])
            return default
        except Exception as e:
            print(f"❌ Error getting provider config: {e}")
            return default
    
    def set_provider_config(self, provider_key: str, config_key: str, config_value: Any, 
                          data_type: str = 'string', description: str = None):
        """Set provider-specific configuration"""
        try:
            value_str = self._serialize_config_value(config_value, data_type)
            
            if IS_PRODUCTION:
                query = """
                    INSERT INTO provider_config (provider, key, value, data_type, description)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (provider, key) DO UPDATE SET
                        value = EXCLUDED.value,
                        data_type = EXCLUDED.data_type,
                        description = EXCLUDED.description,
                        updated_date = CURRENT_TIMESTAMP
                """
            else:
                query = """
                    INSERT OR REPLACE INTO provider_config 
                    (provider, key, value, data_type, description, updated_date)
                    VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                """
            
            return execute_insert(query, (provider_key, config_key, value_str, data_type, description))
        except Exception as e:
            print(f"❌ Error setting provider config: {e}")
            return False
    
    def get_system_config(self, config_key: str, default=None) -> Any:
        """Get system-wide configuration"""
        try:
            if IS_PRODUCTION:
                query = """
                    SELECT value, data_type 
                    FROM system_config 
                    WHERE key = %s
                """
            else:
                query = """
                    SELECT value, data_type 
                    FROM system_config 
                    WHERE key = ?
                """
            
            results = execute_query(query, (config_key,))
            
            if results:
                result = results[0]
                return self._parse_config_value(result['value'], result['data_type'])
            return default
        except Exception as e:
            print(f"❌ Error getting system config: {e}")
            return default
    
    def set_system_config(self, config_key: str, config_value: Any, 
                         data_type: str = 'string', description: str = None):
        """Set system-wide configuration"""
        try:
            value_str = self._serialize_config_value(config_value, data_type)
            
            if IS_PRODUCTION:
                query = """
                    INSERT INTO system_config (key, value, data_type, description)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (key) DO UPDATE SET
                        value = EXCLUDED.value,
                        data_type = EXCLUDED.data_type,
                        description = EXCLUDED.description,
                        updated_date = CURRENT_TIMESTAMP
                """
            else:
                query = """
                    INSERT OR REPLACE INTO system_config 
                    (key, value, data_type, description, updated_date)
                    VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
                """
            
            return execute_insert(query, (config_key, value_str, data_type, description))
        except Exception as e:
            print(f"❌ Error setting system config: {e}")
            return False
    
    def get_all_provider_configs(self, provider_key: str) -> Dict[str, Any]:
        """Get all configurations for a provider"""
        try:
            configs = {}
            
            if IS_PRODUCTION:
                query = """
                    SELECT key, value, data_type 
                    FROM provider_config 
                    WHERE provider = %s
                """
            else:
                query = """
                    SELECT key, value, data_type 
                    FROM provider_config 
                    WHERE provider = ?
                """
            
            results = execute_query(query, (provider_key,))
            
            for result in results:
                configs[result['key']] = self._parse_config_value(
                    result['value'], result['data_type']
                )
            
            return configs
        except Exception as e:
            print(f"❌ Error getting all provider configs: {e}")
            return {}
    
    def _parse_config_value(self, value_str: str, data_type: str) -> Any:
        """Parse configuration value based on data type"""
        try:
            if data_type == 'json':
                return json.loads(value_str)
            elif data_type == 'int':
                return int(value_str)
            elif data_type == 'float':
                return float(value_str)
            elif data_type == 'bool':
                return value_str.lower() in ('true', '1', 'yes', 'on')
            else:  # string
                return value_str
        except Exception as e:
            print(f"❌ Error parsing config value: {e}")
            return value_str
    
    def _serialize_config_value(self, value: Any, data_type: str) -> str:
        """Serialize configuration value to string"""
        try:
            if data_type == 'json':
                return json.dumps(value)
            else:
                return str(value)
        except Exception as e:
            print(f"❌ Error serializing config value: {e}")
            return str(value)

# Global config manager instance
config_manager = ConfigManager()

# Helper functions for easy access
def get_provider_config(provider_key: str, config_key: str, default=None):
    """Helper function to get provider config"""
    return config_manager.get_provider_config(provider_key, config_key, default)

def set_provider_config(provider_key: str, config_key: str, config_value: Any, 
                       data_type: str = 'string', description: str = None):
    """Helper function to set provider config"""
    return config_manager.set_provider_config(provider_key, config_key, config_value, data_type, description)

def get_system_config(config_key: str, default=None):
    """Helper function to get system config"""
    return config_manager.get_system_config(config_key, default)

def set_system_config(config_key: str, config_value: Any, data_type: str = 'string', description: str = None):
    """Helper function to set system config"""
    return config_manager.set_system_config(config_key, config_value, data_type, description) 
