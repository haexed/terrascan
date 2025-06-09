#!/usr/bin/env python3
"""
Daily Cost Calculator
Calculates and summarizes daily API costs and usage statistics
"""

import sys
import os
from datetime import datetime, timedelta
from typing import Dict, Any

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from database.db import execute_query, execute_insert

def calculate_daily_costs(days_back: int = 7) -> Dict[str, Any]:
    """
    Calculate daily costs and usage statistics for the specified number of days
    
    Args:
        days_back: Number of days to analyze (default: 7)
    
    Returns:
        Dict with execution results
    """
    
    try:
        print(f"💰 Calculating daily costs for the last {days_back} days...")
        
        # Get daily cost summary from task logs
        daily_costs = execute_query("""
            SELECT 
                DATE(started_at) as date,
                SUM(actual_cost_cents) as total_cost_cents,
                COUNT(*) as total_runs,
                SUM(records_processed) as total_records,
                COUNT(DISTINCT task_id) as unique_tasks,
                AVG(duration_seconds) as avg_duration,
                SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as successful_runs,
                SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed_runs
            FROM task_log 
            WHERE started_at >= date('now', '-{} days')
            GROUP BY DATE(started_at)
            ORDER BY date DESC
        """.format(days_back))
        
        # Get provider-specific costs
        provider_costs = execute_query("""
            SELECT 
                t.provider,
                SUM(tl.actual_cost_cents) as total_cost_cents,
                COUNT(tl.id) as total_runs,
                SUM(tl.records_processed) as total_records
            FROM task_log tl
            JOIN task t ON tl.task_id = t.id
            WHERE tl.started_at >= date('now', '-{} days')
            AND t.provider IS NOT NULL
            GROUP BY t.provider
            ORDER BY total_cost_cents DESC
        """.format(days_back))
        
        # Calculate totals
        total_cost_cents = sum(day['total_cost_cents'] or 0 for day in daily_costs)
        total_runs = sum(day['total_runs'] or 0 for day in daily_costs)
        total_records = sum(day['total_records'] or 0 for day in daily_costs)
        total_successful = sum(day['successful_runs'] or 0 for day in daily_costs)
        
        # Calculate success rate
        success_rate = (total_successful / total_runs * 100) if total_runs > 0 else 0
        
        # Store summary in cost_summary table (if it exists, create it if not)
        try:
            # Try to create cost_summary table if it doesn't exist
            execute_query("""
                CREATE TABLE IF NOT EXISTS cost_summary (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL,
                    total_cost_cents INTEGER DEFAULT 0,
                    total_runs INTEGER DEFAULT 0,
                    total_records INTEGER DEFAULT 0,
                    success_rate REAL DEFAULT 0,
                    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Insert today's summary
            today = datetime.now().strftime('%Y-%m-%d')
            execute_insert("""
                INSERT OR REPLACE INTO cost_summary 
                (date, total_cost_cents, total_runs, total_records, success_rate)
                VALUES (?, ?, ?, ?, ?)
            """, (today, total_cost_cents, total_runs, total_records, success_rate))
            
        except Exception as e:
            print(f"⚠️ Could not store cost summary: {e}")
        
        # Format output message
        output_lines = [
            f"📊 Daily Cost Analysis ({days_back} days):",
            f"💰 Total Cost: ${total_cost_cents / 100:.2f}",
            f"🔄 Total Runs: {total_runs}",
            f"📈 Total Records: {total_records:,}",
            f"✅ Success Rate: {success_rate:.1f}%",
            "",
            "📅 Daily Breakdown:"
        ]
        
        for day in daily_costs:
            cost_dollars = (day['total_cost_cents'] or 0) / 100
            success_pct = ((day['successful_runs'] or 0) / (day['total_runs'] or 1)) * 100
            output_lines.append(
                f"  {day['date']}: ${cost_dollars:.2f}, {day['total_runs']} runs, "
                f"{day['total_records'] or 0:,} records, {success_pct:.0f}% success"
            )
        
        if provider_costs:
            output_lines.extend(["", "🌐 Provider Costs:"])
            for provider in provider_costs:
                cost_dollars = (provider['total_cost_cents'] or 0) / 100
                output_lines.append(
                    f"  {provider['provider']}: ${cost_dollars:.2f}, "
                    f"{provider['total_runs']} runs, {provider['total_records'] or 0:,} records"
                )
        
        output_msg = "\n".join(output_lines)
        print(f"✅ Cost calculation completed")
        
        return {
            'output': output_msg,
            'records_processed': len(daily_costs),
            'cost_cents': 0  # This task itself is free
        }
        
    except Exception as e:
        raise Exception(f"Error calculating daily costs: {e}")

def calculate_weekly_summary() -> Dict[str, Any]:
    """Calculate weekly cost summary"""
    return calculate_daily_costs(days_back=7)

def calculate_monthly_summary() -> Dict[str, Any]:
    """Calculate monthly cost summary"""
    return calculate_daily_costs(days_back=30)

if __name__ == "__main__":
    # Test the function
    result = calculate_daily_costs()
    print(f"Result: {result}") 
