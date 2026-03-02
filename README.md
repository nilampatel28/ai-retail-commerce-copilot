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

## Getting Started

### Prerequisites

- AWS Account with Bedrock access enabled
- Node.js 18+ and Python 3.11+
- AWS CDK CLI installed
- Git

### Implementation Roadmap

The project follows a 64-hour implementation plan organized into 8 phases:

1. **Phase 1**: Core Infrastructure (AWS CDK, VPC, DynamoDB, S3, Cognito, API Gateway)
2. **Phase 2**: Data Ingestion Pipeline (Kinesis, validation Lambdas)
3. **Phase 3**: ML Models (SageMaker DeepAR, XGBoost, Risk Detector)
4. **Phase 4**: Bedrock Integration (Claude 3 Sonnet for NLU)
5. **Phase 5**: Explainability Engine (SHAP + Bedrock)
6. **Phase 6**: Frontend (React + Amplify)
7. **Phase 7**: Alerts and Workflows (SNS, Step Functions)
8. **Phase 8**: Monitoring and Polish (CloudWatch, audit logging)

See `.kiro/specs/retail-brain-copilot/tasks.md` for detailed implementation tasks.

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
