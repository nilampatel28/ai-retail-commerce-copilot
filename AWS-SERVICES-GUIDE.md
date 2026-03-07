# AWS Services Integration Guide

## RetailBrain Copilot - Complete AWS Architecture

This document explains how RetailBrain Copilot leverages multiple AWS services to deliver an intelligent retail decision assistant.

---

## AWS Services Used

### 1. **Amazon Bedrock** 🤖
**Purpose**: AI/ML Foundation Models for Natural Language Processing

**How We Use It**:
- **Intent Extraction**: Claude 3 Haiku analyzes user queries to understand what they're asking for
- **Response Generation**: Converts structured data into natural, conversational responses
- **Model**: `anthropic.claude-3-haiku-20240307-v1:0`

**Key Features**:
- No model training required - use pre-trained Claude models
- Serverless - pay only for what you use
- Low latency responses (< 2 seconds)

**Code Location**: `backend/lambda/bedrock_handler.py`

**Example**:
```python
# User asks: "What is the forecast for SKU-001?"
# Bedrock extracts: {"intent": "forecast", "sku": "SKU-001"}
# Bedrock generates: "📊 Forecast for SKU-001: 486 units over 7 days..."
```

---

### 2. **AWS Lambda** ⚡
**Purpose**: Serverless compute for query processing

**How We Use It**:
- **Function**: `RetailBrain-QueryHandler`
- **Runtime**: Python 3.11
- **Memory**: 512 MB
- **Timeout**: 30 seconds

**Responsibilities**:
1. Receive user queries from API Gateway
2. Call Bedrock for intent extraction
3. Query DynamoDB for data
4. Call Bedrock for response generation
5. Return formatted response

**Code Location**: `backend/lambda/bedrock_handler.py`

**Cost**: ~$0.20 per 1 million requests

---

### 3. **Amazon DynamoDB** 💾
**Purpose**: NoSQL database for retail data

**Tables**:

#### **RetailBrain-Forecasts**
- **Partition Key**: `sku` (String)
- **Sort Key**: `forecast_date` (String)
- **Data**: 7,500 demand forecasts
- **Use Case**: Store AI-generated demand predictions

#### **RetailBrain-Recommendations**
- **Partition Key**: `recommendation_id` (String)
- **Sort Key**: `created_at` (String)
- **GSI**: `SKUIndex` (sku + created_at)
- **Data**: 20 pricing recommendations
- **Use Case**: Store pricing optimization suggestions

#### **RetailBrain-Alerts**
- **Partition Key**: `alert_id` (String)
- **Sort Key**: `created_at` (String)
- **Data**: 58 inventory alerts
- **Use Case**: Track stockout and overstock risks

#### **RetailBrain-Conversations**
- **Partition Key**: `session_id` (String)
- **Sort Key**: `timestamp` (String)
- **Use Case**: Store conversation history for context

**Billing**: Pay-per-request (no provisioned capacity)

**Code Location**: `backend/cdk_app.py` (lines 30-100)

---

### 4. **Amazon API Gateway** 🌐
**Purpose**: RESTful API for frontend-backend communication

**Endpoints**:
- `POST /api/v1/query` - Submit natural language queries
- `GET /api/v1/forecasts/{sku}` - Get forecast data
- `GET /api/v1/recommendations` - Get pricing recommendations
- `GET /api/v1/alerts` - Get inventory alerts

**Features**:
- CORS enabled for frontend access
- Cognito authorization on all endpoints
- Request/response logging
- Throttling and rate limiting

**Code Location**: `backend/cdk_app.py` (lines 180-230)

---

### 5. **Amazon Cognito** 🔐
**Purpose**: User authentication and authorization

**Configuration**:
- **User Pool**: `RetailBrain-Users`
- **Sign-in**: Email + Password
- **Password Policy**: 12+ chars, uppercase, lowercase, digits, symbols
- **Custom Attributes**: `role` (merchandiser, planner, seller)

**Test User**:
- Email: `demo@retailbrain.com`
- Password: `DemoPass123!`
- Role: `planner`

**Security**:
- JWT tokens for API authentication
- Token expiration: 1 hour
- Refresh tokens: 30 days

**Code Location**: `backend/cdk_app.py` (lines 120-150)

---

### 6. **Amazon S3** 📦
**Purpose**: Static website hosting and data storage

**Buckets**:

#### **Frontend Bucket** (`retailbrain-frontend-*`)
- Hosts React application
- Static website hosting enabled
- Public read access
- CloudFront-ready (future enhancement)

#### **Data Bucket** (`retailbrain-data-*`)
- Stores raw CSV files
- Versioning enabled
- Encryption at rest (S3-managed)
- Used for data lake / analytics

**Code Location**: `backend/cdk_app.py` (lines 105-115)

---

### 7. **AWS CDK** 🏗️
**Purpose**: Infrastructure as Code

**Benefits**:
- Define all infrastructure in Python
- Version control for infrastructure
- Repeatable deployments
- Automatic dependency management

**Stack**: `RetailBrainStack`
- Creates all resources in correct order
- Manages IAM permissions
- Outputs connection details

**Code Location**: `backend/cdk_app.py`

**Deploy Command**:
```bash
cd backend
cdk deploy
```

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                         USER                                 │
│                    (Web Browser)                             │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                   Amazon S3                                  │
│              (Static Website Hosting)                        │
│                   React Frontend                             │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                 Amazon Cognito                               │
│              (User Authentication)                           │
│              JWT Token Generation                            │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              Amazon API Gateway                              │
│                 (REST API)                                   │
│         POST /api/v1/query + Auth                            │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                  AWS Lambda                                  │
│           RetailBrain-QueryHandler                           │
│              (Python 3.11)                                   │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  1. Extract Intent (Bedrock)                         │  │
│  │  2. Query Data (DynamoDB)                            │  │
│  │  3. Generate Response (Bedrock)                      │  │
│  └──────────────────────────────────────────────────────┘  │
└──────────┬─────────────────────────────┬────────────────────┘
           │                             │
           ▼                             ▼
┌──────────────────────┐    ┌───────────────────────────────┐
│  Amazon Bedrock      │    │     Amazon DynamoDB           │
│  Claude 3 Haiku      │    │                               │
│                      │    │  • Forecasts Table            │
│  • Intent Extraction │    │  • Recommendations Table      │
│  • Response Gen      │    │  • Alerts Table               │
│                      │    │  • Conversations Table        │
└──────────────────────┘    └───────────────────────────────┘
```

---

## Data Flow Example

### User Query: "What is the demand forecast for SKU-001?"

1. **Frontend** → API Gateway
   - User types query in chat interface
   - Frontend sends POST request with JWT token

2. **API Gateway** → Lambda
   - Validates JWT token with Cognito
   - Routes request to Lambda function

3. **Lambda** → Bedrock (Intent Extraction)
   ```json
   {
     "intent": "forecast",
     "sku": "SKU-001",
     "action": "get demand forecast"
   }
   ```

4. **Lambda** → DynamoDB
   - Query `RetailBrain-Forecasts` table
   - Filter by `sku = "SKU-001"`
   - Retrieve 7-30 days of forecasts

5. **Lambda** → Bedrock (Response Generation)
   - Input: Query + Intent + Data
   - Output: Natural language response

6. **Lambda** → API Gateway → Frontend
   ```json
   {
     "answer": "📊 Forecast for SKU-001:\n\nNext 7 days: 486 units total\nDaily average: 69.4 units/day\nConfidence: 85%\n\n💡 Maintain 580 units in stock (includes 20% safety buffer)",
     "intent": "forecast",
     "sku": "SKU-001",
     "powered_by": "Amazon Bedrock Claude 3"
   }
   ```

---

## Cost Breakdown

### Monthly Costs (Estimated for Demo)

| Service | Usage | Cost |
|---------|-------|------|
| **Amazon Bedrock** | 10,000 requests/month | ~$3.00 |
| **AWS Lambda** | 10,000 invocations | ~$0.20 |
| **Amazon DynamoDB** | 10,000 reads/writes | ~$1.25 |
| **Amazon API Gateway** | 10,000 requests | ~$0.04 |
| **Amazon Cognito** | 100 active users | Free tier |
| **Amazon S3** | 1 GB storage + hosting | ~$0.50 |
| **AWS CDK** | Infrastructure mgmt | Free |
| **TOTAL** | | **~$5.00/month** |

**Note**: Actual costs depend on usage. AWS Free Tier covers most services for first 12 months.

---

## Security Features

### 1. **Authentication** (Cognito)
- Email + password authentication
- JWT tokens with 1-hour expiration
- Secure password policy

### 2. **Authorization** (API Gateway + Cognito)
- All API endpoints require valid JWT
- Role-based access control (custom:role attribute)
- Request validation

### 3. **Data Encryption**
- **In Transit**: TLS 1.2+ for all API calls
- **At Rest**: S3 and DynamoDB encryption enabled

### 4. **IAM Permissions** (Least Privilege)
- Lambda can only:
  - Read from DynamoDB tables
  - Invoke Bedrock models
  - Write logs to CloudWatch
- No admin or write permissions

### 5. **Audit Logging**
- CloudWatch Logs for all Lambda invocations
- API Gateway access logs
- DynamoDB item-level logging (optional)

---

## Deployment Instructions

### Prerequisites
```bash
# Install AWS CLI
pip install awscli

# Configure credentials
aws configure

# Install CDK
npm install -g aws-cdk
```

### Deploy Everything
```bash
# Run automated deployment script
./scripts/deploy_with_bedrock.sh
```

This script will:
1. ✅ Deploy CDK infrastructure (DynamoDB, Lambda, API Gateway, Cognito, S3)
2. ✅ Load sample data into DynamoDB
3. ✅ Create test user in Cognito
4. ✅ Build and deploy React frontend to S3
5. ✅ Test the deployment
6. ✅ Output live URLs

### Manual Deployment

#### Step 1: Deploy Backend
```bash
cd backend
cdk bootstrap  # First time only
cdk deploy --outputs-file ../cdk-outputs.json
```

#### Step 2: Load Data
```bash
python3 scripts/load_dynamodb.py
```

#### Step 3: Create User
```bash
./scripts/create_cognito_user.sh
```

#### Step 4: Deploy Frontend
```bash
cd frontend
npm install
npm run build
./scripts/deploy_frontend.sh
```

---

## Testing

### Test Lambda Function
```bash
python3 scripts/test_api.py
```

### Test Bedrock Integration
```bash
aws bedrock-runtime invoke-model \
  --model-id anthropic.claude-3-haiku-20240307-v1:0 \
  --body '{"anthropic_version":"bedrock-2023-05-31","max_tokens":100,"messages":[{"role":"user","content":"Hello"}]}' \
  --region us-east-1 \
  output.json
```

### Test API Endpoint
```bash
# Get auth token first (use Cognito)
curl -X POST https://YOUR-API-URL/api/v1/query \
  -H "Authorization: Bearer YOUR-JWT-TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the forecast for SKU-001?"}'
```

---

## Monitoring

### CloudWatch Dashboards
- Lambda invocation count and duration
- API Gateway request count and latency
- DynamoDB read/write capacity
- Bedrock model invocation count

### CloudWatch Logs
- Lambda function logs: `/aws/lambda/RetailBrain-QueryHandler`
- API Gateway logs: `/aws/apigateway/RetailBrainAPI`

### Alarms (Recommended)
- Lambda error rate > 5%
- API Gateway 5xx errors > 10
- DynamoDB throttled requests > 0
- Bedrock throttling errors > 0

---

## Troubleshooting

### Issue: Bedrock Access Denied
**Solution**: Request model access in AWS Console
1. Go to Amazon Bedrock console
2. Click "Model access"
3. Request access to Claude 3 models
4. Wait for approval (usually instant)

### Issue: Lambda Timeout
**Solution**: Increase timeout in CDK
```python
timeout=Duration.seconds(60)  # Increase from 30
```

### Issue: CORS Errors
**Solution**: Check API Gateway CORS configuration
```python
default_cors_preflight_options=apigateway.CorsOptions(
    allow_origins=["*"],  # Or specific domain
    allow_methods=["GET", "POST", "OPTIONS"]
)
```

### Issue: DynamoDB Throttling
**Solution**: Switch to on-demand billing
```python
billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST
```

---

## Future Enhancements

### 1. **Amazon CloudFront**
- CDN for faster frontend loading
- HTTPS with custom domain
- Edge caching

### 2. **Amazon SageMaker**
- Custom demand forecasting models
- Model training and deployment
- A/B testing of models

### 3. **Amazon EventBridge**
- Scheduled forecast updates
- Event-driven alert notifications
- Integration with external systems

### 4. **Amazon QuickSight**
- Business intelligence dashboards
- Advanced analytics
- Executive reporting

### 5. **AWS Step Functions**
- Orchestrate complex workflows
- Multi-step approval processes
- Error handling and retries

---

## Support

For issues or questions:
- **AWS Documentation**: https://docs.aws.amazon.com/
- **Bedrock Guide**: https://docs.aws.amazon.com/bedrock/
- **CDK Guide**: https://docs.aws.amazon.com/cdk/

---

**Last Updated**: March 7, 2026
**Version**: 1.0.0
**Author**: RetailBrain Team
