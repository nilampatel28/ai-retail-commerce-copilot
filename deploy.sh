#!/bin/bash

# RetailBrain Copilot - Complete Deployment with Amazon Bedrock
set -e

echo "=========================================="
echo "RetailBrain Copilot - Full Deployment"
echo "=========================================="
echo ""

# Check AWS credentials
echo "✓ Checking AWS credentials..."
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
REGION="us-east-1"

echo "✓ AWS Account: $ACCOUNT_ID"
echo "✓ Region: $REGION"
echo ""

# Deploy CDK stack
echo "=========================================="
echo "Step 1: Deploying AWS Infrastructure"
echo "=========================================="
echo ""

cd backend

echo "✓ Bootstrapping CDK..."
npx aws-cdk bootstrap aws://$ACCOUNT_ID/$REGION 2>/dev/null || echo "Already bootstrapped"

echo "✓ Deploying CDK stack..."
npx aws-cdk deploy --require-approval never --outputs-file ../cdk-outputs.json

cd ..

echo ""
echo "✅ Infrastructure deployed!"
echo ""

# Extract outputs
API_URL=$(cat cdk-outputs.json | python3 -c "import sys, json; print(json.load(sys.stdin)['RetailBrainStack']['ApiUrl'])")
USER_POOL_ID=$(cat cdk-outputs.json | python3 -c "import sys, json; print(json.load(sys.stdin)['RetailBrainStack']['UserPoolId'])")
CLIENT_ID=$(cat cdk-outputs.json | python3 -c "import sys, json; print(json.load(sys.stdin)['RetailBrainStack']['UserPoolClientId'])")

echo "API URL: $API_URL"
echo "User Pool ID: $USER_POOL_ID"
echo "Client ID: $CLIENT_ID"
echo ""

# Load sample data
echo "=========================================="
echo "Step 2: Loading Sample Data"
echo "=========================================="
echo ""

python3 scripts/load_dynamodb.py

echo ""
echo "✅ Sample data loaded!"
echo ""

# Create test user
echo "=========================================="
echo "Step 3: Creating Test User"
echo "=========================================="
echo ""

aws cognito-idp admin-create-user \
    --user-pool-id $USER_POOL_ID \
    --username demo@retailbrain.com \
    --user-attributes Name=email,Value=demo@retailbrain.com Name=email_verified,Value=true Name=custom:role,Value=planner \
    --message-action SUPPRESS \
    2>/dev/null || echo "User already exists"

aws cognito-idp admin-set-user-password \
    --user-pool-id $USER_POOL_ID \
    --username demo@retailbrain.com \
    --password "DemoPass123!" \
    --permanent

echo "✅ Test user created: demo@retailbrain.com / DemoPass123!"
echo ""

# Update frontend config
echo "=========================================="
echo "Step 4: Building Frontend"
echo "=========================================="
echo ""

cat > frontend/src/aws-exports.ts << EOF
export const awsConfig = {
  region: '$REGION',
  userPoolId: '$USER_POOL_ID',
  userPoolWebClientId: '$CLIENT_ID',
  apiEndpoint: '${API_URL}api/v1'
};
EOF

cd frontend
npm install
npm run build
cd ..

echo "✅ Frontend built!"
echo ""

# Deploy frontend
echo "=========================================="
echo "Step 5: Deploying Frontend to S3"
echo "=========================================="
echo ""

BUCKET_NAME="retailbrain-frontend-$(date +%s)"

aws s3 mb s3://$BUCKET_NAME --region $REGION
aws s3 website s3://$BUCKET_NAME --index-document index.html --error-document index.html

cat > /tmp/bucket-policy.json << EOF
{
  "Version": "2012-10-17",
  "Statement": [{
    "Sid": "PublicReadGetObject",
    "Effect": "Allow",
    "Principal": "*",
    "Action": "s3:GetObject",
    "Resource": "arn:aws:s3:::$BUCKET_NAME/*"
  }]
}
EOF

aws s3api put-bucket-policy --bucket $BUCKET_NAME --policy file:///tmp/bucket-policy.json
aws s3 sync frontend/dist/ s3://$BUCKET_NAME/ --delete

FRONTEND_URL="http://$BUCKET_NAME.s3-website-$REGION.amazonaws.com"

echo "✅ Frontend deployed!"
echo ""

# Save deployment info
cat > LIVE-URL.txt << EOF
RetailBrain Copilot - Live Deployment

Frontend URL: $FRONTEND_URL
API Endpoint: ${API_URL}api/v1
User Pool ID: $USER_POOL_ID
Client ID: $CLIENT_ID

Test Credentials:
Email: demo@retailbrain.com
Password: DemoPass123!

AWS Services Deployed:
✓ Amazon Bedrock (Claude 3 Haiku)
✓ AWS Lambda (Python 3.11)
✓ Amazon DynamoDB (4 tables)
✓ Amazon API Gateway
✓ Amazon Cognito
✓ Amazon S3
✓ AWS CDK

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
echo "AWS Services:"
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
