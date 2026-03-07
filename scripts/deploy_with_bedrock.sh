#!/bin/bash

# RetailBrain Copilot - Complete Deployment with Amazon Bedrock
# This script deploys the full application with all AWS services

set -e

echo "=========================================="
echo "RetailBrain Copilot - Full Deployment"
echo "=========================================="
echo ""

# Check AWS credentials
echo "✓ Checking AWS credentials..."
aws sts get-caller-identity > /dev/null 2>&1 || {
    echo "❌ AWS credentials not configured. Run 'aws configure' first."
    exit 1
}

ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
REGION="us-east-1"

echo "✓ AWS Account: $ACCOUNT_ID"
echo "✓ Region: $REGION"
echo ""

# Step 1: Deploy CDK infrastructure
echo "=========================================="
echo "Step 1: Deploying AWS Infrastructure"
echo "=========================================="
echo ""

cd backend

echo "✓ Installing CDK dependencies..."
pip install -q aws-cdk-lib constructs boto3

echo "✓ Bootstrapping CDK (if needed)..."
cdk bootstrap aws://$ACCOUNT_ID/$REGION 2>/dev/null || echo "Already bootstrapped"

echo "✓ Synthesizing CDK stack..."
cdk synth > /dev/null

echo "✓ Deploying CDK stack..."
cdk deploy --require-approval never --outputs-file ../cdk-outputs.json

cd ..

echo ""
echo "✅ Infrastructure deployed successfully!"
echo ""

# Step 2: Load sample data
echo "=========================================="
echo "Step 2: Loading Sample Data"
echo "=========================================="
echo ""

echo "✓ Loading forecasts, alerts, and recommendations..."
python3 scripts/load_dynamodb.py

echo ""
echo "✅ Sample data loaded successfully!"
echo ""

# Step 3: Create Cognito test user
echo "=========================================="
echo "Step 3: Creating Test User"
echo "=========================================="
echo ""

USER_POOL_ID=$(cat cdk-outputs.json | python3 -c "import sys, json; print(json.load(sys.stdin)['RetailBrainStack']['UserPoolId'])")

echo "✓ User Pool ID: $USER_POOL_ID"

# Create user if doesn't exist
aws cognito-idp admin-create-user \
    --user-pool-id $USER_POOL_ID \
    --username demo@retailbrain.com \
    --user-attributes Name=email,Value=demo@retailbrain.com Name=email_verified,Value=true Name=custom:role,Value=planner \
    --message-action SUPPRESS \
    2>/dev/null || echo "User already exists"

# Set permanent password
aws cognito-idp admin-set-user-password \
    --user-pool-id $USER_POOL_ID \
    --username demo@retailbrain.com \
    --password "DemoPass123!" \
    --permanent

echo "✓ Test user created: demo@retailbrain.com / DemoPass123!"
echo ""

# Step 4: Build and deploy frontend
echo "=========================================="
echo "Step 4: Building and Deploying Frontend"
echo "=========================================="
echo ""

cd frontend

echo "✓ Installing frontend dependencies..."
npm install --silent

# Extract outputs from CDK
API_URL=$(cat ../cdk-outputs.json | python3 -c "import sys, json; print(json.load(sys.stdin)['RetailBrainStack']['ApiUrl'])")
USER_POOL_CLIENT_ID=$(cat ../cdk-outputs.json | python3 -c "import sys, json; print(json.load(sys.stdin)['RetailBrainStack']['UserPoolClientId'])")

echo "✓ API URL: $API_URL"
echo "✓ User Pool Client ID: $USER_POOL_CLIENT_ID"

# Update aws-exports.ts
cat > src/aws-exports.ts << EOF
export const awsConfig = {
  region: '$REGION',
  userPoolId: '$USER_POOL_ID',
  userPoolWebClientId: '$USER_POOL_CLIENT_ID',
  apiEndpoint: '${API_URL}api/v1'
};
EOF

echo "✓ Building frontend..."
npm run build

# Deploy to S3
BUCKET_NAME="retailbrain-frontend-$(date +%s)"

echo "✓ Creating S3 bucket: $BUCKET_NAME"
aws s3 mb s3://$BUCKET_NAME --region $REGION

echo "✓ Configuring bucket for static website hosting..."
aws s3 website s3://$BUCKET_NAME --index-document index.html --error-document index.html

echo "✓ Setting bucket policy for public access..."
cat > /tmp/bucket-policy.json << EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "PublicReadGetObject",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::$BUCKET_NAME/*"
    }
  ]
}
EOF

aws s3api put-bucket-policy --bucket $BUCKET_NAME --policy file:///tmp/bucket-policy.json

echo "✓ Uploading frontend files..."
aws s3 sync dist/ s3://$BUCKET_NAME/ --delete

FRONTEND_URL="http://$BUCKET_NAME.s3-website-$REGION.amazonaws.com"

cd ..

echo ""
echo "✅ Frontend deployed successfully!"
echo ""

# Step 5: Test the deployment
echo "=========================================="
echo "Step 5: Testing Deployment"
echo "=========================================="
echo ""

echo "✓ Testing Lambda function..."
python3 scripts/test_api.py

echo ""
echo "✅ All tests passed!"
echo ""

# Save deployment info
cat > LIVE-URL.txt << EOF
RetailBrain Copilot - Live Deployment

Frontend URL: $FRONTEND_URL
API Endpoint: ${API_URL}api/v1
User Pool ID: $USER_POOL_ID
Client ID: $USER_POOL_CLIENT_ID

Test Credentials:
Email: demo@retailbrain.com
Password: DemoPass123!

Deployed: $(date)
Account: $ACCOUNT_ID
Region: $REGION
EOF

echo "=========================================="
echo "🎉 DEPLOYMENT COMPLETE!"
echo "=========================================="
echo ""
echo "Frontend URL: $FRONTEND_URL"
echo "API Endpoint: ${API_URL}api/v1"
echo ""
echo "Login with:"
echo "  Email: demo@retailbrain.com"
echo "  Password: DemoPass123!"
echo ""
echo "AWS Services Deployed:"
echo "  ✓ Amazon Bedrock (Claude 3 Haiku)"
echo "  ✓ AWS Lambda (Python 3.11)"
echo "  ✓ Amazon DynamoDB (4 tables)"
echo "  ✓ Amazon API Gateway"
echo "  ✓ Amazon Cognito"
echo "  ✓ Amazon S3"
echo "  ✓ AWS CDK"
echo ""
echo "Deployment details saved to LIVE-URL.txt"
echo "=========================================="
