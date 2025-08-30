#!/usr/bin/env python3
"""
Test script to verify model synchronization fix
"""

import streamlit as st
import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.ai_service import AIService

def simulate_streamlit_session():
    """Simulate Streamlit session state behavior"""
    
    print("🧪 Testing Model Synchronization Fix...")
    
    # Simulate session state
    session_state = {
        'selected_model': None,
        'model_connected': False,
        'ai_service': AIService()
    }
    
    print(f"✅ Initial state:")
    print(f"   - session_state['selected_model']: {session_state['selected_model']}")
    print(f"   - session_state['model_connected']: {session_state['model_connected']}")
    print(f"   - ai_service.current_model: {session_state['ai_service'].current_model}")
    
    # Simulate model selection
    selected_model = "Claude Sonnet 3.5 v2"
    print(f"\n🔄 Simulating model selection: {selected_model}")
    
    # This is what happens in the app when model is selected
    if session_state['ai_service'].select_model(selected_model):
        session_state['selected_model'] = selected_model
        session_state['model_connected'] = True
        print(f"   ✅ Model selection successful")
    else:
        session_state['model_connected'] = False
        print(f"   ❌ Model selection failed")
    
    print(f"\n📊 State after selection:")
    print(f"   - session_state['selected_model']: {session_state['selected_model']}")
    print(f"   - session_state['model_connected']: {session_state['model_connected']}")
    print(f"   - ai_service.current_model: {session_state['ai_service'].current_model}")
    
    # Simulate what happens during generate action validation
    print(f"\n🚀 Simulating generate action validation...")
    
    # Check session state
    model_connected = session_state.get('model_connected', False)
    selected_model_state = session_state.get('selected_model')
    ai_current_model = session_state['ai_service'].current_model
    
    print(f"   - model_connected: {model_connected}")
    print(f"   - selected_model: {selected_model_state}")
    print(f"   - ai_service.current_model: {ai_current_model}")
    
    # Validation logic
    if not model_connected or not selected_model_state:
        print(f"   ❌ Validation failed: No model selected")
        return False
    
    if not ai_current_model or ai_current_model != selected_model_state:
        print(f"   ⚠️  AI service model mismatch, synchronizing...")
        session_state['ai_service'].select_model(selected_model_state)
        print(f"   ✅ AI service synchronized")
    
    print(f"   ✅ Validation passed - ready to generate")
    
    # Test actual generation
    try:
        print(f"\n📝 Testing text generation...")
        response = session_state['ai_service'].generate_text("Hello, this is a test.")
        print(f"   ✅ Generation successful: {len(response)} characters")
        return True
    except Exception as e:
        print(f"   ❌ Generation failed: {str(e)}")
        return False

if __name__ == "__main__":
    simulate_streamlit_session()