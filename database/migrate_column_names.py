#!/usr/bin/env python3
"""
Database Migration: Rename created_at/updated_at to created_date/updated_date
Run this script to update existing database column names to our new convention
"""

import sqlite3
import os
import sys
from typing import List

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

DB_PATH = os.path.join(os.path.dirname(__file__), 'terrascan.db')

def check_column_exists(conn: sqlite3.Connection, table_name: str, column_name: str) -> bool:
    """Check if a column exists in a table"""
    cursor = conn.execute(f"PRAGMA table_info({table_name})")
    columns = [row[1] for row in cursor.fetchall()]
    return column_name in columns

def migrate_table_columns(conn: sqlite3.Connection, table_name: str) -> List[str]:
    """Migrate created_at/updated_at columns to created_date/updated_date for a specific table"""
    changes = []
    
    # Check which columns need to be renamed
    has_created_at = check_column_exists(conn, table_name, 'created_at')
    has_updated_at = check_column_exists(conn, table_name, 'updated_at')
    has_created_date = check_column_exists(conn, table_name, 'created_date')
    has_updated_date = check_column_exists(conn, table_name, 'updated_date')
    
    if has_created_at and not has_created_date:
        try:
            conn.execute(f"ALTER TABLE {table_name} ADD COLUMN created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
            conn.execute(f"UPDATE {table_name} SET created_date = created_at")
            changes.append(f"  ✅ {table_name}.created_at → created_date")
        except Exception as e:
            changes.append(f"  ❌ {table_name}.created_at migration failed: {e}")
    
    if has_updated_at and not has_updated_date:
        try:
            conn.execute(f"ALTER TABLE {table_name} ADD COLUMN updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
            conn.execute(f"UPDATE {table_name} SET updated_date = updated_at")
            changes.append(f"  ✅ {table_name}.updated_at → updated_date")
        except Exception as e:
            changes.append(f"  ❌ {table_name}.updated_at migration failed: {e}")
    
    return changes

def main():
    """Run the column migration"""
    print("🔄 Starting database column migration: created_at/updated_at → created_date/updated_date")
    
    if not os.path.exists(DB_PATH):
        print(f"❌ Database not found: {DB_PATH}")
        print("💡 Run the system first to create the database, then run this migration")
        return
    
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        
        # Get all tables
        cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
        tables = [row[0] for row in cursor.fetchall()]
        
        print(f"🔍 Found {len(tables)} tables to check: {', '.join(tables)}")
        
        all_changes = []
        
        # Process each table
        for table in tables:
            table_changes = migrate_table_columns(conn, table)
            if table_changes:
                all_changes.extend([f"📋 Table: {table}"] + table_changes)
        
        if all_changes:
            conn.commit()
            print("\n📊 Migration Summary:")
            for change in all_changes:
                print(change)
            print(f"\n✅ Migration completed! Updated {len([c for c in all_changes if '✅' in c])} columns")
            print("\n⚠️  Note: Old columns (created_at/updated_at) are preserved for safety")
            print("   You can drop them manually later if desired:")
            for table in tables:
                print(f"   -- ALTER TABLE {table} DROP COLUMN created_at;")
                print(f"   -- ALTER TABLE {table} DROP COLUMN updated_at;")
        else:
            print("✅ No migration needed - all columns already use the new naming convention!")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 
