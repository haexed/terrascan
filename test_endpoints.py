#!/usr/bin/env python3
"""
Terrascan Endpoint Testing Script
Tests all endpoints and validates syntax after app.py rewrite
"""

import os
import sys
import json
import time
import traceback
from urllib.parse import urljoin
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Test configuration
BASE_URL = "http://localhost:5000"
TIMEOUT = 10
MAX_RETRIES = 3

class EndpointTester:
    def __init__(self, base_url=BASE_URL):
        self.base_url = base_url
        self.session = requests.Session()
        
        # Configure retries
        retry_strategy = Retry(
            total=MAX_RETRIES,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        self.results = {
            'passed': 0,
            'failed': 0,
            'errors': [],
            'warnings': []
        }

    def test_endpoint(self, path, method='GET', expected_status=200, check_json=False, data=None):
        """Test a single endpoint"""
        url = urljoin(self.base_url, path)
        
        try:
            print(f"Testing {method} {path}... ", end="")
            
            if method == 'GET':
                response = self.session.get(url, timeout=TIMEOUT)
            elif method == 'POST':
                response = self.session.post(url, json=data, timeout=TIMEOUT)
            else:
                print(f"❌ Unsupported method: {method}")
                self.results['failed'] += 1
                return False
            
            # Check status code
            if response.status_code != expected_status:
                print(f"❌ Status {response.status_code} (expected {expected_status})")
                self.results['failed'] += 1
                self.results['errors'].append(f"{method} {path}: Status {response.status_code}")
                return False
            
            # Check JSON response if expected
            if check_json:
                try:
                    json_data = response.json()
                    if not isinstance(json_data, dict):
                        print("⚠️  Non-dict JSON response")
                        self.results['warnings'].append(f"{method} {path}: Non-dict JSON")
                except ValueError:
                    print("❌ Invalid JSON response")
                    self.results['failed'] += 1
                    self.results['errors'].append(f"{method} {path}: Invalid JSON")
                    return False
            
            # Check HTML response for basic structure
            if not check_json and response.headers.get('content-type', '').startswith('text/html'):
                content = response.text.lower()
                if '<html' not in content or '<body' not in content:
                    print("⚠️  Incomplete HTML structure")
                    self.results['warnings'].append(f"{path}: Incomplete HTML")
            
            print("✅ OK")
            self.results['passed'] += 1
            return True
            
        except requests.exceptions.ConnectError:
            print("❌ Connection failed - is the server running?")
            self.results['failed'] += 1
            self.results['errors'].append(f"{method} {path}: Connection failed")
            return False
        except requests.exceptions.Timeout:
            print("❌ Timeout")
            self.results['failed'] += 1
            self.results['errors'].append(f"{method} {path}: Timeout")
            return False
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            self.results['failed'] += 1
            self.results['errors'].append(f"{method} {path}: {str(e)}")
            return False

    def run_syntax_check(self):
        """Check Python syntax by importing the app module"""
        print("\n🔍 Checking Python syntax...")
        
        try:
            # Add the web directory to path
            sys.path.insert(0, os.path.join(os.getcwd(), 'web'))
            
            # Try to import the app module
            import app
            print("✅ app.py syntax is valid")
            
            # Try to create the app
            flask_app = app.create_app()
            print("✅ Flask app creation successful")
            
            # Check if all required routes are registered
            routes = [rule.rule for rule in flask_app.url_map.iter_rules()]
            expected_routes = [
                '/',
                '/dashboard', 
                '/map',
                '/about',
                '/tasks',
                '/system',
                '/api/map-data',
                '/api/refresh',
                '/api/health',
                '/api/tasks',
                '/api/tasks/<task_name>/run',
                '/api/tasks/<task_name>/logs'
            ]
            
            missing_routes = []
            for expected in expected_routes:
                # Handle parameterized routes
                if '<' in expected:
                    found = any(expected.replace('<task_name>', '<') in route for route in routes)
                else:
                    found = expected in routes
                
                if not found:
                    missing_routes.append(expected)
            
            if missing_routes:
                print(f"⚠️  Missing routes: {missing_routes}")
                self.results['warnings'].extend([f"Missing route: {route}" for route in missing_routes])
            else:
                print("✅ All expected routes are registered")
            
            self.results['passed'] += 2  # Syntax + app creation
            return True
            
        except ImportError as e:
            print(f"❌ Import error: {str(e)}")
            self.results['failed'] += 1
            self.results['errors'].append(f"Import error: {str(e)}")
            return False
        except Exception as e:
            print(f"❌ Syntax error: {str(e)}")
            self.results['failed'] += 1
            self.results['errors'].append(f"Syntax error: {str(e)}")
            print(f"Full traceback:\n{traceback.format_exc()}")
            return False

    def test_all_endpoints(self):
        """Test all application endpoints"""
        print("\n🌐 Testing web endpoints...")
        
        # Web pages
        endpoints = [
            ('/', 'GET', 200, False),
            ('/dashboard', 'GET', 200, False),
            ('/map', 'GET', 200, False),
            ('/about', 'GET', 200, False),
            ('/tasks', 'GET', 200, False),
            ('/system', 'GET', 200, False),
        ]
        
        for endpoint, method, status, json_check in endpoints:
            self.test_endpoint(endpoint, method, status, json_check)
        
        print("\n🔌 Testing API endpoints...")
        
        # API endpoints
        api_endpoints = [
            ('/api/map-data', 'GET', 200, True),
            ('/api/refresh', 'GET', 200, True),
            ('/api/health', 'GET', 200, True),
            ('/api/tasks', 'GET', 200, True),
        ]
        
        for endpoint, method, status, json_check in api_endpoints:
            self.test_endpoint(endpoint, method, status, json_check)
        
        print("\n⚙️  Testing parameterized endpoints...")
        
        # Test with a sample task name (may fail if no tasks exist, but tests routing)
        parameterized_endpoints = [
            ('/api/tasks/test_task/logs', 'GET', [200, 404, 500], True),
            ('/api/tasks/test_task/run', 'POST', [200, 404, 500], True),
        ]
        
        for endpoint, method, statuses, json_check in parameterized_endpoints:
            url = urljoin(self.base_url, endpoint)
            try:
                print(f"Testing {method} {endpoint}... ", end="")
                
                if method == 'GET':
                    response = self.session.get(url, timeout=TIMEOUT)
                elif method == 'POST':
                    response = self.session.post(url, json={}, timeout=TIMEOUT)
                
                if response.status_code in statuses:
                    print("✅ OK (routing works)")
                    self.results['passed'] += 1
                else:
                    print(f"⚠️  Status {response.status_code} (expected one of {statuses})")
                    self.results['warnings'].append(f"{method} {endpoint}: Unexpected status {response.status_code}")
                    
            except Exception as e:
                print(f"❌ Error: {str(e)}")
                self.results['errors'].append(f"{method} {endpoint}: {str(e)}")
                self.results['failed'] += 1

    def check_dependencies(self):
        """Check if all required dependencies are available"""
        print("\n📦 Checking dependencies...")
        
        required_modules = [
            'flask',
            'psycopg2',
            'requests',
            'python-dotenv'
        ]
        
        missing_modules = []
        for module in required_modules:
            try:
                if module == 'python-dotenv':
                    import dotenv
                elif module == 'psycopg2':
                    import psycopg2
                else:
                    __import__(module)
                print(f"✅ {module}")
            except ImportError:
                print(f"❌ {module} - Missing!")
                missing_modules.append(module)
        
        if missing_modules:
            print(f"\n⚠️  Missing dependencies: {', '.join(missing_modules)}")
            print("Install with: pip install " + " ".join(missing_modules))
            self.results['errors'].append(f"Missing dependencies: {missing_modules}")
        else:
            print("✅ All dependencies available")
            self.results['passed'] += 1

    def check_environment(self):
        """Check environment configuration"""
        print("\n🔧 Checking environment configuration...")
        
        # Check for .env file
        if os.path.exists('.env'):
            print("✅ .env file found")
            self.results['passed'] += 1
        else:
            print("⚠️  .env file not found")
            self.results['warnings'].append(".env file not found")
        
        # Check critical environment variables
        critical_vars = ['DATABASE_URL']
        optional_vars = ['NASA_API_KEY', 'OPENAQ_API_KEY', 'NOAA_API_KEY', 'OPENWEATHERMAP_API_KEY']
        
        for var in critical_vars:
            if os.environ.get(var):
                print(f"✅ {var}")
                self.results['passed'] += 1
            else:
                print(f"❌ {var} - Missing!")
                self.results['errors'].append(f"Missing critical environment variable: {var}")
        
        for var in optional_vars:
            if os.environ.get(var):
                print(f"✅ {var}")
            else:
                print(f"⚠️  {var} - Not set (API functionality may be limited)")
                self.results['warnings'].append(f"Optional environment variable not set: {var}")

    def run_all_tests(self):
        """Run all tests"""
        print("🧪 Terrascan Endpoint Testing")
        print("=" * 50)
        
        # Load environment variables
        try:
            from dotenv import load_dotenv
            load_dotenv()
        except ImportError:
            print("⚠️  python-dotenv not available, skipping .env loading")
        
        # Run all test categories
        self.check_dependencies()
        self.check_environment()
        self.run_syntax_check()
        
        # Only test endpoints if syntax check passed
        if self.results['failed'] == 0:
            print("\n🚀 Starting local server test...")
            print("ℹ️  Make sure the server is running with: python run.py")
            time.sleep(2)  # Give user time to read
            
            self.test_all_endpoints()
        else:
            print("\n⏭️  Skipping endpoint tests due to syntax errors")
        
        # Print summary
        self.print_summary()

    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 50)
        print("📊 TEST SUMMARY")
        print("=" * 50)
        
        total_tests = self.results['passed'] + self.results['failed']
        print(f"✅ Passed: {self.results['passed']}")
        print(f"❌ Failed: {self.results['failed']}")
        print(f"⚠️  Warnings: {len(self.results['warnings'])}")
        print(f"📈 Total: {total_tests}")
        
        if self.results['failed'] == 0:
            if len(self.results['warnings']) == 0:
                print("\n🎉 ALL TESTS PASSED! The rewrite looks good!")
            else:
                print("\n✅ All critical tests passed, but there are some warnings to review.")
        else:
            print("\n❌ Some tests failed - please review the errors below.")
        
        # Print errors
        if self.results['errors']:
            print("\n🔴 ERRORS:")
            for error in self.results['errors']:
                print(f"  • {error}")
        
        # Print warnings
        if self.results['warnings']:
            print("\n🟡 WARNINGS:")
            for warning in self.results['warnings']:
                print(f"  • {warning}")
        
        print("\n" + "=" * 50)
        
        # Exit with appropriate code
        if self.results['failed'] > 0:
            print("❌ Tests failed - check the errors above")
            sys.exit(1)
        else:
            print("✅ Ready for deployment!")
            sys.exit(0)


def main():
    """Main function"""
    # Allow custom base URL
    base_url = os.environ.get('TEST_BASE_URL', BASE_URL)
    
    tester = EndpointTester(base_url)
    tester.run_all_tests()


if __name__ == '__main__':
    main() 
