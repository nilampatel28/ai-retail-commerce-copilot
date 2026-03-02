#!/bin/bash

echo "🛑 Stopping AWS Services to Conserve Credits..."
echo ""

# Destroy CDK stack (removes Lambda, API Gateway, DynamoDB, etc.)
echo "1️⃣  Destroying CDK Stack..."
cd backend
npx cdk destroy RetailBrainStack --force

echo ""
echo "2️⃣  Removing frontend S3 bucket..."
aws s3 rm s3://retailbrain-frontend-1772462374 --recursive
aws s3 rb s3://retailbrain-frontend-1772462374 --force

echo ""
echo "======================================================================"
echo "✅ ALL SERVICES STOPPED"
echo "======================================================================"
echo ""
echo "💰 Your AWS credits are now safe!"
echo ""
echo "📝 To restart later, run:"
echo "   ./scripts/restart_services.sh"
echo ""
echo "======================================================================"
