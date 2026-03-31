#!/usr/bin/env python3
"""
Database Migration: Drop Redundant Indexes & Enforce Data Retention

Index analysis (metric_data table, 5.6M rows, 2.6GB indexes):
- Many indexes were created by multiple migration scripts, causing duplicates
- The unique constraint (unique_metric_measurement) already creates an implicit index
  that covers provider_key + metric_name lookups
- Single-column indexes on provider_key are redundant with composite indexes

Indexes kept (4):
  1. PK on id
  2. unique_metric_measurement (provider_key, metric_name, timestamp, lat, lng) — dedup + lookups
  3. idx_metric_provider_timestamp (provider_key, timestamp DESC) — time-range queries
  4. idx_metric_location (lat, lng) WHERE NOT NULL — spatial queries

Indexes dropped (7):
  - idx_metric_data_provider — redundant with composites
  - idx_metric_provider — duplicate of above
  - idx_metric_data_timestamp — most queries filter by provider first
  - idx_metric_timestamp — near-duplicate
  - idx_metric_data_location — redundant with partial index
  - idx_metric_provider_metric — covered by unique constraint
  - idx_metric_dedup — identical to unique constraint's implicit index
"""

import os
import psycopg2


def get_connection():
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        print("DATABASE_URL not found")
        return None
    return psycopg2.connect(database_url)


def show_current_indexes(cursor):
    """Show all indexes on metric_data with their sizes"""
    cursor.execute("""
        SELECT indexname, pg_size_pretty(pg_relation_size(indexname::regclass)) as size
        FROM pg_indexes
        WHERE tablename = 'metric_data'
        ORDER BY pg_relation_size(indexname::regclass) DESC
    """)
    rows = cursor.fetchall()
    print(f"\nFound {len(rows)} indexes on metric_data:")
    for name, size in rows:
        print(f"  {size:>10}  {name}")
    return [row[0] for row in rows]


def drop_redundant_indexes(cursor):
    """Drop indexes that are redundant with the unique constraint and composite indexes"""
    redundant = [
        'idx_metric_data_provider',   # redundant with composites
        'idx_metric_provider',        # duplicate single-column on provider_key
        'idx_metric_data_timestamp',  # most queries filter by provider first
        'idx_metric_timestamp',       # near-duplicate
        'idx_metric_data_location',   # redundant with partial index
        'idx_metric_provider_metric', # covered by unique_metric_measurement
        'idx_metric_dedup',           # identical to unique constraint's implicit index
    ]

    existing = show_current_indexes(cursor)

    dropped = 0
    for idx in redundant:
        if idx in existing:
            print(f"  Dropping {idx}...")
            cursor.execute(f"DROP INDEX IF EXISTS {idx}")
            dropped += 1
        else:
            print(f"  {idx} — not found, skipping")

    print(f"\nDropped {dropped} redundant indexes")
    return dropped


def enforce_data_retention(cursor):
    """Delete metric_data older than data_retention_days (default 30)"""
    # Read retention config from system_config
    cursor.execute(
        "SELECT value FROM system_config WHERE key = 'data_retention_days'"
    )
    row = cursor.fetchone()
    retention_days = int(row[0]) if row else 30

    print(f"\nData retention: {retention_days} days")

    # Count what we'll delete
    cursor.execute(
        "SELECT COUNT(*) FROM metric_data WHERE timestamp < NOW() - INTERVAL '%s days'",
        (retention_days,)
    )
    stale_count = cursor.fetchone()[0]
    print(f"Records older than {retention_days} days: {stale_count:,}")

    if stale_count == 0:
        print("Nothing to delete")
        return 0

    # Delete in batches to avoid long locks
    total_deleted = 0
    batch_size = 50000
    while True:
        cursor.execute("""
            DELETE FROM metric_data
            WHERE id IN (
                SELECT id FROM metric_data
                WHERE timestamp < NOW() - INTERVAL '%s days'
                LIMIT %s
            )
        """, (retention_days, batch_size))
        deleted = cursor.rowcount
        total_deleted += deleted
        if deleted > 0:
            print(f"  Deleted batch: {deleted:,} (total: {total_deleted:,})")
            # Commit each batch to release locks
            cursor.connection.commit()
        if deleted < batch_size:
            break

    print(f"Total deleted: {total_deleted:,} stale records")
    return total_deleted


def cleanup_task_logs(cursor):
    """Delete task_log entries older than 90 days"""
    cursor.execute(
        "SELECT COUNT(*) FROM task_log WHERE started_at < NOW() - INTERVAL '90 days'"
    )
    stale = cursor.fetchone()[0]
    if stale > 0:
        cursor.execute(
            "DELETE FROM task_log WHERE started_at < NOW() - INTERVAL '90 days'"
        )
        print(f"Deleted {stale:,} old task_log entries")
    else:
        print("No old task_log entries to clean")
    return stale


def vacuum_tables(conn):
    """Run VACUUM ANALYZE to reclaim space after deletions"""
    print("\nRunning VACUUM ANALYZE to reclaim disk space...")
    old_isolation = conn.isolation_level
    conn.set_isolation_level(0)  # AUTOCOMMIT required for VACUUM
    cursor = conn.cursor()
    cursor.execute("VACUUM ANALYZE metric_data")
    cursor.execute("VACUUM ANALYZE task_log")
    conn.set_isolation_level(old_isolation)
    print("VACUUM complete")


def main():
    print("Terrascan: Index Cleanup & Data Retention")
    print("=" * 50)

    conn = get_connection()
    if not conn:
        return False

    try:
        cursor = conn.cursor()

        # Step 1: Show current state
        cursor.execute("SELECT COUNT(*) FROM metric_data")
        total = cursor.fetchone()[0]
        print(f"\nmetric_data: {total:,} rows")

        # Step 2: Drop redundant indexes
        print("\n--- Dropping redundant indexes ---")
        drop_redundant_indexes(cursor)
        conn.commit()

        # Step 3: Show remaining indexes
        print("\n--- Remaining indexes ---")
        show_current_indexes(cursor)

        # Step 4: Enforce data retention
        print("\n--- Enforcing data retention ---")
        enforce_data_retention(cursor)

        # Step 5: Clean old task logs
        print("\n--- Cleaning old task logs ---")
        cleanup_task_logs(cursor)
        conn.commit()

        # Step 6: VACUUM to reclaim space
        vacuum_tables(conn)

        # Step 7: Final stats
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM metric_data")
        remaining = cursor.fetchone()[0]
        print(f"\nFinal: {remaining:,} rows (was {total:,}, removed {total - remaining:,})")
        show_current_indexes(cursor)

        cursor.close()
        conn.close()
        print("\nDone!")
        return True

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        conn.close()
        return False


if __name__ == "__main__":
    main()
