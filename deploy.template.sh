#!/bin/bash

# RetailBrain Copilot - Deployment Script Template
# Copy this to deploy.sh and customize with your values

set -e

echo "🚀 RetailBrain Copilot - Full Deployment"
echo "=========================================="
echo ""

# Configuration
DEMO_EMAIL="YOUR_DEMO_EMAIL"  # e.g., demo@yourcompany.com
DEMO_PASSWORD="YOUR_SECURE_PASSWORD"  # Use a strong password
AWS_REGION="us-east-1"

# Step 1: Deploy CDK Infrastructure
echo "📦 Step 1: Deploying AWS Infrastructure..."
cd backend
cdk deploy --outputs-file ../cdk-outputs.json --require-approval never
cd ..

# Extract outputs
USER_POOL_ID=$(jq -r '.RetailBrainStack.UserPoolId' cdk-outputs.json)
CLIENT_ID=$(jq -r '.RetailBrainStack.UserPoolClientId' cdk-outputs.json)
API_ENDPOINT=$(jq -r '.RetailBrainStack.ApiEndpoint' cdk-outputs.json)
FRONTEND_BUCKET=$(jq -r '.RetailBrainStack.FrontendBucketName' cdk-outputs.json)

echo "✅ Infrastructure deployed"
echo ""

# Step 2: Load Sample Data
echo "📊 Step 2: Loading sample data into DynamoDB..."
python3 scripts/load_dynamodb.py
echo "✅ Data loaded"
echo ""

# Step 3: Create Test User
echo "👤 Step 3: Creating test user..."
aws cognito-idp admin-create-user \
    --user-pool-id $USER_POOL_ID \
    --username $DEMO_EMAIL \
    --user-attributes Name=email,Value=$DEMO_EMAIL Name=email_verified,Value=true \
    --message-action SUPPRESS \
    --region $AWS_REGION

aws cognito-idp admin-set-user-password \
    --user-pool-id $USER_POOL_ID \
    --username $DEMO_EMAIL \
    --password "$DEMO_PASSWORD" \
    --permanent

echo "✅ Test user created: $DEMO_EMAIL"
echo ""

# Step 4: Update Frontend Configuration
echo "⚙️  Step 4: Updating frontend configuration..."
cat > frontend/src/aws-exports.ts << EOF
export const awsConfig = {
  Auth: {
    Cognito: {
      userPoolId: '$USER_POOL_ID',
      userPoolClientId: '$CLIENT_ID',
      region: '$AWS_REGION'
    }
  }
};

export const apiEndpoint = '$API_ENDPOINT/api/v1';
EOF

echo "✅ Frontend configured"
echo ""

# Step 5: Build and Deploy Frontend
echo "🏗️  Step 5: Building and deploying frontend..."
cd frontend
npm install
npm run build
aws s3 sync dist/ s3://$FRONTEND_BUCKET --delete
cd ..

FRONTEND_URL="http://$FRONTEND_BUCKET.s3-website-$AWS_REGION.amazonaws.com"

echo "✅ Frontend deployed"
echo ""

# Save deployment info locally (not committed to git)
cat > LIVE-URL.txt << EOF
RetailBrain Copilot - Deployment Info
======================================

Frontend URL: $FRONTEND_URL

API Endpoint: $API_ENDPOINT

Test Credentials:
- Email: $DEMO_EMAIL
- Password: [REDACTED - Check your password manager]

Deployed: $(date)
EOF

echo "=========================================="
echo "✅ DEPLOYMENT COMPLETE!"
echo "=========================================="
echo ""
echo "🌐 Live URL: $FRONTEND_URL"
echo ""
echo "Login with:"
echo "  Email: $DEMO_EMAIL"
echo "  Password: [Your configured password]"
echo ""
echo "AWS Services Deployed:"
echo "  ✅ Amazon Bedrock (Claude 3 Haiku)"
echo "  ✅ AWS Lambda"
echo "  ✅ Amazon DynamoDB"
echo "  ✅ Amazon API Gateway"
echo "  ✅ Amazon Cognito"
echo "  ✅ Amazon S3"
echo "  ✅ AWS CDK"
echo ""
echo "📝 Deployment details saved to LIVE-URL.txt (local only)"
echo ""
