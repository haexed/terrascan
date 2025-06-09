#!/usr/bin/env python3
"""
Terrascan Web Interface
Simple Flask app for task management and monitoring
"""

import sys
import os
import json
import requests
from datetime import datetime, timedelta
from flask import Flask, render_template, request, jsonify, redirect, url_for
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from database.db import (
    init_database, get_tasks, get_recent_task_runs, get_running_tasks,
    get_daily_costs, execute_query, get_task_by_name
)
from tasks.runner import TaskRunner
from version import get_version

# Create Flask app with proper static folder configuration
app = Flask(__name__, 
            static_folder='static',
            static_url_path='/static')
app.config['SECRET_KEY'] = 'dev-key-change-in-prod'

# Initialize database on startup
init_database()

# Add version to all templates
@app.context_processor
def inject_version():
    return {'version': get_version()}

@app.route('/')
def dashboard():
    """Main dashboard showing system overview"""
    try:
        # Get system statistics
        all_tasks = get_tasks(active_only=False)
        all_runs = get_recent_task_runs(limit=100)
        
        # Calculate stats
        total_records = execute_query("SELECT COUNT(*) as count FROM metric_data")[0]['count']
        total_cost_cents = sum(run['actual_cost_cents'] or 0 for run in all_runs)
        
        stats = {
            'total_tasks': len(all_tasks),
            'total_runs': len(all_runs),
            'total_records': total_records,
            'total_cost_cents': total_cost_cents
        }
        
        # Get recent activity (last 10 runs)
        recent_logs = get_recent_task_runs(limit=10)
        
        # Get quick action tasks (active tasks)
        quick_tasks = [task for task in all_tasks if task.get('is_active', True)][:3]
        
        return render_template('dashboard.html', 
                             stats=stats,
                             recent_logs=recent_logs,
                             quick_tasks=quick_tasks)
    except Exception as e:
        return f"Dashboard Error: {e}", 500

@app.route('/tasks')
def tasks_page():
    """Tasks management page"""
    try:
        tasks = get_tasks(active_only=False)
        recent_runs = get_recent_task_runs(limit=20)
        
        return render_template('tasks.html', 
                             tasks=tasks,
                             recent_runs=recent_runs)
    except Exception as e:
        return f"Tasks Error: {e}", 500

@app.route('/api/run_task/<task_name>', methods=['POST'])
def api_run_task(task_name):
    """API endpoint to run a task manually"""
    try:
        runner = TaskRunner()
        
        # Get optional parameters from request
        trigger_params = request.json if request.is_json else {}
        
        result = runner.run_task(
            task_name, 
            triggered_by='web_ui',
            trigger_parameters=trigger_params
        )
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/task_status')
def api_task_status():
    """API endpoint for task system status"""
    try:
        runner = TaskRunner()
        status = runner.get_task_status()
        return jsonify(status)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/data')
def data_page():
    """Data exploration page"""
    try:
        # Calculate overview stats
        total_records = execute_query("SELECT COUNT(*) as count FROM metric_data")[0]['count']
        total_providers = execute_query("SELECT COUNT(*) as count FROM provider")[0]['count']
        active_data_providers = execute_query("SELECT COUNT(DISTINCT provider_key) as count FROM metric_data")[0]['count']
        unique_datasets = execute_query("SELECT COUNT(DISTINCT dataset) as count FROM metric_data")[0]['count']
        
        # Calculate date range
        date_range = execute_query("""
            SELECT MIN(DATE(timestamp)) as earliest, MAX(DATE(timestamp)) as latest 
            FROM metric_data
        """)[0]
        
        date_range_days = 0
        if date_range['earliest'] and date_range['latest']:
            from datetime import datetime
            earliest = datetime.strptime(date_range['earliest'], '%Y-%m-%d')
            latest = datetime.strptime(date_range['latest'], '%Y-%m-%d')
            date_range_days = (latest - earliest).days + 1
        
        # Get dataset statistics
        dataset_stats = execute_query("""
            SELECT provider_key, dataset,
                   COUNT(*) as record_count,
                   MAX(timestamp) as latest_timestamp,
                   COUNT(DISTINCT metric_name) as unique_metrics
            FROM metric_data
            GROUP BY provider_key, dataset
            ORDER BY record_count DESC
        """)
        
        # Get recent data samples
        recent_data = execute_query("""
            SELECT * FROM metric_data 
            ORDER BY created_date DESC 
            LIMIT 50
        """)
        
        return render_template('data.html',
                             total_records=total_records,
                             total_providers=total_providers,
                             active_data_providers=active_data_providers,
                             unique_datasets=unique_datasets,
                             date_range_days=date_range_days,
                             dataset_stats=dataset_stats,
                             recent_data=recent_data)
    except Exception as e:
        return f"Data Error: {e}", 500

@app.route('/system')
def system_page():
    """System logs and transparency page"""
    try:
        # Get system logs
        logs = get_recent_task_runs(limit=50)
        
        # Calculate system health stats
        total_runs = len(logs)
        successful_runs = len([r for r in logs if r['status'] == 'completed'])
        success_rate = (successful_runs / total_runs * 100) if total_runs > 0 else 0
        running_tasks = len([r for r in logs if r['status'] == 'running'])
        
        system_health = {
            'status': 'operational' if success_rate > 80 else 'degraded',
            'running_tasks': running_tasks,
            'success_rate': round(success_rate, 1),
            'uptime_days': 1  # Placeholder
        }
        
        # Get system configuration (placeholder data since config table doesn't exist yet)
        system_config = [
            {'key': 'simulation_mode', 'value': 'true', 'value_type': 'boolean', 'description': 'Use simulated data when API keys are not available'},
            {'key': 'log_retention_days', 'value': '30', 'value_type': 'integer', 'description': 'Number of days to keep task logs'},
            {'key': 'max_concurrent_tasks', 'value': '5', 'value_type': 'integer', 'description': 'Maximum number of tasks that can run simultaneously'}
        ]
        
        return render_template('system.html',
                             logs=logs,
                             system_health=system_health,
                             system_config=system_config)
    except Exception as e:
        return f"System Error: {e}", 500

@app.route('/api/data/fires')
def api_fire_data():
    """API endpoint for fire data (for map visualization)"""
    try:
        # Get recent fire data
        fires = execute_query("""
            SELECT location_lat as lat, location_lng as lng, 
                   value as brightness, timestamp, metadata
            FROM metric_data 
            WHERE provider_key = 'nasa_firms' 
            AND dataset = 'active_fires'
            AND created_date > datetime('now', '-7 days')
            ORDER BY timestamp DESC
            LIMIT 1000
        """)
        
        # Parse metadata for additional info
        for fire in fires:
            if fire['metadata']:
                try:
                    fire['metadata'] = json.loads(fire['metadata'])
                except:
                    fire['metadata'] = {}
        
        return jsonify(fires)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/providers')
def api_providers():
    """API endpoint for all providers"""
    try:
        providers = execute_query("""
            SELECT p.*, 
                   COUNT(DISTINCT md.dataset) as dataset_count,
                   COUNT(md.id) as total_records,
                   MAX(md.created_date) as last_data_collected
            FROM provider p
            LEFT JOIN metric_data md ON p.key = md.provider_key
            GROUP BY p.id
            ORDER BY p.name
        """)
        return jsonify(providers)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/task_source/<task_name>')
def api_task_source(task_name):
    """API endpoint to view task source code"""
    try:
        task = get_task_by_name(task_name)
        if not task:
            return jsonify({'error': 'Task not found'}), 404
        
        # Get the command and parse module path
        command = task['command']
        if '.' not in command:
            return jsonify({'error': 'Invalid command format'}), 400
        
        module_path, function_name = command.rsplit('.', 1)
        
        # Convert module path to file path
        file_path = module_path.replace('.', '/') + '.py'
        
        try:
            with open(file_path, 'r') as f:
                source_code = f.read()
            
            return jsonify({
                'task_name': task_name,
                'file_path': file_path,
                'function_name': function_name,
                'source_code': source_code,
                'command': command
            })
        except FileNotFoundError:
            return jsonify({'error': f'Source file not found: {file_path}'}), 404
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/schema')
def schema_page():
    """Database schema visualization page"""
    try:
        # Get all table information
        tables = execute_query("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        
        schema_info = {}
        for table in tables:
            table_name = table['name']
            
            # Get column information
            columns = execute_query(f"PRAGMA table_info({table_name})")
            
            # Get foreign keys
            foreign_keys = execute_query(f"PRAGMA foreign_key_list({table_name})")
            
            # Get indexes
            indexes = execute_query(f"PRAGMA index_list({table_name})")
            
            # Get row count
            try:
                row_count = execute_query(f"SELECT COUNT(*) as count FROM {table_name}")[0]['count']
            except:
                row_count = 0
            
            schema_info[table_name] = {
                'columns': columns,
                'foreign_keys': foreign_keys,
                'indexes': indexes,
                'row_count': row_count
            }
        
        return render_template('schema.html', schema_info=schema_info)
    except Exception as e:
        return f"Schema Error: {e}", 500

@app.route('/metrics')
def metrics_page():
    """Metrics overview and analysis page"""
    try:
        # Get all unique metrics with statistics
        metrics_overview = execute_query("""
            SELECT provider_key, dataset, metric_name, unit,
                   COUNT(*) as record_count,
                   MIN(value) as min_value,
                   MAX(value) as max_value,
                   AVG(value) as avg_value,
                   MIN(timestamp) as earliest_timestamp,
                   MAX(timestamp) as latest_timestamp,
                   COUNT(DISTINCT location_lat || ',' || location_lng) as unique_locations
            FROM metric_data
            GROUP BY provider_key, dataset, metric_name, unit
            ORDER BY provider_key, dataset, metric_name
        """)
        
        # Get provider information
        providers = execute_query("SELECT key, name, description FROM provider")
        provider_info = {p['key']: p for p in providers}
        
        # Group metrics by provider
        metrics_by_provider = {}
        for metric in metrics_overview:
            provider_key = metric['provider_key']
            if provider_key not in metrics_by_provider:
                metrics_by_provider[provider_key] = {
                    'info': provider_info.get(provider_key, {'name': provider_key, 'description': 'Unknown provider'}),
                    'datasets': {}
                }
            
            dataset = metric['dataset']
            if dataset not in metrics_by_provider[provider_key]['datasets']:
                metrics_by_provider[provider_key]['datasets'][dataset] = []
            
            metrics_by_provider[provider_key]['datasets'][dataset].append(metric)
        
        # Calculate summary statistics
        total_metrics = len(metrics_overview)
        total_providers = len(metrics_by_provider)
        total_datasets = len(set(m['dataset'] for m in metrics_overview))
        total_records = sum(m['record_count'] for m in metrics_overview)
        
        summary_stats = {
            'total_metrics': total_metrics,
            'total_providers': total_providers,
            'total_datasets': total_datasets,
            'total_records': total_records
        }
        
        return render_template('metrics.html',
                             metrics_by_provider=metrics_by_provider,
                             summary_stats=summary_stats)
    except Exception as e:
        return f"Metrics Error: {e}", 500

@app.route('/providers')
def providers_page():
    """Providers and datasets page"""
    try:
        # Calculate overview stats
        total_providers = execute_query("SELECT COUNT(*) as count FROM provider")[0]['count']
        active_providers = execute_query("SELECT COUNT(*) as count FROM provider WHERE active = 1")[0]['count']
        total_datasets = execute_query("SELECT COUNT(DISTINCT dataset) as count FROM metric_data")[0]['count']
        total_api_cost = sum(run['actual_cost_cents'] or 0 for run in get_recent_task_runs(limit=1000))
        
        # Get providers with enhanced statistics
        providers_data = execute_query("""
            SELECT p.key, p.name, p.description, p.base_url, p.documentation_url, p.active as is_active
            FROM provider p
            ORDER BY p.active DESC, p.name
        """)
        
        # Enhance each provider with stats and datasets
        providers = []
        for provider in providers_data:
            # Get provider stats
            stats = execute_query("""
                SELECT COUNT(*) as total_records,
                       COUNT(DISTINCT tl.id) as total_requests,
                       SUM(tl.actual_cost_cents) as total_cost_cents
                FROM metric_data md
                LEFT JOIN task_log tl ON tl.task_id IN (
                    SELECT id FROM task WHERE provider = ?
                )
                WHERE md.provider_key = ?
            """, (provider['key'], provider['key']))
            
            provider_stats = stats[0] if stats else {
                'total_records': 0, 'total_requests': 0, 'total_cost_cents': 0
            }
            
            # Get datasets for this provider
            datasets = execute_query("""
                SELECT dataset as name, 
                       'Environmental data' as description,
                       COUNT(*) as record_count
                FROM metric_data 
                WHERE provider_key = ?
                GROUP BY dataset
            """, (provider['key'],))
            
            # Get data types (unique metric names)
            data_types = execute_query("""
                SELECT DISTINCT metric_name 
                FROM metric_data 
                WHERE provider_key = ?
                LIMIT 10
            """, (provider['key'],))
            
            provider.update({
                'stats': provider_stats,
                'datasets': datasets,
                'data_types': [dt['metric_name'] for dt in data_types],
                'website_url': provider.get('base_url'),
                'api_documentation_url': provider.get('documentation_url')
            })
            providers.append(provider)
        
        return render_template('providers.html', 
                             total_providers=total_providers,
                             active_providers=active_providers,
                             total_datasets=total_datasets,
                             total_api_cost=total_api_cost,
                             providers=providers)
    except Exception as e:
        return f"Providers Error: {e}", 500

@app.route('/operational')
def operational_page():
    """Operational costs and Railway hosting monitoring page"""
    try:
        # Get Railway configuration from environment
        railway_token = os.getenv('RAILWAY_API_TOKEN')
        railway_project_id = os.getenv('RAILWAY_PROJECT_ID')
        
        operational_data = {
            'has_railway_config': bool(railway_token and railway_project_id),
            'project_id': railway_project_id,
            'current_usage': 0.0,
            'budget_limit': 10.0,
            'resource_breakdown': {
                'cpu': {'usage': '0 vCPU hours', 'cost': 0.0, 'percentage': 0},
                'memory': {'usage': '0 GB hours', 'cost': 0.0, 'percentage': 0},
                'network': {'usage': '0 GB', 'cost': 0.0, 'percentage': 0},
                'storage': {'usage': '0 GB', 'cost': 0.0, 'percentage': 0}
            }
        }
        
        # If Railway credentials are configured, fetch real data
        if railway_token and railway_project_id:
            try:
                railway_data = fetch_railway_usage(railway_token, railway_project_id)
                if railway_data:
                    operational_data.update(railway_data)
            except Exception as api_error:
                print(f"Railway API Error: {api_error}")
                operational_data['api_error'] = str(api_error)
        
        return render_template('operational.html', operational_data=operational_data)
    except Exception as e:
        return f"Operational Error: {e}", 500

def fetch_railway_usage(token, project_id):
    """Fetch real usage data from Railway's GraphQL API"""
    try:
        # Railway GraphQL endpoint
        url = 'https://backboard.railway.com/graphql/v2'
        
        # Calculate date range (current billing cycle - last 30 days)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        # GraphQL query for actual usage data
        query = """
        query ProjectUsage($projectId: String!) {
            project(id: $projectId) {
                name
                usage {
                    currentPeriod {
                        estimatedCost
                        measurements {
                            cpuUsage
                            memoryUsageGb
                            networkEgressGb
                            diskUsageGb
                        }
                    }
                }
            }
        }
        """
        
        variables = {
            'projectId': project_id
        }
        
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        response = requests.post(
            url,
            json={'query': query, 'variables': variables},
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            
            if 'errors' in data:
                raise Exception(f"GraphQL Error: {data['errors']}")
            
            # Debug: Print the response to understand the structure
            print(f"Railway API Response: {data}")
            
            # Parse usage data from new query structure
            project_data = data.get('data', {}).get('project', {})
            usage_data = project_data.get('usage', {}).get('currentPeriod', {})
            measurements = usage_data.get('measurements', {})
            estimated_cost = usage_data.get('estimatedCost', 0)
            
            # Calculate costs based on Railway's 2025 pricing
            # CPU: $20/vCPU/month, Memory: $10/GB/month, Network: $0.05/GB
            resource_costs = {
                'cpu': {'cost': 0.0, 'usage': '0 vCPU hours', 'raw_value': 0},
                'memory': {'cost': 0.0, 'usage': '0 GB hours', 'raw_value': 0},
                'network': {'cost': 0.0, 'usage': '0 GB', 'raw_value': 0},
                'storage': {'cost': 0.0, 'usage': '0 GB', 'raw_value': 0}
            }
            
            # Parse measurements from new structure
            if measurements:
                # CPU Usage
                if 'cpuUsage' in measurements and measurements['cpuUsage']:
                    cpu_value = float(measurements['cpuUsage'])
                    cpu_hours = cpu_value / 60.0  # Convert minutes to hours
                    cost = cpu_hours * (20.0 / (30 * 24))  # $20/vCPU/month
                    resource_costs['cpu'] = {
                        'cost': cost,
                        'usage': f'{cpu_hours:.1f} vCPU hours',
                        'raw_value': cpu_value
                    }
                
                # Memory Usage
                if 'memoryUsageGb' in measurements and measurements['memoryUsageGb']:
                    memory_value = float(measurements['memoryUsageGb'])
                    cost = memory_value * (10.0 / (30 * 24))  # $10/GB/month
                    resource_costs['memory'] = {
                        'cost': cost,
                        'usage': f'{memory_value:.1f} GB hours',
                        'raw_value': memory_value
                    }
                
                # Network Usage
                if 'networkEgressGb' in measurements and measurements['networkEgressGb']:
                    network_value = float(measurements['networkEgressGb'])
                    cost = network_value * 0.05  # $0.05/GB
                    resource_costs['network'] = {
                        'cost': cost,
                        'usage': f'{network_value:.2f} GB',
                        'raw_value': network_value
                    }
                
                # Storage Usage
                if 'diskUsageGb' in measurements and measurements['diskUsageGb']:
                    storage_value = float(measurements['diskUsageGb'])
                    cost = storage_value * 0.15  # $0.15/GB/month
                    resource_costs['storage'] = {
                        'cost': cost,
                        'usage': f'{storage_value:.2f} GB',
                        'raw_value': storage_value
                    }
            
            # Calculate total cost and percentages
            total_cost = sum(r['cost'] for r in resource_costs.values())
            
            for resource in resource_costs.values():
                if total_cost > 0:
                    resource['percentage'] = int((resource['cost'] / total_cost) * 100)
                else:
                    resource['percentage'] = 0
            
            return {
                'current_usage': round(total_cost, 2),
                'resource_breakdown': resource_costs,
                'last_updated': datetime.now().isoformat()
            }
        
        else:
            raise Exception(f"HTTP {response.status_code}: {response.text}")
            
    except requests.exceptions.RequestException as e:
        raise Exception(f"Network error: {e}")
    except Exception as e:
        raise Exception(f"Railway API error: {e}")

@app.route('/api/railway/refresh', methods=['POST'])
def api_refresh_railway_costs():
    """API endpoint to refresh Railway costs"""
    try:
        railway_token = os.getenv('RAILWAY_API_TOKEN')
        railway_project_id = os.getenv('RAILWAY_PROJECT_ID')
        
        if not railway_token or not railway_project_id:
            return jsonify({'error': 'Railway credentials not configured'}), 400
        
        railway_data = fetch_railway_usage(railway_token, railway_project_id)
        return jsonify({'success': True, 'data': railway_data})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return "Page not found", 404

@app.errorhandler(500)
def internal_error(error):
    return f"Internal error: {error}", 500

if __name__ == '__main__':
    # Development server
    print("🌐 Starting Terrascan Web Interface...")
    print("📊 Dashboard: http://localhost:5000")
    print("🔧 Tasks: http://localhost:5000/tasks")
    print("📈 Data: http://localhost:5000/data")
    print("📊 Metrics: http://localhost:5000/metrics")
    print("🌐 Providers: http://localhost:5000/providers")
    print("🗂️ Schema: http://localhost:5000/schema")
    print("💰 Operational: http://localhost:5000/operational")
    print("🖥️ System: http://localhost:5000/system")
    
    app.run(debug=True, host='0.0.0.0', port=5000) 
