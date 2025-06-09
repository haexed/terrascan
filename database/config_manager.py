"""
Configuration Manager for Terrascan
Handles dynamic configuration storage and retrieval from database
"""

import sqlite3
import json
from typing import Dict, Any, Optional
from database.db import get_db_connection

class ConfigManager:
    """Manages configuration for providers, datasets, and system settings"""
    
    def __init__(self):
        self.init_config_tables()
    
    def init_config_tables(self):
        """Initialize configuration tables"""
        with get_db_connection() as conn:
            # Provider configurations table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS provider_config (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    provider_key TEXT NOT NULL,
                    config_key TEXT NOT NULL,
                    config_value TEXT NOT NULL,
                    data_type TEXT NOT NULL DEFAULT 'string',
                    description TEXT,
                    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(provider_key, config_key)
                )
            """)
            
            # Dataset configurations table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS dataset_config (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    provider_key TEXT NOT NULL,
                    dataset_name TEXT NOT NULL,
                    config_key TEXT NOT NULL,
                    config_value TEXT NOT NULL,
                    data_type TEXT NOT NULL DEFAULT 'string',
                    description TEXT,
                    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(provider_key, dataset_name, config_key)
                )
            """)
            
            # System configurations table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS system_config (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    config_key TEXT NOT NULL UNIQUE,
                    config_value TEXT NOT NULL,
                    data_type TEXT NOT NULL DEFAULT 'string',
                    description TEXT,
                    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.commit()
    
    def get_provider_config(self, provider_key: str, config_key: str, default=None) -> Any:
        """Get provider-specific configuration"""
        with get_db_connection() as conn:
            result = conn.execute("""
                SELECT config_value, data_type 
                FROM provider_config 
                WHERE provider_key = ? AND config_key = ?
            """, (provider_key, config_key)).fetchone()
            
            if result:
                return self._parse_config_value(result['config_value'], result['data_type'])
            return default
    
    def set_provider_config(self, provider_key: str, config_key: str, config_value: Any, 
                          data_type: str = 'string', description: str = None):
        """Set provider-specific configuration"""
        value_str = self._serialize_config_value(config_value, data_type)
        
        with get_db_connection() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO provider_config 
                (provider_key, config_key, config_value, data_type, description, updated_date)
                VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (provider_key, config_key, value_str, data_type, description))
            conn.commit()
    
    def get_dataset_config(self, provider_key: str, dataset_name: str, config_key: str, default=None) -> Any:
        """Get dataset-specific configuration"""
        with get_db_connection() as conn:
            result = conn.execute("""
                SELECT config_value, data_type 
                FROM dataset_config 
                WHERE provider_key = ? AND dataset_name = ? AND config_key = ?
            """, (provider_key, dataset_name, config_key)).fetchone()
            
            if result:
                return self._parse_config_value(result['config_value'], result['data_type'])
            return default
    
    def set_dataset_config(self, provider_key: str, dataset_name: str, config_key: str, 
                         config_value: Any, data_type: str = 'string', description: str = None):
        """Set dataset-specific configuration"""
        value_str = self._serialize_config_value(config_value, data_type)
        
        with get_db_connection() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO dataset_config 
                (provider_key, dataset_name, config_key, config_value, data_type, description, updated_date)
                VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (provider_key, dataset_name, config_key, value_str, data_type, description))
            conn.commit()
    
    def get_system_config(self, config_key: str, default=None) -> Any:
        """Get system-wide configuration"""
        with get_db_connection() as conn:
            result = conn.execute("""
                SELECT config_value, data_type 
                FROM system_config 
                WHERE config_key = ?
            """, (config_key,)).fetchone()
            
            if result:
                return self._parse_config_value(result['config_value'], result['data_type'])
            return default
    
    def set_system_config(self, config_key: str, config_value: Any, 
                         data_type: str = 'string', description: str = None):
        """Set system-wide configuration"""
        value_str = self._serialize_config_value(config_value, data_type)
        
        with get_db_connection() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO system_config 
                (config_key, config_value, data_type, description, updated_date)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (config_key, value_str, data_type, description))
            conn.commit()
    
    def get_all_provider_configs(self, provider_key: str) -> Dict[str, Any]:
        """Get all configurations for a provider"""
        configs = {}
        with get_db_connection() as conn:
            results = conn.execute("""
                SELECT config_key, config_value, data_type 
                FROM provider_config 
                WHERE provider_key = ?
            """, (provider_key,)).fetchall()
            
            for result in results:
                configs[result['config_key']] = self._parse_config_value(
                    result['config_value'], result['data_type']
                )
        
        return configs
    
    def get_all_dataset_configs(self, provider_key: str, dataset_name: str) -> Dict[str, Any]:
        """Get all configurations for a specific dataset"""
        configs = {}
        with get_db_connection() as conn:
            results = conn.execute("""
                SELECT config_key, config_value, data_type 
                FROM dataset_config 
                WHERE provider_key = ? AND dataset_name = ?
            """, (provider_key, dataset_name)).fetchall()
            
            for result in results:
                configs[result['config_key']] = self._parse_config_value(
                    result['config_value'], result['data_type']
                )
        
        return configs
    
    def _parse_config_value(self, value_str: str, data_type: str) -> Any:
        """Parse configuration value based on data type"""
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
    
    def _serialize_config_value(self, value: Any, data_type: str) -> str:
        """Serialize configuration value to string"""
        if data_type == 'json':
            return json.dumps(value)
        else:
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

def get_dataset_config(provider_key: str, dataset_name: str, config_key: str, default=None):
    """Helper function to get dataset config"""
    return config_manager.get_dataset_config(provider_key, dataset_name, config_key, default)

def set_dataset_config(provider_key: str, dataset_name: str, config_key: str, config_value: Any, 
                      data_type: str = 'string', description: str = None):
    """Helper function to set dataset config"""
    return config_manager.set_dataset_config(provider_key, dataset_name, config_key, config_value, data_type, description)

def get_system_config(config_key: str, default=None):
    """Helper function to get system config"""
    return config_manager.get_system_config(config_key, default)

def set_system_config(config_key: str, config_value: Any, data_type: str = 'string', description: str = None):
    """Helper function to set system config"""
    return config_manager.set_system_config(config_key, config_value, data_type, description) 
