#!/usr/bin/env python3
"""
Add scanned_regions table for lazy-loading regional data
This enables the "scan as you go" feature for Terrascan
"""

import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db import get_db_connection, execute_query

def create_scanned_regions_table():
    """Create the scanned_regions table for tracking cached geographic areas"""

    create_table_sql = """
    CREATE TABLE IF NOT EXISTS scanned_regions (
        id SERIAL PRIMARY KEY,
        bbox_north DECIMAL(10, 7) NOT NULL,
        bbox_south DECIMAL(10, 7) NOT NULL,
        bbox_east DECIMAL(10, 7) NOT NULL,
        bbox_west DECIMAL(10, 7) NOT NULL,
        zoom_level INTEGER NOT NULL,
        first_scanned TIMESTAMP DEFAULT NOW(),
        last_updated TIMESTAMP DEFAULT NOW(),
        data_points_cached INTEGER DEFAULT 0,
        layers_scanned TEXT[] DEFAULT '{}',  -- Array of layer names: fires, air, ocean, etc.
        scan_triggered_by VARCHAR(50) DEFAULT 'user',  -- 'user', 'auto', 'prefetch'
        CONSTRAINT valid_bbox CHECK (
            bbox_north > bbox_south AND
            bbox_east > bbox_west AND
            bbox_north >= -90 AND bbox_north <= 90 AND
            bbox_south >= -90 AND bbox_south <= 90 AND
            bbox_east >= -180 AND bbox_east <= 180 AND
            bbox_west >= -180 AND bbox_west <= 180
        ),
        CONSTRAINT valid_zoom CHECK (zoom_level >= 0 AND zoom_level <= 20)
    );

    -- Create index on bounding box for fast spatial queries
    CREATE INDEX IF NOT EXISTS idx_scanned_regions_bbox
    ON scanned_regions (bbox_north, bbox_south, bbox_east, bbox_west);

    -- Create index on last_updated for freshness checks
    CREATE INDEX IF NOT EXISTS idx_scanned_regions_updated
    ON scanned_regions (last_updated);

    -- Create index on zoom level for layer filtering
    CREATE INDEX IF NOT EXISTS idx_scanned_regions_zoom
    ON scanned_regions (zoom_level);
    """

    print("🗺️  Creating scanned_regions table...")

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Execute the SQL
        cursor.execute(create_table_sql)
        conn.commit()

        print("✅ scanned_regions table created successfully")
        print("✅ Indexes created for spatial queries")

        # Verify the table
        cursor.execute("""
            SELECT COUNT(*) as count
            FROM information_schema.tables
            WHERE table_name = 'scanned_regions'
        """)
        result = cursor.fetchone()

        if result and result[0] > 0:
            print("✅ Table verified in database")

        cursor.close()
        conn.close()

        return True

    except Exception as e:
        print(f"❌ Error creating scanned_regions table: {e}")
        return False


def add_helper_functions():
    """Add database helper functions for region queries"""

    functions_sql = """
    -- Function to check if a bounding box overlaps with any scanned region
    CREATE OR REPLACE FUNCTION check_region_overlap(
        p_north DECIMAL, p_south DECIMAL, p_east DECIMAL, p_west DECIMAL,
        p_zoom INTEGER, p_max_age_hours INTEGER DEFAULT 24
    ) RETURNS TABLE(
        id INTEGER,
        bbox_north DECIMAL,
        bbox_south DECIMAL,
        bbox_east DECIMAL,
        bbox_west DECIMAL,
        last_updated TIMESTAMP,
        data_points_cached INTEGER,
        layers_scanned TEXT[]
    ) AS $$
    BEGIN
        RETURN QUERY
        SELECT
            sr.id,
            sr.bbox_north,
            sr.bbox_south,
            sr.bbox_east,
            sr.bbox_west,
            sr.last_updated,
            sr.data_points_cached,
            sr.layers_scanned
        FROM scanned_regions sr
        WHERE
            -- Check for bounding box overlap
            sr.bbox_north >= p_south AND
            sr.bbox_south <= p_north AND
            sr.bbox_east >= p_west AND
            sr.bbox_west <= p_east AND
            -- Same or similar zoom level (within 1 level)
            ABS(sr.zoom_level - p_zoom) <= 1 AND
            -- Data is fresh enough
            sr.last_updated > NOW() - INTERVAL '1 hour' * p_max_age_hours
        ORDER BY sr.last_updated DESC;
    END;
    $$ LANGUAGE plpgsql;

    -- Function to get region coverage statistics
    CREATE OR REPLACE FUNCTION get_scan_statistics()
    RETURNS TABLE(
        total_regions INTEGER,
        total_data_points BIGINT,
        oldest_scan TIMESTAMP,
        newest_scan TIMESTAMP,
        avg_points_per_region DECIMAL
    ) AS $$
    BEGIN
        RETURN QUERY
        SELECT
            COUNT(*)::INTEGER as total_regions,
            SUM(data_points_cached)::BIGINT as total_data_points,
            MIN(first_scanned) as oldest_scan,
            MAX(last_updated) as newest_scan,
            AVG(data_points_cached) as avg_points_per_region
        FROM scanned_regions;
    END;
    $$ LANGUAGE plpgsql;
    """

    print("📊 Creating helper functions...")

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(functions_sql)
        conn.commit()

        print("✅ Helper functions created:")
        print("   - check_region_overlap()")
        print("   - get_scan_statistics()")

        cursor.close()
        conn.close()

        return True

    except Exception as e:
        print(f"❌ Error creating helper functions: {e}")
        return False


def main():
    """Run the migration"""
    print("=" * 60)
    print("TERRASCAN - Scanned Regions Migration")
    print("Adding lazy-loading regional scan capabilities")
    print("=" * 60)
    print()

    # Step 1: Create table
    if not create_scanned_regions_table():
        print("❌ Migration failed at table creation")
        sys.exit(1)

    print()

    # Step 2: Add helper functions
    if not add_helper_functions():
        print("❌ Migration failed at helper function creation")
        sys.exit(1)

    print()
    print("=" * 60)
    print("🎉 Migration completed successfully!")
    print("=" * 60)
    print()
    print("📋 Summary:")
    print("   ✅ scanned_regions table created")
    print("   ✅ Spatial indexes added")
    print("   ✅ Helper functions installed")
    print()
    print("🚀 Terrascan is now ready for 'scan as you go' functionality!")
    print()


if __name__ == "__main__":
    main()
