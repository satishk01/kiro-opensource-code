#!/usr/bin/env python3
"""
Test script for Nova Pro model integration
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.ai_service import AIService
import json

def test_nova_model():
    """Test Nova Pro model with correct payload format"""
    print("🧪 Testing Nova Pro model...")
    
    # Initialize AI service
    ai_service = AIService()
    
    # Initialize Bedrock client
    if not ai_service.initialize_bedrock_client():
        print("❌ Failed to initialize Bedrock client")
        return False
    
    # Select Nova Pro model
    if not ai_service.select_model("Amazon Nova Pro"):
        print("❌ Failed to select Nova Pro model")
        return False
    
    try:
        # Test the payload format directly
        print("\n🔍 Testing Nova Pro payload format...")
        config = ai_service.model_configs["Amazon Nova Pro"]
        payload = ai_service._prepare_nova_payload("Hello, can you tell me about yourself?")
        print(f"✅ Payload format: {json.dumps(payload, indent=2)}")
        
        # Test simple text generation
        print("\n📝 Testing simple text generation...")
        response = ai_service.generate_text("Hello, can you tell me about yourself?")
        print(f"✅ Response: {response[:200]}...")
        
        # Test requirements generation
        print("\n📋 Testing requirements generation...")
        requirements = ai_service.generate_requirements(
            "A simple todo list application where users can add, edit, and delete tasks"
        )
        print(f"✅ Requirements generated: {len(requirements)} characters")
        print(f"Preview: {requirements[:300]}...")
        
        print("\n🎉 All Nova Pro tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Nova Pro test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_nova_model()
    sys.exit(0 if success else 1)