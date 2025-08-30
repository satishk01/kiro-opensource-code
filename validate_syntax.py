#!/usr/bin/env python3
"""
Quick syntax validation for app.py
"""

import ast

def validate_syntax():
    """Validate app.py syntax"""
    try:
        with open('app.py', 'r') as f:
            source = f.read()
        
        # Parse the source code
        ast.parse(source)
        print("✅ app.py syntax is valid!")
        return True
        
    except SyntaxError as e:
        print(f"❌ Syntax error: {e}")
        print(f"   Line {e.lineno}: {e.text}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = validate_syntax()
    if success:
        print("🚀 App is ready to run!")
    exit(0 if success else 1)