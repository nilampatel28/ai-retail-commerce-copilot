# RetailBrain Copilot - Project Structure

## Overview
AI-powered retail decision assistant built with AWS services for the AI for Bharat Hackathon 2026.

## Directory Structure

```
ai-retail-commerce-copilot/
├── backend/              # AWS CDK infrastructure and Lambda functions
│   ├── cdk_app.py       # CDK stack definition
│   └── lambda/          # Lambda function handlers
│       ├── bedrock_handler.py    # Main handler with Bedrock integration
│       ├── query_handler.py      # Alternative handler
│       └── simple_handler.py     # Fallback handler
│
├── frontend/            # React web application
│   ├── src/
│   │   ├── App.tsx                    # Main app component
│   │   └── components/
│   │       ├── ChatInterface.tsx      # Chat UI
│   │       └── Dashboard.tsx          # Analytics dashboard
│   └── dist/            # Built frontend (deployed to S3)
│
├── data/                # Sample retail data (CSV files)
│   ├── forecasts.csv
│   ├── recommendations.csv
│   ├── alerts.csv
│   └── products.csv
│
├── scripts/             # Deployment and utility scripts
│   ├── deploy_with_bedrock.sh    # Full deployment script
│   ├── load_dynamodb.py           # Load data into DynamoDB
│   ├── generate_sample_data.py   # Generate sample data
│   └── test_api.py                # API testing script
│
├── .kiro/               # Kiro spec-driven development files
│   └── specs/retail-brain-copilot/
│       ├── requirements.md        # Feature requirements
│       ├── design.md              # Technical design
│       └── tasks.md               # Implementation tasks
│
├── docs/                # Documentation (not pushed to GitHub)
│   ├── DEMO-SPEAKER-NOTES-FINAL.md
│   ├── AWS-SERVICES-GUIDE.md
│   ├── BEDROCK-USAGE-GUIDE.md
│   ├── SECURITY-CHECKLIST.md
│   └── [other documentation files]
│
├── README.md            # Main project README
└── requirements.txt     # Python dependencies
```

## Key Files

### Backend
- `backend/cdk_app.py` - Defines all AWS infrastructure (DynamoDB, Lambda, API Gateway, Cognito, S3)
- `backend/lambda/bedrock_handler.py` - Lambda function with Amazon Bedrock integration for NLP

### Frontend
- `frontend/src/App.tsx` - Main React application with routing and authentication
- `frontend/src/components/ChatInterface.tsx` - Natural language query interface
- `frontend/src/components/Dashboard.tsx` - Analytics and insights dashboard

### Data
- `data/*.csv` - Sample retail data (50 products, 7,500 forecasts, 58 alerts, 20 recommendations)

### Scripts
- `scripts/deploy_with_bedrock.sh` - Automated deployment script
- `scripts/load_dynamodb.py` - Loads sample data into DynamoDB tables

## AWS Services Used

1. **Amazon Bedrock** - Claude 3 Haiku for natural language processing
2. **AWS Lambda** - Serverless query processing
3. **Amazon DynamoDB** - NoSQL database for retail data
4. **Amazon API Gateway** - RESTful API endpoints
5. **Amazon Cognito** - User authentication and authorization
6. **Amazon S3** - Static website hosting for React frontend
7. **AWS CDK** - Infrastructure as Code

## Getting Started

### Prerequisites
```bash
# Install AWS CLI
pip install awscli

# Configure AWS credentials
aws configure

# Install CDK
npm install -g aws-cdk

# Install Python dependencies
pip install -r requirements.txt
```

### Deploy
```bash
# Run automated deployment
./scripts/deploy_with_bedrock.sh
```

This will:
1. Deploy AWS infrastructure
2. Load sample data
3. Create test user
4. Build and deploy frontend
5. Output live URLs

## Documentation

All detailed documentation is in the `docs/` folder (not pushed to GitHub for security):
- Demo speaker notes
- AWS services integration guide
- Bedrock usage verification
- Security checklist
- Deployment guides

## Security

- All sensitive files are excluded via `.gitignore`
- API endpoints require Cognito authentication
- IAM roles follow least privilege principle
- Data encrypted at rest and in transit

## Live Demo

The application is deployed and accessible at the URL provided in the hackathon submission form.

Test credentials are provided separately (not in this repository).

## Team

AI Innovation_NilamPatel

## Hackathon

AI for Bharat Hackathon 2026

## License

This project was created for the AI for Bharat Hackathon 2026.
