#!/usr/bin/env python3
"""
Quick data loader - loads minimal data for demo
"""

import boto3
import csv
from decimal import Decimal

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

def load_forecasts():
    """Load first 100 forecasts"""
    table = dynamodb.Table('RetailBrain-Forecasts')
    
    print("Loading forecasts...")
    with open('data/forecasts.csv', 'r') as f:
        reader = csv.DictReader(f)
        count = 0
        with table.batch_writer() as batch:
            for row in reader:
                if count >= 100:
                    break
                batch.put_item(Item={
                    'sku': row['sku'],
                    'forecast_date': row['forecast_date'],
                    'forecasted_demand': Decimal(str(row['forecasted_demand'])),
                    'confidence_score': Decimal(str(row['confidence_score']))
                })
                count += 1
    print(f"✓ Loaded {count} forecasts")

def load_recommendations():
    """Load all recommendations"""
    table = dynamodb.Table('RetailBrain-Recommendations')
    
    print("Loading recommendations...")
    with open('data/recommendations.csv', 'r') as f:
        reader = csv.DictReader(f)
        count = 0
        with table.batch_writer() as batch:
            for row in reader:
                batch.put_item(Item={
                    'recommendation_id': row['recommendation_id'],
                    'sku': row['sku'],
                    'created_at': row['created_at'],
                    'type': row['type'],
                    'current_price': Decimal(str(row['current_price'])),
                    'recommended_price': Decimal(str(row['recommended_price'])),
                    'estimated_revenue_impact': Decimal(str(row['estimated_revenue_impact'])),
                    'confidence_score': Decimal(str(row['confidence_score'])),
                    'status': row['status']
                })
                count += 1
    print(f"✓ Loaded {count} recommendations")

def load_alerts():
    """Load all alerts"""
    table = dynamodb.Table('RetailBrain-Alerts')
    
    print("Loading alerts...")
    with open('data/alerts.csv', 'r') as f:
        reader = csv.DictReader(f)
        count = 0
        with table.batch_writer() as batch:
            for row in reader:
                item = {
                    'alert_id': row['alert_id'],
                    'sku': row['sku'],
                    'created_at': row['created_at'],
                    'type': row['type'],
                    'severity': row['severity'],
                    'current_inventory': Decimal(str(row['current_inventory'])),
                    'days_of_supply': Decimal(str(row['days_of_supply'])),
                    'status': row['status']
                }
                # Add optional fields if present
                if row.get('recommended_action'):
                    item['recommended_action'] = row['recommended_action']
                if row.get('estimated_stockout_date'):
                    item['estimated_stockout_date'] = row['estimated_stockout_date']
                
                batch.put_item(Item=item)
                count += 1
    print(f"✓ Loaded {count} alerts")

if __name__ == '__main__':
    print("Quick Data Loader - Loading minimal demo data")
    print("=" * 50)
    load_forecasts()
    load_recommendations()
    load_alerts()
    print("=" * 50)
    print("✅ Data loading complete!")
