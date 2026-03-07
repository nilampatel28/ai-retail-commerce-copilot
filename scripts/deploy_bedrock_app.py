#!/usr/bin/env python3
"""
Deploy RetailBrain Copilot with Amazon Bedrock
"""

import subprocess
import json
import sys
import time

def run_command(cmd, cwd=None):
    """Run shell command and return output"""
    print(f"Running: {cmd}")
    result = subprocess.run(
        cmd, 
        shell=True, 
        cwd=cwd,
        capture_output=True, 
        text=True
    )
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        return None
    return result.stdout

def main():
    print("=" * 60)
    print("RetailBrain Copilot - Bedrock Deployment")
    print("=" * 60)
    print()
    
    # Check AWS credentials
    print("✓ Checking AWS credentials...")
    identity = run_command("aws sts get-caller-identity")
    if not identity:
        print("❌ AWS credentials not configured")
        sys.exit(1)
    
    identity_data = json.loads(identity)
    account_id = identity_data['Account']
    print(f"✓ AWS Account: {account_id}")
    print()
    
    # Bootstrap CDK (if needed)
    print("✓ Bootstrapping CDK...")
    run_command(f"cdk bootstrap aws://{account_id}/us-east-1", cwd="backend")
    print()
    
    # Deploy CDK stack
    print("=" * 60)
    print("Deploying CDK Stack...")
    print("=" * 60)
    print()
    
    deploy_cmd = "cdk deploy --require-approval never --outputs-file ../cdk-outputs.json"
    result = run_command(deploy_cmd, cwd="backend")
    
    if not result:
        print("❌ CDK deployment failed")
        sys.exit(1)
    
    print()
    print("✅ CDK Stack deployed successfully!")
    print()
    
    # Load outputs
    try:
        with open("cdk-outputs.json", "r") as f:
            outputs = json.load(f)
        
        stack_outputs = outputs.get('RetailBrainStack', {})
        api_url = stack_outputs.get('ApiUrl', '')
        user_pool_id = stack_outputs.get('UserPoolId', '')
        client_id = stack_outputs.get('UserPoolClientId', '')
        
        print("=" * 60)
        print("Deployment Outputs")
        print("=" * 60)
        print(f"API URL: {api_url}")
        print(f"User Pool ID: {user_pool_id}")
        print(f"Client ID: {client_id}")
        print()
        
        # Load sample data
        print("=" * 60)
        print("Loading Sample Data...")
        print("=" * 60)
        print()
        
        run_command("python3 scripts/load_dynamodb.py")
        print("✅ Sample data loaded!")
        print()
        
        # Create test user
        print("=" * 60)
        print("Creating Test User...")
        print("=" * 60)
        print()
        
        # Create user
        create_user_cmd = f"""aws cognito-idp admin-create-user \
            --user-pool-id {user_pool_id} \
            --username demo@retailbrain.com \
            --user-attributes Name=email,Value=demo@retailbrain.com Name=email_verified,Value=true Name=custom:role,Value=planner \
            --message-action SUPPRESS 2>/dev/null || echo 'User exists'"""
        
        run_command(create_user_cmd)
        
        # Set password
        set_password_cmd = f"""aws cognito-idp admin-set-user-password \
            --user-pool-id {user_pool_id} \
            --username demo@retailbrain.com \
            --password "DemoPass123!" \
            --permanent"""
        
        run_command(set_password_cmd)
        
        print("✅ Test user created: demo@retailbrain.com / DemoPass123!")
        print()
        
        # Update frontend config
        print("=" * 60)
        print("Updating Frontend Configuration...")
        print("=" * 60)
        print()
        
        aws_exports = f"""export const awsConfig = {{
  region: 'us-east-1',
  userPoolId: '{user_pool_id}',
  userPoolWebClientId: '{client_id}',
  apiEndpoint: '{api_url}api/v1'
}};
"""
        
        with open("frontend/src/aws-exports.ts", "w") as f:
            f.write(aws_exports)
        
        print("✅ Frontend configuration updated!")
        print()
        
        # Build frontend
        print("=" * 60)
        print("Building Frontend...")
        print("=" * 60)
        print()
        
        run_command("npm install", cwd="frontend")
        run_command("npm run build", cwd="frontend")
        
        print("✅ Frontend built!")
        print()
        
        # Deploy frontend to S3
        print("=" * 60)
        print("Deploying Frontend to S3...")
        print("=" * 60)
        print()
        
        bucket_name = f"retailbrain-frontend-{int(time.time())}"
        
        # Create bucket
        run_command(f"aws s3 mb s3://{bucket_name} --region us-east-1")
        
        # Configure website hosting
        run_command(f"aws s3 website s3://{bucket_name} --index-document index.html --error-document index.html")
        
        # Set bucket policy
        policy = {
            "Version": "2012-10-17",
            "Statement": [{
                "Sid": "PublicReadGetObject",
                "Effect": "Allow",
                "Principal": "*",
                "Action": "s3:GetObject",
                "Resource": f"arn:aws:s3:::{bucket_name}/*"
            }]
        }
        
        with open("/tmp/bucket-policy.json", "w") as f:
            json.dump(policy, f)
        
        run_command(f"aws s3api put-bucket-policy --bucket {bucket_name} --policy file:///tmp/bucket-policy.json")
        
        # Upload files
        run_command(f"aws s3 sync frontend/dist/ s3://{bucket_name}/ --delete")
        
        frontend_url = f"http://{bucket_name}.s3-website-us-east-1.amazonaws.com"
        
        print("✅ Frontend deployed!")
        print()
        
        # Save deployment info
        deployment_info = f"""RetailBrain Copilot - Live Deployment

Frontend URL: {frontend_url}
API Endpoint: {api_url}api/v1
User Pool ID: {user_pool_id}
Client ID: {client_id}

Test Credentials:
Email: demo@retailbrain.com
Password: DemoPass123!

AWS Services:
✓ Amazon Bedrock (Claude 3 Haiku)
✓ AWS Lambda (Python 3.11)
✓ Amazon DynamoDB (4 tables)
✓ Amazon API Gateway
✓ Amazon Cognito
✓ Amazon S3
✓ AWS CDK

Deployed: {time.strftime('%Y-%m-%d %H:%M:%S')}
Account: {account_id}
Region: us-east-1
"""
        
        with open("LIVE-URL.txt", "w") as f:
            f.write(deployment_info)
        
        print("=" * 60)
        print("🎉 DEPLOYMENT COMPLETE!")
        print("=" * 60)
        print()
        print(f"Frontend URL: {frontend_url}")
        print(f"API Endpoint: {api_url}api/v1")
        print()
        print("Login with:")
        print("  Email: demo@retailbrain.com")
        print("  Password: DemoPass123!")
        print()
        print("Deployment details saved to LIVE-URL.txt")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
