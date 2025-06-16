#!/usr/bin/env python3
"""
TERRASCAN Syntax Checker
Quick syntax validation for the rewritten app.py
"""

import os
import sys
import traceback
from pathlib import Path

class SyntaxChecker:
    def __init__(self):
        self.results = {
            'passed': 0,
            'failed': 0,
            'errors': [],
            'warnings': []
        }

    def check_file_syntax(self, file_path):
        """Check Python syntax of a file"""
        try:
            with open(file_path, 'r') as f:
                source = f.read()
            
            # Compile to check syntax
            compile(source, file_path, 'exec')
            print(f"✅ {file_path} - Syntax OK")
            self.results['passed'] += 1
            return True
            
        except SyntaxError as e:
            print(f"❌ {file_path} - Syntax Error: {e}")
            self.results['failed'] += 1
            self.results['errors'].append(f"{file_path}: {e}")
            return False
        except Exception as e:
            print(f"❌ {file_path} - Error: {e}")
            self.results['failed'] += 1
            self.results['errors'].append(f"{file_path}: {e}")
            return False

    def check_imports(self, file_path):
        """Check if imports can be resolved"""
        print(f"\n🔍 Checking imports in {file_path}...")
        
        try:
            # Add directories to path
            sys.path.insert(0, str(Path(file_path).parent))
            sys.path.insert(0, os.getcwd())
            
            # Load environment first
            from dotenv import load_dotenv
            load_dotenv()
            print("✅ Environment loaded")
            
            # Try importing the main modules
            import web.app as app
            print("✅ app.py imported successfully")
            
            # Try creating the Flask app
            flask_app = app.create_app()
            print("✅ Flask app created successfully")
            
            # Check routes
            routes = [rule.rule for rule in flask_app.url_map.iter_rules()]
            print(f"✅ Found {len(routes)} routes registered")
            
            # Print some sample routes
            web_routes = [r for r in routes if not r.startswith('/api/') and not r.startswith('/static')]
            api_routes = [r for r in routes if r.startswith('/api/')]
            
            print(f"   📄 Web routes: {len(web_routes)}")
            for route in web_routes[:5]:  # Show first 5
                print(f"      • {route}")
            
            print(f"   🔌 API routes: {len(api_routes)}")
            for route in api_routes[:5]:  # Show first 5
                print(f"      • {route}")
            
            self.results['passed'] += 3
            return True
            
        except ImportError as e:
            print(f"❌ Import error: {e}")
            self.results['failed'] += 1
            self.results['errors'].append(f"Import error: {e}")
            return False
        except Exception as e:
            print(f"❌ Error: {e}")
            self.results['failed'] += 1
            self.results['errors'].append(f"Error: {e}")
            print(f"Full traceback:\n{traceback.format_exc()}")
            return False

    def check_environment(self):
        """Check environment configuration"""
        print("\n🔧 Checking environment...")
        
        # Check for .env file
        if os.path.exists('.env'):
            print("✅ .env file found")
            self.results['passed'] += 1
        else:
            print("❌ .env file not found")
            self.results['failed'] += 1
            self.results['errors'].append(".env file not found")
            return False
        
        # Load environment
        try:
            from dotenv import load_dotenv
            load_dotenv()
            print("✅ Environment variables loaded")
        except ImportError:
            print("⚠️  python-dotenv not available")
            self.results['warnings'].append("python-dotenv not available")
        
        # Check critical variables
        database_url = os.environ.get('DATABASE_URL')
        if database_url:
            print("✅ DATABASE_URL is set")
            # Don't print the full URL for security
            if 'postgresql://' in database_url:
                print("   🐘 PostgreSQL connection configured")
            self.results['passed'] += 1
        else:
            print("❌ DATABASE_URL not set")
            self.results['failed'] += 1
            self.results['errors'].append("DATABASE_URL not set")
        
        # Check optional API keys
        api_keys = ['NASA_API_KEY', 'OPENAQ_API_KEY', 'NOAA_API_KEY', 'OPENWEATHERMAP_API_KEY']
        for key in api_keys:
            if os.environ.get(key):
                print(f"✅ {key} is set")
            else:
                print(f"⚠️  {key} not set (limited functionality)")
                self.results['warnings'].append(f"{key} not set")
        
        return True

    def check_key_files(self):
        """Check that key files exist and have proper syntax"""
        print("\n📁 Checking key files...")
        
        files_to_check = [
            'web/app.py',
            'database/db.py', 
            'utils/__init__.py',
            'run.py'
        ]
        
        all_good = True
        for file_path in files_to_check:
            if os.path.exists(file_path):
                if not self.check_file_syntax(file_path):
                    all_good = False
            else:
                print(f"❌ {file_path} - File not found")
                self.results['failed'] += 1
                self.results['errors'].append(f"{file_path} not found")
                all_good = False
        
        return all_good

    def run_all_checks(self):
        """Run all syntax and structure checks"""
        print("🔍 TERRASCAN Syntax & Structure Check")
        print("=" * 50)
        
        # Check environment first
        env_ok = self.check_environment()
        
        # Check file syntax
        files_ok = self.check_key_files()
        
        # Try import check if environment and files are OK
        if env_ok and files_ok:
            self.check_imports('web/app.py')
        else:
            print("\n⏭️  Skipping import tests due to previous errors")
        
        # Print summary
        self.print_summary()

    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 50)
        print("📊 SYNTAX CHECK SUMMARY")
        print("=" * 50)
        
        total = self.results['passed'] + self.results['failed']
        print(f"✅ Passed: {self.results['passed']}")
        print(f"❌ Failed: {self.results['failed']}")
        print(f"⚠️  Warnings: {len(self.results['warnings'])}")
        print(f"📈 Total: {total}")
        
        if self.results['failed'] == 0:
            print("\n🎉 SYNTAX CHECK PASSED!")
            print("📋 The app.py rewrite looks syntactically correct")
            print("🚀 Ready to test with a running server")
        else:
            print("\n❌ SYNTAX ISSUES FOUND")
            print("🔧 Please fix the errors below before testing")
        
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
            print("   (Warnings won't prevent the app from running)")
        
        print("\n" + "=" * 50)
        
        # Return success status
        return self.results['failed'] == 0


def main():
    """Main function"""
    checker = SyntaxChecker()
    success = checker.run_all_checks()
    
    if success:
        print("✅ Ready for endpoint testing!")
        print("💡 Next: Run 'python3 run.py' to start the server")
        print("💡 Then: Test endpoints manually or with curl")
        sys.exit(0)
    else:
        print("❌ Fix syntax errors first")
        sys.exit(1)


if __name__ == '__main__':
    main() 
