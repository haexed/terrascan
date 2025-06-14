#!/usr/bin/env python3
"""
Terrascan Task Runner
Executes tasks and logs results to database
"""

import sys
import os
import json
import traceback
import subprocess
import importlib
from datetime import datetime
from typing import Dict, Any

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from database.db import (
    get_task_by_name, start_task_run, complete_task_run, 
    get_running_tasks, store_metric_data
)

class TaskRunner:
    """Executes tasks and manages their lifecycle"""
    
    def __init__(self):
        self.running_tasks = set()
    
    def run_task(self, task_name: str, triggered_by: str = 'manual', 
                 trigger_parameters: Dict = None) -> Dict[str, Any]:
        """
        Run a single task and return results
        
        Returns dict with:
        - success: bool
        - run_id: int 
        - output: str
        - error: str (if failed)
        - duration: float
        - records_processed: int
        """
        # Get task definition
        task = get_task_by_name(task_name)
        if not task:
            return {
                'success': False,
                'error': f"Task '{task_name}' not found",
                'duration': 0
            }
        
        if not task['active']:
            return {
                'success': False,
                'error': f"Task '{task_name}' is disabled",
                'duration': 0
            }
        
        # Start task run
        run_id = start_task_run(
            task['id'], 
            triggered_by=triggered_by,
            trigger_parameters=trigger_parameters
        )
        
        start_time = datetime.now()
        print(f"🚀 Starting task: {task_name} (run_id: {run_id})")
        
        try:
            # Execute the task
            result = self._execute_task_command(task, trigger_parameters)
            
            # Complete successfully  
            complete_task_run(
                run_id,
                exit_code=0,
                stdout=result.get('output', ''),
                stderr=result.get('error', ''),
                actual_cost_cents=result.get('cost_cents', 0),
                records_processed=result.get('records_stored', result.get('records_processed', 0))
            )
            
            duration = (datetime.now() - start_time).total_seconds()
            print(f"✅ Task completed: {task_name} ({duration:.1f}s, {result.get('records_processed', 0)} records)")
            
            return {
                'success': True,
                'run_id': run_id,
                'output': result.get('output', ''),
                'duration': duration,
                'records_processed': result.get('records_stored', result.get('records_processed', 0)),
                'cost_cents': result.get('cost_cents', 0)
            }
            
        except Exception as e:
            # Complete with error
            error_details = traceback.format_exc()
            complete_task_run(
                run_id,
                exit_code=1,
                stderr=str(e),
                error_details=error_details
            )
            
            duration = (datetime.now() - start_time).total_seconds()
            print(f"❌ Task failed: {task_name} ({duration:.1f}s) - {str(e)}")
            
            return {
                'success': False,
                'run_id': run_id,
                'error': str(e),
                'error_details': error_details,
                'duration': duration
            }
    
    def _execute_task_command(self, task: Dict, trigger_parameters: Dict = None) -> Dict[str, Any]:
        """Execute the actual task command"""
        command = task['command']
        
        # Merge default parameters with trigger parameters
        parameters = {}
        if task['parameters']:
            parameters.update(json.loads(task['parameters']))
        if trigger_parameters:
            parameters.update(trigger_parameters)
        
        # Import and call the function
        # Command format: "module.function" (e.g., "tasks.fetch_nasa_fires")
        module_name, function_name = command.rsplit('.', 1)
        
        try:
            module = importlib.import_module(module_name)
            function = getattr(module, function_name)
            
            # Call the function with parameters
            if parameters:
                result = function(**parameters)
            else:
                result = function()
            
            return result
            
        except ImportError as e:
            raise Exception(f"Could not import {module_name}: {e}")
        except AttributeError as e:
            raise Exception(f"Function {function_name} not found in {module_name}: {e}")
        except Exception as e:
            raise Exception(f"Task execution failed: {e}")
    
    def run_scheduled_tasks(self):
        """Check for scheduled tasks that need to run (called by cron)"""
        from crontab import CronTab
        
        # Get all active tasks with cron schedules
        from database.db import get_tasks
        tasks = get_tasks(active_only=True)
        
        scheduled_tasks = [t for t in tasks if t['cron_schedule'] and t['cron_schedule'] != 'on_demand']
        
        now = datetime.now()
        tasks_run = 0
        
        for task in scheduled_tasks:
            # Check if task should run now based on cron schedule
            cron = CronTab(task['cron_schedule'])
            
            # Check if it's time to run (within the last minute)
            if cron.test(now):
                print(f"⏰ Running scheduled task: {task['name']}")
                result = self.run_task(task['name'], triggered_by='cron')
                tasks_run += 1
                
                if not result['success']:
                    print(f"⚠️ Scheduled task failed: {task['name']} - {result.get('error', 'Unknown error')}")
        
        if tasks_run == 0:
            print(f"⏰ No scheduled tasks due at {now.strftime('%Y-%m-%d %H:%M')}")
        else:
            print(f"⏰ Ran {tasks_run} scheduled tasks")
        
        return tasks_run
    
    def get_task_status(self) -> Dict[str, Any]:
        """Get current task system status"""
        running = get_running_tasks()
        
        # Get recent activity
        from database.db import get_recent_task_runs
        recent = get_recent_task_runs(limit=10)
        
        return {
            'running_tasks': len(running),
            'running_task_details': running,
            'recent_runs': recent,
            'system_status': 'operational' if len(running) < 10 else 'busy'
        }

# CLI interface
def main():
    """Command line interface for task runner"""
    if len(sys.argv) < 2:
        print("Usage: python runner.py <command> [args]")
        print("Commands:")
        print("  run <task_name>              - Run a specific task")
        print("  schedule                     - Run scheduled tasks (for cron)")
        print("  status                       - Show task system status")
        print("  list                         - List all tasks")
        return
    
    runner = TaskRunner()
    command = sys.argv[1]
    
    if command == 'run':
        if len(sys.argv) < 3:
            print("Error: Task name required")
            return
        
        task_name = sys.argv[2]
        result = runner.run_task(task_name, triggered_by='manual')
        
        if result['success']:
            print(f"Task completed successfully in {result['duration']:.1f}s")
            if result.get('records_processed', 0) > 0:
                print(f"Processed {result['records_processed']} records")
        else:
            print(f"Task failed: {result['error']}")
            sys.exit(1)
    
    elif command == 'schedule':
        tasks_run = runner.run_scheduled_tasks()
        print(f"Scheduled execution complete - {tasks_run} tasks run")
    
    elif command == 'status':
        status = runner.get_task_status()
        print(f"Running tasks: {status['running_tasks']}")
        print(f"System status: {status['system_status']}")
        
        if status['recent_runs']:
            print("\nRecent runs:")
            for run in status['recent_runs'][:5]:
                print(f"  {run['task_name']}: {run['status']} ({run['started_at']})")
    
    elif command == 'list':
        from database.db import get_tasks
        tasks = get_tasks(active_only=False)
        print(f"Found {len(tasks)} tasks:")
        for task in tasks:
            status = "✅" if task['active'] else "❌"
            schedule = task['cron_schedule'] or 'on_demand'
            print(f"  {status} {task['name']} - {schedule}")
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)

if __name__ == "__main__":
    main() 
