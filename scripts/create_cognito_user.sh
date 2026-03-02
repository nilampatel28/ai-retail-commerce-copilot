#!/bin/bash
# Create test user in Cognito User Pool

echo "👤 Creating Cognito test user..."

# Check if cdk-outputs.json exists
if [ ! -f "cdk-outputs.json" ]; then
    echo "❌ Error: cdk-outputs.json not found"
    echo "Run CDK deployment first:"
    echo "   cd backend && cdk deploy --outputs-file ../cdk-outputs.json"
    exit 1
fi

# Extract User Pool ID from CDK outputs
USER_POOL_ID=$(cat cdk-outputs.json | jq -r '.RetailBrainStack.UserPoolId')

if [ -z "$USER_POOL_ID" ] || [ "$USER_POOL_ID" == "null" ]; then
    echo "❌ Error: Could not find User Pool ID in cdk-outputs.json"
    exit 1
fi

echo "📍 User Pool ID: $USER_POOL_ID"

# Create demo user (planner role)
echo ""
echo "1️⃣  Creating demo user (planner)..."
aws cognito-idp admin-create-user \
  --user-pool-id $USER_POOL_ID \
  --username demo@retailbrain.com \
  --user-attributes Name=email,Value=demo@retailbrain.com Name=custom:role,Value=planner \
  --temporary-password TempPass123! \
  --message-action SUPPRESS \
  2>/dev/null

# Set permanent password
aws cognito-idp admin-set-user-password \
  --user-pool-id $USER_POOL_ID \
  --username demo@retailbrain.com \
  --password DemoPass123! \
  --permanent

echo "   ✅ Created: demo@retailbrain.com (password: DemoPass123!)"

# Create merchandiser user
echo ""
echo "2️⃣  Creating merchandiser user..."
aws cognito-idp admin-create-user \
  --user-pool-id $USER_POOL_ID \
  --username merchandiser@retailbrain.com \
  --user-attributes Name=email,Value=merchandiser@retailbrain.com Name=custom:role,Value=merchandiser \
  --temporary-password TempPass123! \
  --message-action SUPPRESS \
  2>/dev/null

aws cognito-idp admin-set-user-password \
  --user-pool-id $USER_POOL_ID \
  --username merchandiser@retailbrain.com \
  --password DemoPass123! \
  --permanent

echo "   ✅ Created: merchandiser@retailbrain.com (password: DemoPass123!)"

# Create seller user
echo ""
echo "3️⃣  Creating seller user..."
aws cognito-idp admin-create-user \
  --user-pool-id $USER_POOL_ID \
  --username seller@retailbrain.com \
  --user-attributes Name=email,Value=seller@retailbrain.com Name=custom:role,Value=seller \
  --temporary-password TempPass123! \
  --message-action SUPPRESS \
  2>/dev/null

aws cognito-idp admin-set-user-password \
  --user-pool-id $USER_POOL_ID \
  --username seller@retailbrain.com \
  --password DemoPass123! \
  --permanent

echo "   ✅ Created: seller@retailbrain.com (password: DemoPass123!)"

echo ""
echo "======================================================================"
echo "✅ USER CREATION COMPLETE!"
echo "======================================================================"
echo ""
echo "📋 Test Users:"
echo "   • demo@retailbrain.com (planner) - password: DemoPass123!"
echo "   • merchandiser@retailbrain.com (merchandiser) - password: DemoPass123!"
echo "   • seller@retailbrain.com (seller) - password: DemoPass123!"
echo ""
echo "🎯 Next Steps:"
echo "   1. Test API with: python scripts/test_api.py"
echo "   2. Deploy frontend to Amplify"
echo "   3. Test login in browser"
echo ""
echo "======================================================================"
