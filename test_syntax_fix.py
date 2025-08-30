#!/usr/bin/env python3
"""
Test script to verify the syntax fix
"""

def test_app_import():
    """Test that app.py can be imported without syntax errors"""
    print("🧪 Testing app.py syntax...")
    
    try:
        # This will fail if there are syntax errors
        import ast
        
        with open('app.py', 'r') as f:
            source = f.read()
        
        # Parse the source code
        ast.parse(source)
        print("✅ app.py syntax is valid")
        return True
        
    except SyntaxError as e:
        print(f"❌ Syntax error found: {e}")
        print(f"   Line {e.lineno}: {e.text}")
        return False
    except Exception as e:
        print(f"❌ Error parsing app.py: {e}")
        return False

def test_function_definitions():
    """Test that key functions are properly defined"""
    print("🧪 Testing function definitions...")
    
    try:
        with open('app.py', 'r') as f:
            content = f.read()
        
        expected_functions = [
            "def main(",
            "def initialize_session_state(",
            "def render_navigation_panel(",
            "def render_content_panel(",
            "def render_actions_panel(",
            "def generate_jira_templates(",
            "def parse_tasks_from_markdown("
        ]
        
        for func in expected_functions:
            if func in content:
                print(f"✅ Found: {func}")
            else:
                print(f"❌ Missing: {func}")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error checking functions: {e}")
        return False

def test_main_call():
    """Test that main() is called at the end"""
    print("🧪 Testing main() call...")
    
    try:
        with open('app.py', 'r') as f:
            content = f.read()
        
        if 'if __name__ == "__main__":\n    main()' in content:
            print("✅ main() call found")
            return True
        else:
            print("❌ main() call missing")
            return False
            
    except Exception as e:
        print(f"❌ Error checking main call: {e}")
        return False

if __name__ == "__main__":
    success1 = test_app_import()
    success2 = test_function_definitions()
    success3 = test_main_call()
    
    if all([success1, success2, success3]):
        print("\n🎉 All syntax tests passed!")
        print("\n✅ Fixed Issues:")
        print("  - Broken function definition repaired")
        print("  - main() call restored")
        print("  - All functions properly defined")
        print("  - Syntax is valid")
        
        print("\n🚀 App is ready to run!")
    else:
        print("\n❌ Some tests failed. Check the issues above.")
    
    exit(0 if all([success1, success2, success3]) else 1)