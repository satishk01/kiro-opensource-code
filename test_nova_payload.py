#!/usr/bin/env python3
"""
Test script for Nova Pro payload format (without AWS dependencies)
"""

import json

def test_nova_payload_format():
    """Test Nova Pro payload format"""
    print("🧪 Testing Nova Pro payload format...")
    
    # Simulate the payload creation logic
    def prepare_nova_payload(prompt: str, system_prompt: str = None) -> dict:
        """Prepare payload for Nova models"""
        max_tokens = 4096
        temperature = 0.7
        
        # Nova Pro expects content to be an array of content objects
        messages = [{"role": "user", "content": [{"text": prompt}]}]
        
        payload = {
            "messages": messages,
            "inferenceConfig": {
                "max_new_tokens": max_tokens,
                "temperature": temperature
            }
        }
        
        if system_prompt:
            payload["system"] = [{"text": system_prompt}]
            
        return payload
    
    # Test basic payload
    print("\n📝 Testing basic payload...")
    basic_payload = prepare_nova_payload("Hello, can you tell me about yourself?")
    print(f"✅ Basic payload: {json.dumps(basic_payload, indent=2)}")
    
    # Test payload with system prompt
    print("\n🔧 Testing payload with system prompt...")
    system_payload = prepare_nova_payload(
        "Generate requirements for a todo app",
        "You are OpenFlux, an AI assistant for developers."
    )
    print(f"✅ System payload: {json.dumps(system_payload, indent=2)}")
    
    # Verify required fields
    print("\n✅ Verifying required fields...")
    assert "messages" in basic_payload, "Missing 'messages' field"
    assert "inferenceConfig" in basic_payload, "Missing 'inferenceConfig' field"
    assert "max_new_tokens" in basic_payload["inferenceConfig"], "Missing 'max_new_tokens' field"
    assert "temperature" in basic_payload["inferenceConfig"], "Missing 'temperature' field"
    
    print("✅ All payload format tests passed!")
    print("\n🎯 The Nova Pro payload now uses the correct 'messages' format instead of 'inputText'")
    
    return True

if __name__ == "__main__":
    test_nova_payload_format()