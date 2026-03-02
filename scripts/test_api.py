#!/usr/bin/env python3
"""
Test API endpoints after deployment
Verifies that backend is working correctly
"""

import requests
import json
import boto3
import sys

print("🧪 Testing RetailBrain Copilot API...")

try:
    # Load CDK outputs
    with open('cdk-outputs.json') as f:
        outputs = json.load(f)
        api_url = outputs['RetailBrainStack']['ApiUrl']
        user_pool_id = outputs['RetailBrainStack']['UserPoolId']
        client_id = outputs['RetailBrainStack']['UserPoolClientId']
    
    print(f"\n📍 API URL: {api_url}")
    print(f"👤 User Pool: {user_pool_id}")
    
    # ========================================================================
    # Authenticate
    # ========================================================================
    print("\n1️⃣  Authenticating...")
    
    cognito = boto3.client('cognito-idp', region_name='us-east-1')
    
    try:
        response = cognito.initiate_auth(
            ClientId=client_id,
            AuthFlow='USER_PASSWORD_AUTH',
            AuthParameters={
                'USERNAME': 'demo@retailbrain.com',
                'PASSWORD': 'DemoPass123!'
            }
        )
        
        id_token = response['AuthenticationResult']['IdToken']
        print("   ✅ Authentication successful")
        
    except cognito.exceptions.NotAuthorizedException:
        print("   ❌ Authentication failed - user not found or wrong password")
        print("\n   Create user first:")
        print(f"   aws cognito-idp admin-create-user --user-pool-id {user_pool_id} --username demo@retailbrain.com ...")
        sys.exit(1)
    
    # ========================================================================
    # Test API Endpoints
    # ========================================================================
    headers = {
        'Authorization': id_token,
        'Content-Type': 'application/json'
    }
    
    # Test 1: Forecast query
    print("\n2️⃣  Testing forecast query...")
    try:
        response = requests.post(
            f"{api_url}api/v1/query",
            headers=headers,
            json={
                'query': 'What is the demand forecast for SKU-001 next week?',
                'userId': 'demo@retailbrain.com',
                'role': 'planner'
            },
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Status: {response.status_code}")
            print(f"   📊 Intent: {data.get('intent')}")
            print(f"   💬 Answer: {data.get('answer', '')[:100]}...")
        else:
            print(f"   ❌ Status: {response.status_code}")
            print(f"   Error: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
    
    # Test 2: Pricing query
    print("\n3️⃣  Testing pricing query...")
    try:
        response = requests.post(
            f"{api_url}api/v1/query",
            headers=headers,
            json={
                'query': 'What price should I set for SKU-025?',
                'userId': 'demo@retailbrain.com',
                'role': 'seller'
            },
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Status: {response.status_code}")
            print(f"   📊 Intent: {data.get('intent')}")
            print(f"   💬 Answer: {data.get('answer', '')[:100]}...")
        else:
            print(f"   ❌ Status: {response.status_code}")
            print(f"   Error: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
    
    # Test 3: Alert query
    print("\n4️⃣  Testing alert query...")
    try:
        response = requests.post(
            f"{api_url}api/v1/query",
            headers=headers,
            json={
                'query': 'Which SKUs are at risk of stockout?',
                'userId': 'demo@retailbrain.com',
                'role': 'planner'
            },
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Status: {response.status_code}")
            print(f"   📊 Intent: {data.get('intent')}")
            print(f"   💬 Answer: {data.get('answer', '')[:100]}...")
        else:
            print(f"   ❌ Status: {response.status_code}")
            print(f"   Error: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
    
    # Test 4: Ambiguous query (should ask for clarification)
    print("\n5️⃣  Testing ambiguous query...")
    try:
        response = requests.post(
            f"{api_url}api/v1/query",
            headers=headers,
            json={
                'query': 'What is the forecast?',
                'userId': 'demo@retailbrain.com',
                'role': 'planner'
            },
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Status: {response.status_code}")
            if data.get('needs_clarification'):
                print(f"   ❓ Clarification needed: {data.get('answer')}")
            else:
                print(f"   💬 Answer: {data.get('answer', '')[:100]}...")
        else:
            print(f"   ❌ Status: {response.status_code}")
            print(f"   Error: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
    
    # ========================================================================
    # Summary
    # ========================================================================
    print("\n" + "="*70)
    print("✅ API TESTING COMPLETE!")
    print("="*70)
    print(f"\n🎯 Next Steps:")
    print(f"   1. Deploy frontend to Amplify")
    print(f"   2. Test end-to-end flow in browser")
    print(f"   3. Record demo video")
    print("\n" + "="*70 + "\n")
    
except FileNotFoundError:
    print("\n❌ Error: cdk-outputs.json not found")
    print("\nRun CDK deployment first:")
    print("   cd backend")
    print("   cdk deploy --outputs-file ../cdk-outputs.json")
    sys.exit(1)
    
except Exception as e:
    print(f"\n❌ Error: {str(e)}")
    sys.exit(1)
