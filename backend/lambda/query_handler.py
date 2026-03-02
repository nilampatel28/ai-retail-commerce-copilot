"""
Query Handler Lambda Function
Processes natural language queries using Amazon Bedrock and routes to appropriate services.
"""

import json
import boto3
import os
from datetime import datetime
from typing import Dict, Any, List

# Initialize AWS clients
bedrock_runtime = boto3.client('bedrock-runtime', region_name=os.environ.get('AWS_REGION', 'us-east-1'))
dynamodb = boto3.resource('dynamodb', region_name=os.environ.get('AWS_REGION', 'us-east-1'))

# DynamoDB tables
FORECASTS_TABLE = os.environ.get('FORECASTS_TABLE', 'RetailBrain-Forecasts')
RECOMMENDATIONS_TABLE = os.environ.get('RECOMMENDATIONS_TABLE', 'RetailBrain-Recommendations')
ALERTS_TABLE = os.environ.get('ALERTS_TABLE', 'RetailBrain-Alerts')
CONVERSATION_TABLE = os.environ.get('CONVERSATION_TABLE', 'RetailBrain-Conversations')

# Bedrock model ID
BEDROCK_MODEL_ID = 'anthropic.claude-3-sonnet-20240229-v1:0'


def extract_intent_with_bedrock(query: str, user_context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Use Bedrock to extract intent and entities from natural language query.
    """
    
    prompt = f"""You are an AI assistant for a retail decision support system. 
    
User Role: {user_context.get('role', 'unknown')}
Query: {query}

Extract the following from the query:
1. Intent: One of [forecast, pricing, inventory, performance, explanation, simulation, alert]
2. Entities: SKU, location, time period, or other relevant entities
3. Missing entities: What information is needed to answer the query?

Respond in JSON format:
{{
    "intent": "forecast|pricing|inventory|performance|explanation|simulation|alert",
    "entities": {{
        "sku": "SKU-XXX or null",
        "location": "Store-XXX or null",
        "time_period": "next week|next month|etc or null"
    }},
    "missing_entities": ["list of missing required entities"],
    "clarifying_question": "Question to ask if entities are missing, or null"
}}

Examples:
Query: "What's the demand forecast for SKU-001 next week?"
Response: {{"intent": "forecast", "entities": {{"sku": "SKU-001", "time_period": "next week"}}, "missing_entities": [], "clarifying_question": null}}

Query: "What price should I set?"
Response: {{"intent": "pricing", "entities": {{}}, "missing_entities": ["sku"], "clarifying_question": "Which SKU would you like pricing recommendations for?"}}

Now process the user's query."""

    try:
        # Call Bedrock Claude 3 Sonnet
        response = bedrock_runtime.invoke_model(
            modelId=BEDROCK_MODEL_ID,
            body=json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 500,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            })
        )
        
        response_body = json.loads(response['body'].read())
        content = response_body['content'][0]['text']
        
        # Extract JSON from response
        start_idx = content.find('{')
        end_idx = content.rfind('}') + 1
        json_str = content[start_idx:end_idx]
        
        intent_data = json.loads(json_str)
        return intent_data
        
    except Exception as e:
        print(f"Error calling Bedrock: {str(e)}")
        return {
            "intent": "unknown",
            "entities": {},
            "missing_entities": [],
            "clarifying_question": None,
            "error": str(e)
        }


def get_forecast_data(sku: str, location: str = None) -> Dict[str, Any]:
    """
    Retrieve forecast data from DynamoDB.
    """
    table = dynamodb.Table(FORECASTS_TABLE)
    
    try:
        # Query forecasts for SKU
        response = table.query(
            KeyConditionExpression='sku = :sku',
            ExpressionAttributeValues={':sku': sku},
            Limit=30  # Next 30 days
        )
        
        forecasts = response.get('Items', [])
        
        if not forecasts:
            return {"error": f"No forecast data found for {sku}"}
        
        # Calculate summary statistics
        total_demand = sum(f['forecasted_demand'] for f in forecasts)
        avg_confidence = sum(f['confidence_score'] for f in forecasts) / len(forecasts)
        
        return {
            "sku": sku,
            "forecast_period": "30 days",
            "total_forecasted_demand": round(total_demand, 2),
            "avg_daily_demand": round(total_demand / 30, 2),
            "avg_confidence": round(avg_confidence, 2),
            "daily_forecasts": forecasts[:7]  # Return first 7 days for display
        }
        
    except Exception as e:
        print(f"Error querying forecasts: {str(e)}")
        return {"error": str(e)}


def get_pricing_recommendations(sku: str = None) -> Dict[str, Any]:
    """
    Retrieve pricing recommendations from DynamoDB.
    """
    table = dynamodb.Table(RECOMMENDATIONS_TABLE)
    
    try:
        if sku:
            # Query recommendations for specific SKU
            response = table.query(
                IndexName='SKUIndex',
                KeyConditionExpression='sku = :sku',
                ExpressionAttributeValues={':sku': sku},
                FilterExpression='#status = :status',
                ExpressionAttributeNames={'#status': 'status'},
                ExpressionAttributeValues={':status': 'pending'}
            )
        else:
            # Scan for all pending recommendations
            response = table.scan(
                FilterExpression='#status = :status',
                ExpressionAttributeNames={'#status': 'status'},
                ExpressionAttributeValues={':status': 'pending'},
                Limit=10
            )
        
        recommendations = response.get('Items', [])
        
        if not recommendations:
            return {"error": f"No pricing recommendations found{' for ' + sku if sku else ''}"}
        
        return {
            "recommendations": recommendations,
            "count": len(recommendations)
        }
        
    except Exception as e:
        print(f"Error querying recommendations: {str(e)}")
        return {"error": str(e)}


def get_alerts(alert_type: str = None, severity: str = None) -> Dict[str, Any]:
    """
    Retrieve alerts from DynamoDB.
    """
    table = dynamodb.Table(ALERTS_TABLE)
    
    try:
        # Build filter expression
        filter_expressions = []
        expression_values = {}
        
        if alert_type:
            filter_expressions.append('#type = :type')
            expression_values[':type'] = alert_type
        
        if severity:
            filter_expressions.append('severity = :severity')
            expression_values[':severity'] = severity
        
        filter_expressions.append('#status = :status')
        expression_values[':status'] = 'active'
        
        scan_kwargs = {
            'FilterExpression': ' AND '.join(filter_expressions),
            'ExpressionAttributeValues': expression_values,
            'Limit': 50
        }
        
        if alert_type:
            scan_kwargs['ExpressionAttributeNames'] = {'#type': 'type', '#status': 'status'}
        else:
            scan_kwargs['ExpressionAttributeNames'] = {'#status': 'status'}
        
        response = table.scan(**scan_kwargs)
        
        alerts = response.get('Items', [])
        
        # Group by type
        stockout_alerts = [a for a in alerts if a.get('type') == 'stockout_risk']
        overstock_alerts = [a for a in alerts if a.get('type') == 'overstock']
        
        return {
            "alerts": alerts,
            "total_count": len(alerts),
            "stockout_count": len(stockout_alerts),
            "overstock_count": len(overstock_alerts)
        }
        
    except Exception as e:
        print(f"Error querying alerts: {str(e)}")
        return {"error": str(e)}


def generate_response_with_bedrock(query: str, data: Dict[str, Any], user_context: Dict[str, Any]) -> str:
    """
    Generate natural language response using Bedrock.
    """
    
    role_context = {
        'merchandiser': 'Focus on assortment decisions and SKU performance insights.',
        'planner': 'Focus on demand forecasts and inventory optimization insights.',
        'seller': 'Focus on pricing recommendations and promotional effectiveness insights.'
    }
    
    role_instruction = role_context.get(user_context.get('role', 'planner'), '')
    
    prompt = f"""You are an AI retail assistant. Generate a clear, concise response to the user's query.

User Role: {user_context.get('role', 'unknown')}
Role Context: {role_instruction}

User Query: {query}

Data Retrieved:
{json.dumps(data, indent=2)}

Generate a natural language response that:
1. Directly answers the user's question
2. Highlights key insights relevant to their role
3. Includes specific numbers and metrics
4. Suggests actionable next steps if appropriate
5. Is conversational and easy to understand

Response:"""

    try:
        response = bedrock_runtime.invoke_model(
            modelId=BEDROCK_MODEL_ID,
            body=json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 1000,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            })
        )
        
        response_body = json.loads(response['body'].read())
        answer = response_body['content'][0]['text']
        
        return answer.strip()
        
    except Exception as e:
        print(f"Error generating response: {str(e)}")
        return f"I found the data you requested, but encountered an error generating the response: {str(e)}"


def lambda_handler(event, context):
    """
    Main Lambda handler for query processing.
    """
    
    try:
        # Parse request body
        body = json.loads(event.get('body', '{}'))
        query = body.get('query', '')
        user_id = body.get('userId', 'anonymous')
        session_id = body.get('sessionId', 'default')
        
        if not query:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'error': 'Query is required'})
            }
        
        # Get user context (role, permissions)
        user_context = {
            'user_id': user_id,
            'role': body.get('role', 'planner'),  # Default to planner
            'session_id': session_id
        }
        
        # Step 1: Extract intent and entities using Bedrock
        intent_data = extract_intent_with_bedrock(query, user_context)
        
        # Step 2: Check if clarification is needed
        if intent_data.get('clarifying_question'):
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'answer': intent_data['clarifying_question'],
                    'needs_clarification': True,
                    'intent': intent_data.get('intent'),
                    'missing_entities': intent_data.get('missing_entities', [])
                })
            }
        
        # Step 3: Route to appropriate data source based on intent
        intent = intent_data.get('intent')
        entities = intent_data.get('entities', {})
        
        if intent == 'forecast':
            sku = entities.get('sku')
            location = entities.get('location')
            data = get_forecast_data(sku, location)
            
        elif intent == 'pricing':
            sku = entities.get('sku')
            data = get_pricing_recommendations(sku)
            
        elif intent == 'alert' or intent == 'inventory':
            alert_type = 'stockout_risk' if 'stockout' in query.lower() else None
            severity = 'high' if 'high' in query.lower() else None
            data = get_alerts(alert_type, severity)
            
        else:
            data = {"message": "I understand your query, but this feature is not yet implemented."}
        
        # Step 4: Generate natural language response
        answer = generate_response_with_bedrock(query, data, user_context)
        
        # Step 5: Store conversation history
        # TODO: Implement conversation history storage
        
        # Step 6: Return response
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'answer': answer,
                'intent': intent,
                'entities': entities,
                'data': data,
                'confidence': intent_data.get('confidence', 0.85),
                'timestamp': datetime.now().isoformat()
            })
        }
        
    except Exception as e:
        print(f"Error in lambda_handler: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': 'Internal server error',
                'message': str(e)
            })
        }
