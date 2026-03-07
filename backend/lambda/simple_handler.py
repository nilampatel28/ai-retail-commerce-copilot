import json
import boto3
import os
from decimal import Decimal

dynamodb = boto3.resource('dynamodb')

class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)

def lambda_handler(event, context):
    try:
        body = json.loads(event.get('body', '{}'))
        query = body.get('query', '').lower()
        
        # Simple pattern matching
        if 'sku-001' in query or 'sku 001' in query:
            table = dynamodb.Table(os.environ['FORECASTS_TABLE'])
            response = table.query(
                KeyConditionExpression='sku = :sku',
                ExpressionAttributeValues={':sku': 'SKU-001'},
                Limit=7
            )
            items = response.get('Items', [])
            if items:
                total = sum(float(i['forecasted_demand']) for i in items)
                answer = f"📊 Forecast for SKU-001:\n\nNext 7 days total: {total:.0f} units\nDaily average: {total/7:.1f} units/day\n\n💡 Maintain {total*1.2:.0f} units in stock (includes 20% safety buffer)"
            else:
                answer = "No forecast data found for SKU-001"
                
        elif 'stockout' in query or 'alert' in query or 'risk' in query:
            table = dynamodb.Table(os.environ['ALERTS_TABLE'])
            response = table.scan(Limit=50)
            items = response.get('Items', [])
            stockout = [i for i in items if i.get('type') == 'stockout_risk']
            answer = f"🚨 Found {len(stockout)} SKUs at risk of stockout\n\nHigh priority items need immediate attention. Check dashboard for details."
            
        elif 'price' in query or 'pricing' in query:
            table = dynamodb.Table(os.environ['RECOMMENDATIONS_TABLE'])
            response = table.scan(Limit=20)
            items = response.get('Items', [])
            answer = f"💰 Found {len(items)} pricing recommendations\n\nTotal revenue opportunity: ${sum(float(i.get('estimated_revenue_impact', 0)) for i in items):,.0f}"
            
        else:
            answer = "👋 Try asking:\n• What is the forecast for SKU-001?\n• Which SKUs are at risk of stockout?\n• Show me pricing recommendations"
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type,Authorization',
                'Access-Control-Allow-Methods': 'GET,POST,OPTIONS'
            },
            'body': json.dumps({'answer': answer}, cls=DecimalEncoder)
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': str(e)})
        }
