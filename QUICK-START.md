# ⚡ Quick Start - When AWS Credits Arrive

## 🎯 Goal: Deploy working prototype in 2 days

---

## ✅ Pre-Flight Checklist (Already Done!)

- ✅ Sample data generated (22,500 transactions, 50 SKUs)
- ✅ Backend Lambda functions ready
- ✅ CDK infrastructure code ready
- ✅ Frontend package.json ready
- ✅ Deployment scripts ready
- ✅ Test scripts ready

---

## 🚀 Day 1: Backend (12 hours)

### Hour 1: AWS Setup (30 min)

```bash
# 1. Apply AWS credits to your account
# 2. Configure AWS CLI
aws configure
# Enter: Access Key, Secret Key, Region (us-east-1), Format (json)

# 3. Verify credentials
aws sts get-caller-identity

# 4. Enable Bedrock access
# Go to: AWS Console → Bedrock → Model access → Request access to Claude 3 Sonnet
# Wait for approval (usually instant)

# 5. Verify Bedrock access
aws bedrock list-foundation-models --region us-east-1 | grep claude-3-sonnet
```

### Hour 2: Deploy Infrastructure (30 min)

```bash
# 1. Install CDK
npm install -g aws-cdk
cdk --version

# 2. Install Python dependencies
source venv/bin/activate
pip install -r requirements.txt
pip install aws-cdk-lib constructs

# 3. Bootstrap CDK (first time only)
cdk bootstrap

# 4. Deploy stack
cd backend
cdk deploy RetailBrainStack --outputs-file ../cdk-outputs.json --require-approval never

# 5. Verify deployment
cat ../cdk-outputs.json
```

### Hour 3: Load Data (30 min)

```bash
# 1. Upload data to S3
BUCKET_NAME=$(cat cdk-outputs.json | jq -r '.RetailBrainStack.DataBucketName')
aws s3 cp data/ s3://$BUCKET_NAME/data/ --recursive

# 2. Load data into DynamoDB
cd ..
python scripts/load_dynamodb.py

# 3. Verify data loaded
aws dynamodb scan --table-name RetailBrain-Forecasts --max-items 5
```

### Hour 4: Create Test Users (15 min)

```bash
# Run the script
./scripts/create_cognito_user.sh

# Verify users created
USER_POOL_ID=$(cat cdk-outputs.json | jq -r '.RetailBrainStack.UserPoolId')
aws cognito-idp list-users --user-pool-id $USER_POOL_ID
```

### Hour 5: Test Backend (30 min)

```bash
# Install test dependencies
pip install requests

# Run API tests
python scripts/test_api.py

# Expected output:
# ✅ Authentication successful
# ✅ Forecast query working
# ✅ Pricing query working
# ✅ Alert query working
```

### Hours 6-12: Troubleshooting & Optimization

If everything works, you're ahead of schedule! Use this time to:
- Test more query variations
- Optimize Bedrock prompts
- Add error handling
- Prepare demo talking points

---

## 🎨 Day 2: Frontend (12 hours)

### Hour 1-2: Setup Frontend (1 hour)

```bash
# 1. Install Node.js dependencies
cd frontend
npm install

# 2. Create aws-exports.js
cat > src/aws-exports.js << EOF
const awsconfig = {
  aws_project_region: 'us-east-1',
  aws_cognito_region: 'us-east-1',
  aws_user_pools_id: '$(cat ../cdk-outputs.json | jq -r '.RetailBrainStack.UserPoolId')',
  aws_user_pools_web_client_id: '$(cat ../cdk-outputs.json | jq -r '.RetailBrainStack.UserPoolClientId')',
  aws_cloud_logic_custom: [
    {
      name: 'RetailBrainAPI',
      endpoint: '$(cat ../cdk-outputs.json | jq -r '.RetailBrainStack.ApiUrl')',
      region: 'us-east-1'
    }
  ]
};
export default awsconfig;
EOF

# 3. Test local build
npm run build
```

### Hour 3-6: Build Components (3 hours)

Copy the component code from DEPLOYMENT-GUIDE.md:
1. `src/App.tsx` - Main app with authentication
2. `src/components/ChatInterface.tsx` - Chat component
3. `src/components/Dashboard.tsx` - Dashboard component

```bash
# Create component files
mkdir -p src/components
# Copy code from DEPLOYMENT-GUIDE.md into these files

# Test local dev server
npm run dev
# Open http://localhost:5173
```

### Hour 7-8: Deploy to Amplify (1 hour)

```bash
# 1. Install Amplify CLI
npm install -g @aws-amplify/cli

# 2. Initialize Amplify
amplify init
# Choose: RetailBrainCopilot, dev, default editor, JavaScript, React, build command: npm run build, dist directory: dist

# 3. Add hosting
amplify add hosting
# Choose: Hosting with Amplify Console, Manual deployment

# 4. Build and publish
npm run build
amplify publish

# 5. Save the live URL
echo "Live URL: https://main.d1234567890.amplifyapp.com" > ../LIVE-URL.txt
```

### Hour 9-10: Test End-to-End (1 hour)

```bash
# 1. Open live URL in browser
# 2. Login with: demo@retailbrain.com / DemoPass123!
# 3. Test queries:
#    - "What is the demand forecast for SKU-001?"
#    - "Which SKUs are at risk of stockout?"
#    - "What price should I set for SKU-025?"
# 4. Check dashboard loads
# 5. Test in incognito mode
# 6. Test on mobile (responsive)
```

### Hour 11: Record Demo Video (1 hour)

```bash
# 1. Prepare demo script (see WINNING-STRATEGY.md)
# 2. Use Loom or OBS Studio
# 3. Record 3-5 minute demo:
#    - Introduction (30 sec)
#    - Problem statement (30 sec)
#    - Live demo (3 min)
#    - Technology overview (30 sec)
#    - Business value (30 sec)
# 4. Upload to YouTube (unlisted)
# 5. Save link: https://youtu.be/YOUR_VIDEO_ID
```

### Hour 12: Submit (1 hour)

```bash
# 1. Update README with live URL and video link
# 2. Write project summary (200-300 words)
# 3. Take screenshots for backup
# 4. Submit via hackathon dashboard:
#    - Project Summary
#    - Demo Video link
#    - GitHub Repository
#    - Working Prototype URL
#    - Problem Statement
# 5. Verify submission received
```

---

## 🆘 Emergency Shortcuts

### If Running Out of Time

**Priority 1 (Must Have):**
- ✅ Backend deployed with Bedrock integration
- ✅ At least 1 query type working (forecast)
- ✅ Basic frontend with chat interface
- ✅ Live URL accessible

**Priority 2 (Nice to Have):**
- Dashboard with metrics
- Multiple query types
- Polished UI

**Priority 3 (Skip if Needed):**
- Advanced visualizations
- Mobile responsiveness
- Extensive error handling

### If Bedrock Access Delayed

Use OpenAI API as temporary fallback:
```python
import openai
openai.api_key = "your-key"
response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": prompt}]
)
```

### If SageMaker Too Complex

Use pre-computed forecasts from sample data (already in DynamoDB).

### If Frontend Build Fails

Deploy a simple HTML page with fetch API:
```html
<!DOCTYPE html>
<html>
<head><title>RetailBrain Copilot</title></head>
<body>
  <h1>RetailBrain Copilot</h1>
  <input id="query" placeholder="Ask a question...">
  <button onclick="sendQuery()">Send</button>
  <div id="response"></div>
  <script>
    async function sendQuery() {
      const query = document.getElementById('query').value;
      const response = await fetch('YOUR_API_URL/api/v1/query', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({query, userId: 'demo', role: 'planner'})
      });
      const data = await response.json();
      document.getElementById('response').innerText = data.answer;
    }
  </script>
</body>
</html>
```

---

## 📊 Progress Tracking

### Day 1 Milestones
- [ ] Hour 1: AWS setup complete
- [ ] Hour 2: CDK deployed
- [ ] Hour 3: Data loaded
- [ ] Hour 4: Users created
- [ ] Hour 5: API tested
- [ ] Hour 12: Backend complete ✅

### Day 2 Milestones
- [ ] Hour 2: Frontend setup
- [ ] Hour 6: Components built
- [ ] Hour 8: Deployed to Amplify
- [ ] Hour 10: End-to-end tested
- [ ] Hour 11: Video recorded
- [ ] Hour 12: Submitted ✅

---

## 💰 Cost Monitoring

Check costs regularly:
```bash
aws ce get-cost-and-usage \
  --time-period Start=2026-03-01,End=2026-03-05 \
  --granularity DAILY \
  --metrics BlendedCost
```

Expected: ~$35 total (well within $100 budget)

---

## 🎯 Success Criteria

Before submitting, verify:
- [ ] Live URL works in incognito mode
- [ ] Can login with demo@retailbrain.com
- [ ] Can ask questions and get AI responses
- [ ] Dashboard shows metrics
- [ ] Demo video uploaded to YouTube
- [ ] GitHub README has all links
- [ ] Project summary written

---

## 📞 Support

If stuck:
- AWS Support: Check AWS Console
- Hackathon Mentors: Use provided contact
- GitHub Issues: Document problems
- Stack Overflow: Search for errors

---

## 🏆 You've Got This!

Everything is prepared. When AWS credits arrive:
1. Follow this checklist step-by-step
2. Don't skip steps
3. Test frequently
4. Ask for help if stuck
5. Submit on time

**Remember: A simple, working demo beats a complex, broken one.**

**Focus on Bedrock integration - it's your key differentiator!**

🚀 Good luck! 🏆
