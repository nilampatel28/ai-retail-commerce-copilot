#!/usr/bin/env python3
"""
AWS CDK App for RetailBrain Copilot Infrastructure
Deploys DynamoDB tables, Lambda functions, API Gateway, and Cognito
"""

from aws_cdk import (
    App, Stack, Duration, RemovalPolicy,
    aws_dynamodb as dynamodb,
    aws_lambda as lambda_,
    aws_apigateway as apigateway,
    aws_cognito as cognito,
    aws_s3 as s3,
    aws_iam as iam,
)
from constructs import Construct


class RetailBrainStack(Stack):
    """
    Main CDK stack for RetailBrain Copilot
    """
    
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        # ====================================================================
        # DynamoDB Tables
        # ====================================================================
        
        # Forecasts Table
        forecasts_table = dynamodb.Table(
            self, "ForecastsTable",
            table_name="RetailBrain-Forecasts",
            partition_key=dynamodb.Attribute(
                name="sku",
                type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="forecast_date",
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY,  # For demo only
            time_to_live_attribute="ttl"
        )
        
        # Recommendations Table
        recommendations_table = dynamodb.Table(
            self, "RecommendationsTable",
            table_name="RetailBrain-Recommendations",
            partition_key=dynamodb.Attribute(
                name="recommendation_id",
                type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="created_at",
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY
        )
        
        # Add GSI for SKU queries
        recommendations_table.add_global_secondary_index(
            index_name="SKUIndex",
            partition_key=dynamodb.Attribute(
                name="sku",
                type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="created_at",
                type=dynamodb.AttributeType.STRING
            )
        )
        
        # Alerts Table
        alerts_table = dynamodb.Table(
            self, "AlertsTable",
            table_name="RetailBrain-Alerts",
            partition_key=dynamodb.Attribute(
                name="alert_id",
                type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="created_at",
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY,
            time_to_live_attribute="ttl"
        )
        
        # Conversation History Table
        conversations_table = dynamodb.Table(
            self, "ConversationsTable",
            table_name="RetailBrain-Conversations",
            partition_key=dynamodb.Attribute(
                name="session_id",
                type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="timestamp",
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY,
            time_to_live_attribute="ttl"
        )
        
        # ====================================================================
        # S3 Bucket for Data Lake
        # ====================================================================
        
        data_bucket = s3.Bucket(
            self, "DataBucket",
            bucket_name=f"retailbrain-data-{self.account}",
            encryption=s3.BucketEncryption.S3_MANAGED,
            versioned=True,
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True  # For demo only
        )
        
        # ====================================================================
        # Cognito User Pool
        # ====================================================================
        
        user_pool = cognito.UserPool(
            self, "UserPool",
            user_pool_name="RetailBrain-Users",
            self_sign_up_enabled=False,
            sign_in_aliases=cognito.SignInAliases(email=True),
            password_policy=cognito.PasswordPolicy(
                min_length=12,
                require_lowercase=True,
                require_uppercase=True,
                require_digits=True,
                require_symbols=True
            ),
            standard_attributes=cognito.StandardAttributes(
                email=cognito.StandardAttribute(required=True, mutable=False)
            ),
            custom_attributes={
                "role": cognito.StringAttribute(mutable=True)
            },
            removal_policy=RemovalPolicy.DESTROY
        )
        
        user_pool_client = user_pool.add_client(
            "UserPoolClient",
            auth_flows=cognito.AuthFlow(
                user_password=True,
                user_srp=True
            ),
            generate_secret=False
        )
        
        # ====================================================================
        # Lambda Functions
        # ====================================================================
        
        # Query Handler Lambda
        query_handler = lambda_.Function(
            self, "QueryHandler",
            function_name="RetailBrain-QueryHandler",
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler="query_handler.lambda_handler",
            code=lambda_.Code.from_asset("backend"),
            timeout=Duration.seconds(30),
            memory_size=512,
            environment={
                "FORECASTS_TABLE": forecasts_table.table_name,
                "RECOMMENDATIONS_TABLE": recommendations_table.table_name,
                "ALERTS_TABLE": alerts_table.table_name,
                "CONVERSATION_TABLE": conversations_table.table_name,
                "DATA_BUCKET": data_bucket.bucket_name,
                "AWS_REGION": self.region
            }
        )
        
        # Grant permissions
        forecasts_table.grant_read_data(query_handler)
        recommendations_table.grant_read_data(query_handler)
        alerts_table.grant_read_data(query_handler)
        conversations_table.grant_read_write_data(query_handler)
        data_bucket.grant_read(query_handler)
        
        # Grant Bedrock permissions
        query_handler.add_to_role_policy(
            iam.PolicyStatement(
                actions=["bedrock:InvokeModel"],
                resources=["*"]
            )
        )
        
        # ====================================================================
        # API Gateway
        # ====================================================================
        
        api = apigateway.RestApi(
            self, "RetailBrainAPI",
            rest_api_name="RetailBrain API",
            description="API for RetailBrain Copilot",
            default_cors_preflight_options=apigateway.CorsOptions(
                allow_origins=apigateway.Cors.ALL_ORIGINS,
                allow_methods=apigateway.Cors.ALL_METHODS,
                allow_headers=["Content-Type", "Authorization"]
            )
        )
        
        # Cognito Authorizer
        authorizer = apigateway.CognitoUserPoolsAuthorizer(
            self, "CognitoAuthorizer",
            cognito_user_pools=[user_pool]
        )
        
        # API Resources
        api_v1 = api.root.add_resource("api").add_resource("v1")
        
        # POST /api/v1/query
        query_resource = api_v1.add_resource("query")
        query_resource.add_method(
            "POST",
            apigateway.LambdaIntegration(query_handler),
            authorizer=authorizer,
            authorization_type=apigateway.AuthorizationType.COGNITO
        )
        
        # GET /api/v1/forecasts/{sku}
        forecasts_resource = api_v1.add_resource("forecasts").add_resource("{sku}")
        forecasts_resource.add_method(
            "GET",
            apigateway.LambdaIntegration(query_handler),
            authorizer=authorizer,
            authorization_type=apigateway.AuthorizationType.COGNITO
        )
        
        # GET /api/v1/recommendations
        recommendations_resource = api_v1.add_resource("recommendations")
        recommendations_resource.add_method(
            "GET",
            apigateway.LambdaIntegration(query_handler),
            authorizer=authorizer,
            authorization_type=apigateway.AuthorizationType.COGNITO
        )
        
        # GET /api/v1/alerts
        alerts_resource = api_v1.add_resource("alerts")
        alerts_resource.add_method(
            "GET",
            apigateway.LambdaIntegration(query_handler),
            authorizer=authorizer,
            authorization_type=apigateway.AuthorizationType.COGNITO
        )
        
        # ====================================================================
        # Outputs
        # ====================================================================
        
        from aws_cdk import CfnOutput
        
        CfnOutput(self, "UserPoolId", value=user_pool.user_pool_id)
        CfnOutput(self, "UserPoolClientId", value=user_pool_client.user_pool_client_id)
        CfnOutput(self, "ApiUrl", value=api.url)
        CfnOutput(self, "DataBucketName", value=data_bucket.bucket_name)


# CDK App
app = App()
RetailBrainStack(app, "RetailBrainStack")
app.synth()
