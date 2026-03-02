#!/bin/bash

echo "🚀 Restarting AWS Services..."
echo ""

# Redeploy CDK stack
echo "1️⃣  Deploying CDK Stack..."
cd backend
npx cdk deploy RetailBrainStack --outputs-file ../cdk-outputs.json --require-approval never

echo ""
echo "2️⃣  Loading data into DynamoDB..."
cd ..
python scripts/load_dynamodb.py

echo ""
echo "3️⃣  Creating Cognito users..."
./scripts/create_cognito_user.sh

echo ""
echo "4️⃣  Deploying frontend..."
./scripts/deploy_frontend.sh

echo ""
echo "======================================================================"
echo "✅ ALL SERVICES RESTARTED"
echo "======================================================================"
echo ""
echo "🌐 Your application is live again!"
echo ""
echo "Check FINAL-DEPLOYMENT-SUMMARY.md for URLs and credentials"
echo ""
echo "======================================================================"
