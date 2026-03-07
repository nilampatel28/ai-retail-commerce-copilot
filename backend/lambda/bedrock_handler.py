"""
Enhanced Query Handler with Amazon Bedrock Integration
Processes natural language queries using Claude 3 models
"""

import json
import boto3
import os
from decimal import Decimal
from datetime import datetime
from typing import Dict, Any, List, Optional

# Initialize AWS clients
dynamodb = boto3.resource('dynamodb')
bedrock_runtime = boto3.client('bedrock-runtime')

# DynamoDB table names
FORECASTS_TABLE = os.environ.get('FORECASTS_TABLE', 'RetailBrain-Forecasts')
RECOMMENDATIONS_TABLE = os.environ.get('RECOMMENDATIONS_TABLE', 'RetailBrain-Recommendations')
ALERTS_TABLE = os.environ.get('ALERTS_TABLE', 'RetailBrain-Alerts')

# Bedrock model configuration
BEDROCK_MODEL_ID = 'anthropic.claude-3-haiku-20240307-v1:0'


class DecimalEncoder(json.JSONEncoder):
    """JSON encoder for Decimal types from DynamoDB"""
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)


def extract_intent_with_bedrock(query: str) -> Dict[str, Any]:
    """
    Use Amazon Bedrock Claude to extract intent and entities from query
    """
    prompt = f"""Analyze this retail query and extract structured information.

Query: "{query}"

Identify:
1. Intent: forecast, pricing, inventory, alert, or general
2. SKU: Extract any SKU mentioned (format: SKU-XXX)
3. Action: What the user wants to know

Respond in JSON format:
{{
    "intent": "forecast|pricing|inventory|alert|general",
    "sku": "SKU-XXX or null",
    "action": "brief description"
}}

Examples:
Query: "What is the demand forecast for SKU-001?"
{{"intent": "forecast", "sku": "SKU-001", "action": "get demand forecast"}}

Query: "Show me pricing recommendations"
{{"intent": "pricing", "sku": null, "action": "list pricing recommendations"}}

Query: "Which SKUs are at risk?"
{{"intent": "alert", "sku": null, "action": "list stockout risks"}}"""

    try:
        response = bedrock_runtime.invoke_model(
            modelId=BEDROCK_MODEL_ID,
            body=json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 300,
                "messages": [{
                    "role": "user",
                    "content": prompt
                }],
                "temperature": 0.1
            })
        )
        
        response_body = json.loads(response['body'].read())
        content = response_body['content'][0]['text']
        
        # Extract JSON from response
        start_idx = content.find('{')
        end_idx = content.rfind('}') + 1
        if start_idx >= 0 and end_idx > start_idx:
            json_str = content[start_idx:end_idx]
            intent_data = json.loads(json_str)
            
            # Clean up SKU if present
            if intent_data.get('sku'):
                sku = intent_data['sku']
                # Remove punctuation except hyphen
                sku = ''.join(c for c in sku if c.isalnum() or c == '-')
                intent_data['sku'] = sku
            
            return intent_data
        
        return {"intent": "general", "sku": None, "action": "unknown"}
        
    except Exception as e:
        print(f"Bedrock intent extraction error: {str(e)}")
        # Fallback to simple pattern matching
        return extract_intent_fallback(query)


def extract_intent_fallback(query: str) -> Dict[str, Any]:
    """Fallback intent extraction using pattern matching"""
    query_lower = query.lower()
    
    # Extract SKU - clean up any punctuation
    sku = None
    if 'sku-' in query_lower or 'sku ' in query_lower:
        parts = query.upper().split()
        for part in parts:
            if part.startswith('SKU-') or part.startswith('SKU'):
                # Clean up punctuation
                sku = part.replace('SKU', 'SKU-').replace('--', '-')
                sku = ''.join(c for c in sku if c.isalnum() or c == '-')
                break
    
    # Determine intent
    if 'forecast' in query_lower or 'demand' in query_lower:
        intent = 'forecast'
    elif 'price' in query_lower or 'pricing' in query_lower:
        intent = 'pricing'
    elif 'stockout' in query_lower or 'alert' in query_lower or 'risk' in query_lower:
        intent = 'alert'
    elif 'inventory' in query_lower or 'stock' in query_lower:
        intent = 'inventory'
    else:
        intent = 'general'
    
    return {"intent": intent, "sku": sku, "action": "process query"}


def get_forecast_data(sku: str) -> Dict[str, Any]:
    """Retrieve forecast data from DynamoDB"""
    try:
        table = dynamodb.Table(FORECASTS_TABLE)
        response = table.query(
            KeyConditionExpression='sku = :sku',
            ExpressionAttributeValues={':sku': sku},
            Limit=30
        )
        
        items = response.get('Items', [])
        if not items:
            return {"error": f"No forecast data found for {sku}"}
        
        # Calculate metrics
        total_demand = sum(float(i['forecasted_demand']) for i in items)
        avg_confidence = sum(float(i.get('confidence_score', 0.85)) for i in items) / len(items)
        
        return {
            "sku": sku,
            "total_forecasted_demand": round(total_demand, 2),
            "avg_daily_demand": round(total_demand / len(items), 2),
            "forecast_days": len(items),
            "avg_confidence": round(avg_confidence, 2),
            "daily_forecasts": items[:7]
        }
    except Exception as e:
        print(f"Error querying forecasts: {str(e)}")
        return {"error": str(e)}


def get_pricing_recommendations(sku: Optional[str] = None) -> Dict[str, Any]:
    """Retrieve pricing recommendations from DynamoDB"""
    try:
        table = dynamodb.Table(RECOMMENDATIONS_TABLE)
        
        if sku:
            response = table.scan(
                FilterExpression='sku = :sku',
                ExpressionAttributeValues={':sku': sku},
                Limit=10
            )
        else:
            response = table.scan(Limit=20)
        
        items = response.get('Items', [])
        if not items:
            return {"error": f"No pricing recommendations found{' for ' + sku if sku else ''}"}
        
        total_revenue_impact = sum(float(i.get('estimated_revenue_impact', 0)) for i in items)
        
        return {
            "recommendations": items,
            "count": len(items),
            "total_revenue_impact": round(total_revenue_impact, 2)
        }
    except Exception as e:
        print(f"Error querying recommendations: {str(e)}")
        return {"error": str(e)}


def get_alerts(alert_type: Optional[str] = None) -> Dict[str, Any]:
    """Retrieve alerts from DynamoDB"""
    try:
        table = dynamodb.Table(ALERTS_TABLE)
        response = table.scan(Limit=50)
        
        items = response.get('Items', [])
        
        # Filter by type if specified
        if alert_type:
            items = [i for i in items if i.get('type') == alert_type]
        
        # Group by type
        stockout_alerts = [i for i in items if i.get('type') == 'stockout_risk']
        overstock_alerts = [i for i in items if i.get('type') == 'overstock']
        
        return {
            "alerts": items,
            "total_count": len(items),
            "stockout_count": len(stockout_alerts),
            "overstock_count": len(overstock_alerts)
        }
    except Exception as e:
        print(f"Error querying alerts: {str(e)}")
        return {"error": str(e)}


def generate_response_with_bedrock(query: str, intent_data: Dict[str, Any], data: Dict[str, Any]) -> str:
    """
    Generate natural language response using Amazon Bedrock Claude
    """
    # Prepare context for Claude
    context = f"""You are RetailBrain AI, an intelligent retail assistant.

User Query: "{query}"
Intent: {intent_data.get('intent')}
Data Retrieved: {json.dumps(data, indent=2, cls=DecimalEncoder)}

Generate a clear, professional response that:
1. Directly answers the user's question
2. Highlights key metrics and insights
3. Uses emojis sparingly for visual clarity
4. Provides actionable recommendations
5. Is concise (2-4 sentences max)

Response:"""

    try:
        response = bedrock_runtime.invoke_model(
            modelId=BEDROCK_MODEL_ID,
            body=json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 500,
                "messages": [{
                    "role": "user",
                    "content": context
                }],
                "temperature": 0.7
            })
        )
        
        response_body = json.loads(response['body'].read())
        answer = response_body['content'][0]['text'].strip()
        
        return answer
        
    except Exception as e:
        print(f"Bedrock response generation error: {str(e)}")
        # Fallback to template-based response
        return generate_response_fallback(intent_data, data)


def generate_response_fallback(intent_data: Dict[str, Any], data: Dict[str, Any]) -> str:
    """Fallback response generation without Bedrock"""
    
    if 'error' in data:
        return f"❌ {data['error']}"
    
    intent = intent_data.get('intent')
    
    if intent == 'forecast' and 'total_forecasted_demand' in data:
        return f"""📊 Forecast for {data['sku']}:

Next {data['forecast_days']} days: {data['total_forecasted_demand']:.0f} units total
Daily average: {data['avg_daily_demand']:.1f} units/day
Confidence: {data['avg_confidence']*100:.0f}%

💡 Maintain {data['avg_daily_demand']*7*1.2:.0f} units in stock (includes 20% safety buffer)"""
    
    elif intent == 'pricing' and 'recommendations' in data:
        return f"""💰 Found {data['count']} pricing recommendations

Total revenue opportunity: ${data['total_revenue_impact']:,.0f}

These recommendations optimize for revenue while maintaining competitive positioning. Review details in the dashboard."""
    
    elif intent == 'alert' and 'alerts' in data:
        return f"""🚨 Active Alerts Summary:

• {data['stockout_count']} SKUs at risk of stockout
• {data['overstock_count']} SKUs with overstock
• {data['total_count']} total active alerts

High-priority items need immediate attention. Check dashboard for details."""
    
    return "✅ Query processed. Check the dashboard for detailed information."


def lambda_handler(event, context):
    """
    Main Lambda handler with Amazon Bedrock integration
    """
    try:
        # Parse request
        body = json.loads(event.get('body', '{}'))
        query = body.get('query', '').strip()
        
        if not query:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type,Authorization',
                    'Access-Control-Allow-Methods': 'GET,POST,OPTIONS'
                },
                'body': json.dumps({'error': 'Query is required'})
            }
        
        # Step 1: Extract intent using Bedrock
        intent_data = extract_intent_with_bedrock(query)
        intent = intent_data.get('intent')
        sku = intent_data.get('sku')
        
        # Step 2: Retrieve data based on intent
        if intent == 'forecast' and sku:
            data = get_forecast_data(sku)
        elif intent == 'pricing':
            data = get_pricing_recommendations(sku)
        elif intent == 'alert' or intent == 'inventory':
            data = get_alerts('stockout_risk' if 'stockout' in query.lower() else None)
        elif intent == 'general':
            data = {
                "message": "I can help you with demand forecasts, pricing recommendations, and inventory alerts.",
                "examples": [
                    "What is the forecast for SKU-001?",
                    "Show me pricing recommendations",
                    "Which SKUs are at risk of stockout?"
                ]
            }
        else:
            data = {"error": "I couldn't understand your query. Please try rephrasing."}
        
        # Step 3: Generate response using Bedrock
        answer = generate_response_with_bedrock(query, intent_data, data)
        
        # Step 4: Return response
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type,Authorization',
                'Access-Control-Allow-Methods': 'GET,POST,OPTIONS'
            },
            'body': json.dumps({
                'answer': answer,
                'intent': intent,
                'sku': sku,
                'timestamp': datetime.now().isoformat(),
                'powered_by': 'Amazon Bedrock Claude 3'
            }, cls=DecimalEncoder)
        }
        
    except Exception as e:
        print(f"Lambda handler error: {str(e)}")
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
