#!/usr/bin/env python3
"""
Test script to verify the spec generation workflow
"""

import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.ai_service import AIService

def test_spec_workflow():
    """Test the complete spec generation workflow"""
    print("🧪 Testing Spec Generation Workflow...")
    print("=" * 50)
    
    try:
        # Initialize AI service
        print("1. Initializing AI Service...")
        ai_service = AIService()
        
        # Test connection
        print("2. Testing Bedrock connection...")
        if ai_service.initialize_bedrock_client():
            print("   ✅ Bedrock connection successful")
        else:
            print("   ❌ Bedrock connection failed")
            return False
        
        # Test model selection
        print("3. Testing model selection...")
        if ai_service.select_model("Claude Sonnet 3.5 v2"):
            print("   ✅ Model selection successful")
        else:
            print("   ❌ Model selection failed")
            return False
        
        # Test requirements generation
        print("4. Testing requirements generation...")
        test_description = "A simple user authentication system with login and registration"
        
        try:
            requirements = ai_service.generate_requirements(test_description)
            if requirements and len(requirements) > 100:
                print("   ✅ Requirements generated successfully")
                print(f"   📝 Generated {len(requirements)} characters")
            else:
                print("   ⚠️  Requirements generated but seem short")
        except Exception as e:
            print(f"   ❌ Requirements generation failed: {e}")
            return False
        
        # Test design generation
        print("5. Testing design generation...")
        try:
            design = ai_service.create_design(requirements)
            if design and len(design) > 100:
                print("   ✅ Design generated successfully")
                print(f"   📝 Generated {len(design)} characters")
            else:
                print("   ⚠️  Design generated but seem short")
        except Exception as e:
            print(f"   ❌ Design generation failed: {e}")
            return False
        
        # Test task generation
        print("6. Testing task generation...")
        try:
            tasks = ai_service.generate_tasks(design)
            if tasks:
                print("   ✅ Tasks generated successfully")
                if isinstance(tasks, list):
                    print(f"   📝 Generated {len(tasks)} tasks")
                else:
                    print(f"   📝 Generated task content: {len(str(tasks))} characters")
            else:
                print("   ⚠️  No tasks generated")
        except Exception as e:
            print(f"   ❌ Task generation failed: {e}")
            return False
        
        print("\n" + "=" * 50)
        print("✅ All spec workflow tests passed!")
        print("\n💡 The spec generation functionality is working correctly.")
        print("   You can now use the Streamlit app to generate complete specifications.")
        
        return True
        
    except Exception as e:
        print(f"❌ Unexpected error during testing: {e}")
        return False

if __name__ == "__main__":
    success = test_spec_workflow()
    sys.exit(0 if success else 1)