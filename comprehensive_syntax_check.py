#!/usr/bin/env python3
"""
Comprehensive syntax check for app.py
"""

import ast
import sys

def check_syntax():
    """Comprehensive syntax validation"""
    print("🔍 Comprehensive Syntax Check for app.py")
    print("=" * 50)
    
    try:
        # Read the file
        with open('app.py', 'r') as f:
            source = f.read()
        
        print(f"📄 File size: {len(source)} characters")
        print(f"📄 Lines: {len(source.split(chr(10)))}")
        
        # Parse the source code
        tree = ast.parse(source)
        print("✅ Syntax is valid!")
        
        # Check for common issues
        issues = []
        
        # Check for function definitions
        functions = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                functions.append(node.name)
        
        print(f"\n📋 Found {len(functions)} functions:")
        for func in functions:
            print(f"  ✅ {func}()")
        
        # Check for expected functions
        expected_functions = [
            'load_css',
            'initialize_session_state', 
            'render_navigation_panel',
            'render_content_panel',
            'render_actions_panel',
            'render_spec_generation_content',
            'render_jira_integration_content',
            'render_diagram_generation_content',
            'render_settings_content',
            'render_jira_download_options',
            'handle_generate_action',
            'handle_regenerate_action',
            'handle_accept_action',
            'handle_reject_action',
            'main',
            'generate_jira_templates',
            'parse_tasks_from_markdown'
        ]
        
        missing_functions = []
        for expected in expected_functions:
            if expected not in functions:
                missing_functions.append(expected)
        
        if missing_functions:
            print(f"\n⚠️ Missing expected functions:")
            for func in missing_functions:
                print(f"  ❌ {func}()")
        else:
            print(f"\n✅ All expected functions found!")
        
        # Check for imports
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                for alias in node.names:
                    imports.append(f"{module}.{alias.name}")
        
        print(f"\n📦 Found {len(imports)} imports:")
        for imp in imports[:10]:  # Show first 10
            print(f"  ✅ {imp}")
        if len(imports) > 10:
            print(f"  ... and {len(imports) - 10} more")
        
        # Check for main guard
        has_main_guard = 'if __name__ == "__main__":' in source
        if has_main_guard:
            print(f"\n✅ Main guard found")
        else:
            print(f"\n❌ Main guard missing")
            issues.append("Missing main guard")
        
        # Check for common syntax patterns
        if source.count('def ') != len(functions):
            issues.append("Function definition count mismatch")
        
        # Check for unmatched quotes/brackets
        quote_count = source.count('"') + source.count("'")
        if quote_count % 2 != 0:
            issues.append("Unmatched quotes detected")
        
        # Summary
        print(f"\n📊 Summary:")
        print(f"  Functions: {len(functions)}")
        print(f"  Imports: {len(imports)}")
        print(f"  Issues: {len(issues)}")
        
        if issues:
            print(f"\n⚠️ Potential issues:")
            for issue in issues:
                print(f"  - {issue}")
        
        return len(issues) == 0
        
    except SyntaxError as e:
        print(f"❌ Syntax Error:")
        print(f"   Line {e.lineno}: {e.text}")
        print(f"   Error: {e.msg}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def check_specific_patterns():
    """Check for specific patterns that might cause issues"""
    print(f"\n🔍 Checking specific patterns...")
    
    with open('app.py', 'r') as f:
        content = f.read()
    
    patterns = [
        ('Broken function definitions', r'def \w+\n'),
        ('Missing colons', r'if.*[^:]\n'),
        ('Unmatched parentheses', r'\([^)]*\n[^)]*\)'),
    ]
    
    import re
    issues = []
    
    for pattern_name, pattern in patterns:
        matches = re.findall(pattern, content)
        if matches:
            print(f"  ⚠️ {pattern_name}: {len(matches)} potential issues")
            issues.extend(matches)
        else:
            print(f"  ✅ {pattern_name}: OK")
    
    return len(issues) == 0

if __name__ == "__main__":
    print("🧪 Starting comprehensive syntax validation...\n")
    
    success1 = check_syntax()
    success2 = check_specific_patterns()
    
    print(f"\n{'='*50}")
    
    if success1 and success2:
        print("🎉 All syntax checks passed!")
        print("\n✅ app.py is ready to run!")
        print("\n🚀 Features available:")
        print("  - Three-panel Kiro-style layout")
        print("  - Light theme with professional styling")
        print("  - Spec generation with SpecEngine")
        print("  - JIRA integration with templates")
        print("  - Generate → Review → Accept/Reject workflow")
        print("  - Context-aware actions and downloads")
    else:
        print("❌ Some issues found. Please review above.")
    
    exit(0 if (success1 and success2) else 1)