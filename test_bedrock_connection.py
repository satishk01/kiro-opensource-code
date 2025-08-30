#!/usr/bin/env python3
"""
Simple test script to verify AWS Bedrock connectivity
Run this script to test if your AWS credentials and permissions are working correctly.
"""

import boto3
import json
from botocore.exceptions import ClientError, NoCredentialsError

def test_bedrock_connection():
    """Test AWS Bedrock connection and permissions"""
    print("🔍 Testing AWS Bedrock Connection...")
    print("=" * 50)
    
    try:
        # Test AWS credentials
        print("1. Testing AWS credentials...")
        session = boto3.Session()
        sts = session.client('sts')
        identity = sts.get_caller_identity()
        print(f"   ✅ AWS Identity: {identity.get('Arn', 'Unknown')}")
        
        # Test Bedrock control plane access
        print("\n2. Testing Bedrock control plane access...")
        bedrock_control = session.client('bedrock', region_name='us-east-1')
        
        try:
            models_response = bedrock_control.list_foundation_models()
            available_models = [model['modelId'] for model in models_response.get('modelSummaries', [])]
            print(f"   ✅ Found {len(available_models)} available models")
            
            # Check for our target models
            target_models = [
                'anthropic.claude-3-5-sonnet-20241022-v2:0',
                'amazon.nova-pro-v1:0'
            ]
            
            for model_id in target_models:
                if model_id in available_models:
                    print(f"   ✅ Target model available: {model_id}")
                else:
                    print(f"   ⚠️  Target model not found: {model_id}")
                    
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'AccessDeniedException':
                print("   ⚠️  Access denied to list models (this is OK if you have invoke permissions)")
            else:
                print(f"   ❌ Error listing models: {e}")
        
        # Test Bedrock runtime access
        print("\n3. Testing Bedrock runtime access...")
        bedrock_runtime = session.client('bedrock-runtime', region_name='us-east-1')
        
        # Try a simple test with Claude (if available)
        try:
            test_payload = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 10,
                "messages": [{"role": "user", "content": "Hello"}]
            }
            
            response = bedrock_runtime.invoke_model(
                modelId='anthropic.claude-3-5-sonnet-20241022-v2:0',
                body=json.dumps(test_payload),
                contentType='application/json'
            )
            
            response_body = json.loads(response['body'].read())
            print("   ✅ Successfully invoked Claude model")
            print(f"   📝 Test response: {response_body.get('content', [{}])[0].get('text', 'No text')[:50]}...")
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'AccessDeniedException':
                print("   ❌ Access denied to invoke Claude model")
                print("   💡 Check your IAM permissions for bedrock-runtime:InvokeModel")
            elif error_code == 'ValidationException':
                print("   ❌ Model validation error (model might not be available in your region)")
            else:
                print(f"   ❌ Error invoking model: {e}")
        
        print("\n" + "=" * 50)
        print("✅ Connection test completed!")
        print("\n💡 If you see errors above, check:")
        print("   - Your EC2 instance has an IAM role attached")
        print("   - The IAM role has the necessary Bedrock permissions")
        print("   - Bedrock is available in your region (us-east-1)")
        print("   - You have access to the specific models you want to use")
        
    except NoCredentialsError:
        print("❌ No AWS credentials found!")
        print("💡 Make sure your EC2 instance has an IAM role attached with Bedrock permissions")
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    test_bedrock_connection()