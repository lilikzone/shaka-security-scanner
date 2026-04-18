#!/usr/bin/env python3
"""
Test AWS Bedrock AI Integration
Tests different Claude models with inference profiles
"""

import json
import boto3
from datetime import datetime

def test_bedrock_model(model_id: str, model_name: str):
    """Test a specific Bedrock model"""
    print(f"\n{'='*70}")
    print(f"Testing: {model_name}")
    print(f"Model ID: {model_id}")
    print(f"{'='*70}")
    
    try:
        # Create Bedrock Runtime client
        session = boto3.Session(profile_name='sandbox', region_name='us-east-1')
        bedrock = session.client('bedrock-runtime')
        
        # Prepare request
        request_body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 200,
            "messages": [
                {
                    "role": "user",
                    "content": "You are testing AWS Bedrock integration. Respond with: 'AI is working! Model: [your model name]'"
                }
            ]
        }
        
        # Invoke model
        print(f"⏳ Invoking model...")
        start_time = datetime.now()
        
        response = bedrock.invoke_model(
            modelId=model_id,
            body=json.dumps(request_body)
        )
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # Parse response
        response_body = json.loads(response['body'].read())
        
        # Extract text from response
        if 'content' in response_body and len(response_body['content']) > 0:
            text = response_body['content'][0]['text']
            print(f"✅ SUCCESS!")
            print(f"⏱️  Duration: {duration:.2f}s")
            print(f"📝 Response: {text}")
            print(f"🔢 Input tokens: {response_body.get('usage', {}).get('input_tokens', 'N/A')}")
            print(f"🔢 Output tokens: {response_body.get('usage', {}).get('output_tokens', 'N/A')}")
            return True
        else:
            print(f"❌ FAILED: Unexpected response format")
            print(f"Response: {json.dumps(response_body, indent=2)}")
            return False
            
    except Exception as e:
        print(f"❌ FAILED: {str(e)}")
        return False

def main():
    """Test multiple Claude models"""
    print("🧪 AWS Bedrock AI Integration Test")
    print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌍 Region: us-east-1")
    print(f"👤 Profile: sandbox")
    
    # Models to test (using inference profiles)
    models = [
        ("us.anthropic.claude-3-5-haiku-20241022-v1:0", "Claude 3.5 Haiku (US)"),
        ("us.anthropic.claude-sonnet-4-5-20250929-v1:0", "Claude Sonnet 4.5 (US)"),
        ("us.anthropic.claude-haiku-4-5-20251001-v1:0", "Claude Haiku 4.5 (US)"),
    ]
    
    results = {}
    
    for model_id, model_name in models:
        success = test_bedrock_model(model_id, model_name)
        results[model_name] = success
    
    # Summary
    print(f"\n{'='*70}")
    print("📊 TEST SUMMARY")
    print(f"{'='*70}")
    
    for model_name, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {model_name}")
    
    total = len(results)
    passed = sum(1 for s in results.values() if s)
    
    print(f"\n📈 Results: {passed}/{total} models working")
    
    if passed > 0:
        print("\n✅ AI Integration is WORKING!")
        print("💡 Recommendation: Use one of the working models in .env.backend")
    else:
        print("\n❌ AI Integration is NOT working")
        print("💡 Check AWS Bedrock model access and permissions")

if __name__ == "__main__":
    main()
