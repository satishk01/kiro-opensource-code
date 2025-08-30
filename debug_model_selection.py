#!/usr/bin/env python3
"""
Debug script to test model selection issue
"""

import streamlit as st
import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.ai_service import AIService

def test_model_selection():
    """Test model selection functionality"""
    print("🔍 Testing Model Selection...")
    
    # Initialize AI service
    ai_service = AIService()
    print(f"✅ AI Service initialized")
    print(f"   - Current model: {getattr(ai_service, 'current_model', 'None')}")
    print(f"   - Available models: {ai_service.get_available_models()}")
    
    # Test model selection
    test_model = "Claude Sonnet 3.5 v2"
    print(f"\n🧠 Testing model selection: {test_model}")
    
    result = ai_service.select_model(test_model)
    print(f"   - Selection result: {result}")
    print(f"   - Current model after selection: {getattr(ai_service, 'current_model', 'None')}")
    
    # Test generate_text method
    if result:
        print(f"\n📝 Testing text generation...")
        try:
            response = ai_service.generate_text("Hello, this is a test prompt.")
            print(f"   - Generation successful: {len(response)} characters")
        except Exception as e:
            print(f"   - Generation failed: {str(e)}")
    else:
        print(f"\n❌ Skipping text generation - model selection failed")

if __name__ == "__main__":
    test_model_selection()