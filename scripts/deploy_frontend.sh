#!/bin/bash

echo "🚀 Deploying Frontend to S3..."

# Create S3 bucket for frontend hosting
BUCKET_NAME="retailbrain-frontend-$(date +%s)"
REGION="us-east-1"

echo "📦 Creating S3 bucket: $BUCKET_NAME"
aws s3 mb s3://$BUCKET_NAME --region $REGION

# Configure bucket for static website hosting
echo "🌐 Configuring static website hosting..."
aws s3 website s3://$BUCKET_NAME --index-document index.html --error-document index.html

# Set bucket policy for public read access
echo "🔓 Setting bucket policy..."
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

# Upload frontend build
echo "📤 Uploading frontend files..."
aws s3 sync frontend/dist/ s3://$BUCKET_NAME/ --delete

# Get website URL
WEBSITE_URL="http://$BUCKET_NAME.s3-website-$REGION.amazonaws.com"

echo ""
echo "======================================================================"
echo "✅ FRONTEND DEPLOYED SUCCESSFULLY!"
echo "======================================================================"
echo ""
echo "🌐 Website URL: $WEBSITE_URL"
echo ""
echo "📝 Save this URL for your hackathon submission!"
echo ""
echo "======================================================================"

# Save URL to file
echo $WEBSITE_URL > LIVE-URL.txt
echo "✅ URL saved to LIVE-URL.txt"
