# RetailBrain Copilot - AI Decision Assistant for Retail

An AI-powered decision assistant system designed to help retail merchandising, pricing, and inventory teams make faster, data-driven decisions. Built for the AI for Bharat Hackathon using AWS Generative AI services.

## Overview

RetailBrain Copilot transforms complex retail data into clear, explainable, and actionable recommendations through a conversational interface. The system leverages Amazon Bedrock for natural language understanding, SageMaker for custom ML models, and a comprehensive suite of AWS managed services.

## Key Features

- **Conversational AI Interface**: Natural language queries powered by Amazon Bedrock (Claude 3 Sonnet)
- **Demand Forecasting**: ML-based predictions using SageMaker DeepAR
- **Pricing Optimization**: AI-driven pricing recommendations with margin constraints
- **Explainable AI**: SHAP-based explanations for all recommendations
- **Proactive Alerts**: Automated stockout and overstock risk detection
- **Human-in-the-Loop**: Approval workflows for AI recommendations
- **Cross-Functional Intelligence**: Integrated insights across merchandising, inventory, and pricing

## Architecture

Built entirely on AWS serverless and managed services:

- **Amazon Bedrock**: Foundation models for NLU and explanation generation
- **Amazon SageMaker**: Custom ML models (DeepAR, XGBoost)
- **AWS Lambda**: Serverless compute for all business logic
- **Amazon DynamoDB**: Real-time operational data storage
- **Amazon Kinesis**: Real-time data ingestion
- **AWS Step Functions**: Workflow orchestration
- **Amazon API Gateway**: RESTful and WebSocket APIs
- **AWS Cognito**: Authentication and authorization
- **Amazon S3**: Data lake and model artifacts
- **Amazon CloudWatch**: Monitoring and observability

## Project Structure

```
.
├── .kiro/
│   └── specs/
│       └── retail-brain-copilot/
│           ├── requirements.md    # 25 detailed requirements
│           ├── design.md          # Comprehensive technical design
│           └── tasks.md           # 60 implementation tasks
├── README.md
└── .gitignore
```

## 🚀 Quick Start

**Status**: ✅ All prerequisites completed! Ready for deployment when AWS credits arrive.

### What's Ready

- ✅ **Sample Data Generated**: 22,500 transactions, 50 SKUs, 5 locations, 90 days history
- ✅ **Backend Code**: Lambda functions, CDK infrastructure, API handlers
- ✅ **Frontend Template**: React app with Amplify configuration
- ✅ **Deployment Scripts**: Automated setup and testing scripts
- ✅ **Documentation**: Complete guides for deployment and demo

### Prerequisites

- AWS Account with Bedrock access enabled
- Node.js 18+ and Python 3.11+
- AWS CDK CLI installed
- Git

### 2-Day Implementation Plan

When AWS credits arrive, follow these guides:

1. **[QUICK-START.md](QUICK-START.md)** - Step-by-step checklist for 2-day deployment
2. **[DEPLOYMENT-GUIDE.md](DEPLOYMENT-GUIDE.md)** - Detailed deployment instructions
3. **[2-DAY-MVP-PLAN.md](2-DAY-MVP-PLAN.md)** - Hour-by-hour implementation plan
4. **[WINNING-STRATEGY.md](WINNING-STRATEGY.md)** - Strategy for winning the hackathon

### Generated Sample Data

Located in `data/` directory:
- **products.csv**: 50 SKUs across 5 categories
- **sales_history.csv**: 22,500 transactions with seasonality
- **inventory_current.csv**: 250 inventory records
- **forecasts.csv**: 7,500 pre-computed forecasts
- **recommendations.csv**: 20 pricing recommendations
- **alerts.csv**: 58 active alerts (stockout, overstock)

### Ready-to-Deploy Code

- **backend/query_handler.py**: Lambda function for query processing with Bedrock
- **backend/cdk_app.py**: CDK infrastructure (DynamoDB, Lambda, API Gateway, Cognito)
- **frontend/package.json**: React app dependencies
- **scripts/**: Automated deployment and testing scripts

## Why AI is Essential

Traditional retail decision-making relies on manual analysis and rigid rule-based systems, leading to:
- Delayed responses to market changes (weeks vs. hours)
- Suboptimal decisions due to inability to process complex multi-dimensional data
- Stockouts and overstocking costing 5-10% of annual revenue

AI solves these problems through:
- **Pattern Recognition at Scale**: Identify complex demand patterns across thousands of SKUs
- **Real-time Adaptation**: Continuously learn from new data and adapt to market conditions
- **Multi-factor Optimization**: Simultaneously optimize revenue, margin, and inventory costs
- **Natural Language Understanding**: Enable non-technical users to interact with complex data
- **Predictive Capabilities**: Proactive insights that prevent problems before they occur

## AWS Service Usage

### Generative AI
- **Amazon Bedrock**: Claude 3 Sonnet for natural language understanding, query parsing, and explanation generation
- **RAG Workflows**: Vector embeddings in OpenSearch for retrieving relevant historical patterns

### ML/AI
- **Amazon SageMaker**: Custom ML models for demand forecasting (DeepAR) and pricing optimization (XGBoost)
- **SHAP Integration**: Explainable AI with feature importance analysis

### Compute & Storage
- **AWS Lambda**: Serverless functions for API handlers, data processing, and ML inference
- **Amazon DynamoDB**: Low-latency operational data (inventory, forecasts, recommendations)
- **Amazon S3**: Data lake for historical data and model artifacts
- **Amazon RDS**: PostgreSQL for audit logs and compliance

### Integration & Orchestration
- **Amazon API Gateway**: REST and WebSocket APIs with Cognito authorization
- **AWS Step Functions**: Human-in-the-loop approval workflows
- **Amazon Kinesis**: Real-time data ingestion streams
- **Amazon EventBridge**: Event routing and scheduled jobs

### Security & Monitoring
- **AWS Cognito**: User authentication and role-based access control
- **Amazon CloudWatch**: Metrics, logs, alarms, and dashboards
- **AWS IAM**: Fine-grained access control policies
- **AWS KMS**: Encryption key management

## Business Value

- **Reduce Stockouts**: Proactive alerts prevent lost sales (5-10% revenue impact)
- **Optimize Pricing**: AI-driven recommendations maximize revenue and margin
- **Faster Decisions**: Natural language interface accelerates decision-making from days to minutes
- **Build Trust**: Explainable AI with confidence scores and reasoning
- **Scalable**: Handle 10,000+ SKUs across 500+ locations

## Team

**Team Name**: AI Innovation_NilamPatel  
**Team Leader**: Nilam Patel  
**Hackathon**: AI for Bharat Hackathon (Powered by AWS)

## License

This project is developed for the AI for Bharat Hackathon.

## Acknowledgments

- Built using Kiro for spec-driven development
- Powered by AWS Generative AI services
- Innovation Partner: YourStory
