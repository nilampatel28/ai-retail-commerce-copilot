# Deployment Guide


All sensitive configuration is generated during deployment and stored locally only.

## Prerequisites

1. **AWS CLI** configured with your credentials
   ```bash
   aws configure
   ```

2. **AWS CDK** installed
   ```bash
   npm install -g aws-cdk
   ```

3. **Python 3.11+** with dependencies
   ```bash
   pip install -r requirements.txt
   ```

4. **Node.js 18+** for frontend
   ```bash
   node --version
   ```

## Deployment Steps

### Option 1: Automated Deployment (Recommended)

1. **Copy the deployment template**:
   ```bash
   cp deploy.template.sh deploy.sh
   chmod +x deploy.sh
   ```

2. **Edit deploy.sh** and set your values:
   ```bash
   DEMO_EMAIL="your-email@example.com"
   DEMO_PASSWORD="YourSecurePassword123!"
   ```

3. **Run deployment**:
   ```bash
   ./deploy.sh
   ```

### Option 2: Manual Deployment

#### Step 1: Deploy Infrastructure
```bash
cd backend
cdk bootstrap  # First time only
cdk deploy --outputs-file ../cdk-outputs.json
cd ..
```

#### Step 2: Load Sample Data
```bash
python3 scripts/load_dynamodb.py
```

#### Step 3: Create Test User
```bash
# Get User Pool ID from cdk-outputs.json
USER_POOL_ID="your-user-pool-id"

aws cognito-idp admin-create-user \
    --user-pool-id $USER_POOL_ID \
    --username demo@example.com \
    --user-attributes Name=email,Value=demo@example.com Name=email_verified,Value=true \
    --message-action SUPPRESS

aws cognito-idp admin-set-user-password \
    --user-pool-id $USER_POOL_ID \
    --username demo@example.com \
    --password "YourPassword123!" \
    --permanent
```

#### Step 4: Configure Frontend
```bash
# Copy template
cp frontend/src/aws-exports.template.ts frontend/src/aws-exports.ts

# Edit frontend/src/aws-exports.ts with values from cdk-outputs.json
```

#### Step 5: Build and Deploy Frontend
```bash
cd frontend
npm install
npm run build

# Get bucket name from cdk-outputs.json
BUCKET_NAME="your-frontend-bucket"
aws s3 sync dist/ s3://$BUCKET_NAME --delete
cd ..
```

## Post-Deployment

### Access Your Application

Your application will be available at:
```
http://[FRONTEND-BUCKET-NAME].s3-website-us-east-1.amazonaws.com
```

The exact URL is in `cdk-outputs.json` under `FrontendBucketWebsiteURL`.

### Test the Application

1. Open the frontend URL
2. Login with your configured credentials
3. Try these sample queries:
   - "What is the demand forecast for SKU-001?"
   - "Show me pricing recommendations"
   - "Which SKUs are at risk of stockout?"

## Security Best Practices

### Files to Keep Local (Never Commit)

These files are automatically excluded by `.gitignore`:
- `cdk-outputs.json` - Contains all deployment details
- `frontend/src/aws-exports.ts` - Contains API endpoints and Cognito config
- `deploy.sh` - Contains your customized deployment script
- `LIVE-URL.txt` - Contains deployment URLs and info
- `docs/` - All documentation with sensitive info

### Changing Passwords

To change the demo user password:
```bash
aws cognito-idp admin-set-user-password \
    --user-pool-id YOUR_USER_POOL_ID \
    --username demo@example.com \
    --password "NewPassword123!" \
    --permanent
```

### Rotating Credentials

If credentials are compromised:
1. Change Cognito user passwords immediately
2. Redeploy the stack to get new API endpoints
3. Update frontend configuration
4. Rebuild and redeploy frontend

## Troubleshooting

### Issue: CDK Deploy Fails
**Solution**: Ensure AWS credentials are configured and you have necessary permissions

### Issue: Frontend Shows CORS Errors
**Solution**: Check that API Gateway CORS is properly configured in `backend/cdk_app.py`

### Issue: Login Fails
**Solution**: Verify Cognito User Pool ID and Client ID in `frontend/src/aws-exports.ts`

### Issue: Bedrock Access Denied
**Solution**: Request model access in AWS Console → Amazon Bedrock → Model access

## Cleanup

To delete all AWS resources:
```bash
cd backend
cdk destroy
cd ..
```

**Warning**: This will delete all data in DynamoDB tables.

## Support

For issues:
1. Check CloudWatch Logs for Lambda errors
2. Verify all AWS services are in the same region (us-east-1)
3. Ensure IAM permissions are correctly configured

## Architecture

This deployment creates:
- 4 DynamoDB tables (Forecasts, Recommendations, Alerts, Conversations)
- 1 Lambda function (Query Handler with Bedrock integration)
- 1 API Gateway REST API
- 1 Cognito User Pool
- 2 S3 buckets (Frontend hosting, Data storage)
- All necessary IAM roles and policies

Total estimated cost: ~$5/month for demo usage

---

**Last Updated**: March 2026  
**Version**: 1.0.0
