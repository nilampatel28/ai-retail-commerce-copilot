#!/usr/bin/env python3
"""
Load sample data into DynamoDB tables
Run this after CDK deployment to populate tables with demo data
"""

import boto3
import pandas as pd
import json
from datetime import datetime, timedelta
from decimal import Decimal
import sys

print("🚀 Loading data into DynamoDB...")

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

def convert_float_to_decimal(obj):
    """Convert float to Decimal for DynamoDB"""
    if isinstance(obj, float):
        return Decimal(str(obj))
    return obj

try:
    # ========================================================================
    # 1. Load Forecasts
    # ========================================================================
    print("\n1️⃣  Loading forecasts...")
    forecasts_table = dynamodb.Table('RetailBrain-Forecasts')
    forecasts_df = pd.read_csv('data/forecasts.csv')
    
    with forecasts_table.batch_writer() as batch:
        for idx, row in forecasts_df.iterrows():
            # Add TTL (90 days from now)
            ttl = int((datetime.now() + timedelta(days=90)).timestamp())
            
            batch.put_item(Item={
                'sku': str(row['sku']),
                'forecast_date': str(row['forecast_date']),
                'location': str(row['location']),
                'forecasted_demand': convert_float_to_decimal(row['forecasted_demand']),
                'confidence_p10': convert_float_to_decimal(row['confidence_p10']),
                'confidence_p50': convert_float_to_decimal(row['confidence_p50']),
                'confidence_p90': convert_float_to_decimal(row['confidence_p90']),
                'confidence_score': convert_float_to_decimal(row['confidence_score']),
                'model_version': str(row['model_version']),
                'generated_at': str(row['generated_at']),
                'ttl': ttl
            })
            
            if (idx + 1) % 100 == 0:
                print(f"   Loaded {idx + 1}/{len(forecasts_df)} forecasts...")
    
    print(f"   ✅ Loaded {len(forecasts_df)} forecasts")
    
    # ========================================================================
    # 2. Load Recommendations
    # ========================================================================
    print("\n2️⃣  Loading recommendations...")
    recommendations_table = dynamodb.Table('RetailBrain-Recommendations')
    recommendations_df = pd.read_csv('data/recommendations.csv')
    
    with recommendations_table.batch_writer() as batch:
        for idx, row in recommendations_df.iterrows():
            batch.put_item(Item={
                'recommendation_id': str(row['recommendation_id']),
                'sku': str(row['sku']),
                'type': str(row['type']),
                'current_price': convert_float_to_decimal(row['current_price']),
                'recommended_price': convert_float_to_decimal(row['recommended_price']),
                'price_change_percent': convert_float_to_decimal(row['price_change_percent']),
                'confidence_score': convert_float_to_decimal(row['confidence_score']),
                'estimated_revenue_impact': convert_float_to_decimal(row['estimated_revenue_impact']),
                'estimated_margin_impact': convert_float_to_decimal(row['estimated_margin_impact']),
                'explanation': str(row['explanation']),
                'top_factors': str(row['top_factors']),
                'status': str(row['status']),
                'created_at': str(row['created_at'])
            })
    
    print(f"   ✅ Loaded {len(recommendations_df)} recommendations")
    
    # ========================================================================
    # 3. Load Alerts
    # ========================================================================
    print("\n3️⃣  Loading alerts...")
    alerts_table = dynamodb.Table('RetailBrain-Alerts')
    alerts_df = pd.read_csv('data/alerts.csv')
    
    with alerts_table.batch_writer() as batch:
        for idx, row in alerts_df.iterrows():
            # Add TTL (30 days from now)
            ttl = int((datetime.now() + timedelta(days=30)).timestamp())
            
            item = {
                'alert_id': str(row['alert_id']),
                'type': str(row['type']),
                'severity': str(row['severity']),
                'sku': str(row['sku']),
                'location': str(row['location']),
                'current_inventory': int(row['current_inventory']),
                'days_of_supply': convert_float_to_decimal(row['days_of_supply']),
                'recommended_action': str(row['recommended_action']),
                'created_at': str(row['created_at']),
                'status': str(row['status']),
                'ttl': ttl
            }
            
            # Add type-specific fields
            if row['type'] == 'stockout_risk':
                item['estimated_stockout_date'] = str(row['estimated_stockout_date'])
            elif row['type'] == 'overstock':
                item['excess_quantity'] = int(row['excess_quantity'])
                item['carrying_cost_monthly'] = convert_float_to_decimal(row['carrying_cost_monthly'])
            
            batch.put_item(Item=item)
    
    print(f"   ✅ Loaded {len(alerts_df)} alerts")
    
    # ========================================================================
    # Summary
    # ========================================================================
    print("\n" + "="*70)
    print("✅ DATA LOADING COMPLETE!")
    print("="*70)
    print(f"\n📊 Summary:")
    print(f"   • Forecasts: {len(forecasts_df):,} records")
    print(f"   • Recommendations: {len(recommendations_df)} records")
    print(f"   • Alerts: {len(alerts_df)} records")
    print(f"\n🎯 Next Steps:")
    print(f"   1. Test API endpoints")
    print(f"   2. Create Cognito test user")
    print(f"   3. Deploy frontend")
    print("\n" + "="*70 + "\n")
    
except Exception as e:
    print(f"\n❌ Error loading data: {str(e)}")
    print(f"\nMake sure:")
    print(f"   1. CDK stack is deployed")
    print(f"   2. DynamoDB tables exist")
    print(f"   3. AWS credentials are configured")
    print(f"   4. You're in the project root directory")
    sys.exit(1)
