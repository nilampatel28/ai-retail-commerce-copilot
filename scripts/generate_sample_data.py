#!/usr/bin/env python3
"""
Generate realistic sample retail data for RetailBrain Copilot demo.
Creates sales, inventory, pricing, and product data for 50 SKUs across 5 locations.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import random

# Set random seed for reproducibility
np.random.seed(42)
random.seed(42)

# Configuration
NUM_SKUS = 50
NUM_LOCATIONS = 5
DAYS_HISTORY = 90
START_DATE = datetime.now() - timedelta(days=DAYS_HISTORY)

# Product categories with different demand patterns
CATEGORIES = {
    'Electronics': {'base_demand': 50, 'seasonality': 1.3, 'margin': 0.25},
    'Clothing': {'base_demand': 80, 'seasonality': 1.5, 'margin': 0.40},
    'Food': {'base_demand': 150, 'seasonality': 1.1, 'margin': 0.15},
    'Home': {'base_demand': 40, 'seasonality': 1.2, 'margin': 0.30},
    'Beauty': {'base_demand': 60, 'seasonality': 1.15, 'margin': 0.35},
}

LOCATIONS = ['Store-NYC', 'Store-LA', 'Store-CHI', 'Store-HOU', 'Store-PHX']

print("🚀 Generating RetailBrain Copilot Sample Data...")
print(f"📊 Configuration: {NUM_SKUS} SKUs, {NUM_LOCATIONS} locations, {DAYS_HISTORY} days")

# ============================================================================
# 1. Generate Product Catalog
# ============================================================================
print("\n1️⃣  Generating product catalog...")

products = []
for i in range(1, NUM_SKUS + 1):
    sku_id = f"SKU-{i:03d}"
    category = random.choice(list(CATEGORIES.keys()))
    cat_config = CATEGORIES[category]
    
    base_price = random.uniform(10, 200)
    cost = base_price * (1 - cat_config['margin'])
    
    product = {
        'sku': sku_id,
        'name': f"{category} Product {i}",
        'category': category,
        'base_price': round(base_price, 2),
        'cost': round(cost, 2),
        'margin_percent': round(cat_config['margin'] * 100, 1),
        'supplier': f"Supplier-{random.randint(1, 10)}",
        'lead_time_days': random.randint(3, 14)
    }
    products.append(product)

products_df = pd.DataFrame(products)
products_df.to_csv('data/products.csv', index=False)
print(f"   ✅ Created {len(products_df)} products")

# ============================================================================
# 2. Generate Historical Sales Data
# ============================================================================
print("\n2️⃣  Generating historical sales data...")

sales_records = []
for sku_data in products:
    sku = sku_data['sku']
    category = sku_data['category']
    base_price = sku_data['base_price']
    cat_config = CATEGORIES[category]
    
    for location in LOCATIONS:
        # Location-specific demand multiplier
        location_multiplier = random.uniform(0.7, 1.3)
        
        for day in range(DAYS_HISTORY):
            date = START_DATE + timedelta(days=day)
            
            # Demand components
            base_demand = cat_config['base_demand'] * location_multiplier
            
            # Seasonality (weekly pattern + trend)
            day_of_week = date.weekday()
            weekly_factor = 1.2 if day_of_week in [5, 6] else 0.9  # Weekend boost
            
            # Monthly trend (some products growing, some declining)
            trend_factor = 1 + (day / DAYS_HISTORY) * random.uniform(-0.3, 0.5)
            
            # Random noise
            noise = random.uniform(0.8, 1.2)
            
            # Calculate demand
            demand = base_demand * weekly_factor * trend_factor * noise
            quantity = max(0, int(np.random.poisson(demand)))
            
            # Price variations (promotions)
            is_promotion = random.random() < 0.15  # 15% chance of promotion
            if is_promotion:
                discount = random.uniform(0.1, 0.3)
                price = base_price * (1 - discount)
                promotion_type = random.choice(['BOGO', 'Discount', 'Clearance'])
            else:
                price = base_price * random.uniform(0.95, 1.05)  # Small variations
                promotion_type = None
            
            if quantity > 0:  # Only record if there were sales
                sales_records.append({
                    'date': date.strftime('%Y-%m-%d'),
                    'sku': sku,
                    'location': location,
                    'quantity': quantity,
                    'price': round(price, 2),
                    'revenue': round(quantity * price, 2),
                    'is_promotion': is_promotion,
                    'promotion_type': promotion_type,
                    'day_of_week': date.strftime('%A'),
                    'week_of_year': date.isocalendar()[1]
                })

sales_df = pd.DataFrame(sales_records)
sales_df.to_csv('data/sales_history.csv', index=False)
print(f"   ✅ Created {len(sales_df):,} sales transactions")

# ============================================================================
# 3. Generate Current Inventory Levels
# ============================================================================
print("\n3️⃣  Generating current inventory levels...")

inventory_records = []
for sku_data in products:
    sku = sku_data['sku']
    category = sku_data['category']
    
    for location in LOCATIONS:
        # Calculate recent average daily sales
        recent_sales = sales_df[
            (sales_df['sku'] == sku) & 
            (sales_df['location'] == location)
        ].tail(30)
        
        if len(recent_sales) > 0:
            avg_daily_sales = recent_sales['quantity'].sum() / 30
        else:
            avg_daily_sales = CATEGORIES[category]['base_demand'] / 7
        
        # Inventory scenarios for demo
        scenario = random.random()
        if scenario < 0.15:  # 15% stockout risk
            days_of_supply = random.uniform(1, 5)
            risk_level = 'high' if days_of_supply < 3 else 'medium'
        elif scenario < 0.25:  # 10% overstock
            days_of_supply = random.uniform(70, 120)
            risk_level = 'overstock'
        else:  # 75% normal
            days_of_supply = random.uniform(15, 45)
            risk_level = 'low'
        
        quantity_on_hand = int(avg_daily_sales * days_of_supply)
        
        inventory_records.append({
            'sku': sku,
            'location': location,
            'quantity_on_hand': max(0, quantity_on_hand),
            'days_of_supply': round(days_of_supply, 1),
            'avg_daily_sales': round(avg_daily_sales, 2),
            'risk_level': risk_level,
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })

inventory_df = pd.DataFrame(inventory_records)
inventory_df.to_csv('data/inventory_current.csv', index=False)
print(f"   ✅ Created {len(inventory_df)} inventory records")

# ============================================================================
# 4. Generate Pricing History
# ============================================================================
print("\n4️⃣  Generating pricing history...")

pricing_records = []
for sku_data in products:
    sku = sku_data['sku']
    base_price = sku_data['base_price']
    
    # Generate 5-10 pricing events over the period
    num_events = random.randint(5, 10)
    event_dates = sorted([
        START_DATE + timedelta(days=random.randint(0, DAYS_HISTORY))
        for _ in range(num_events)
    ])
    
    for i, event_date in enumerate(event_dates):
        is_promotion = random.random() < 0.4
        
        if is_promotion:
            discount = random.uniform(0.1, 0.35)
            promo_price = base_price * (1 - discount)
            promo_end = event_date + timedelta(days=random.randint(3, 14))
            
            pricing_records.append({
                'sku': sku,
                'effective_date': event_date.strftime('%Y-%m-%d'),
                'end_date': promo_end.strftime('%Y-%m-%d'),
                'base_price': round(base_price, 2),
                'promotional_price': round(promo_price, 2),
                'discount_percent': round(discount * 100, 1),
                'promotion_type': random.choice(['Seasonal Sale', 'Clearance', 'BOGO', 'Flash Sale']),
                'is_active': False
            })
        else:
            # Regular price adjustment
            price_change = random.uniform(-0.05, 0.10)
            new_price = base_price * (1 + price_change)
            
            pricing_records.append({
                'sku': sku,
                'effective_date': event_date.strftime('%Y-%m-%d'),
                'end_date': None,
                'base_price': round(new_price, 2),
                'promotional_price': None,
                'discount_percent': 0,
                'promotion_type': None,
                'is_active': i == len(event_dates) - 1  # Last one is active
            })

pricing_df = pd.DataFrame(pricing_records)
pricing_df.to_csv('data/pricing_history.csv', index=False)
print(f"   ✅ Created {len(pricing_df)} pricing records")

# ============================================================================
# 5. Generate Alerts (Stockout & Overstock)
# ============================================================================
print("\n5️⃣  Generating alerts...")

alerts = []
alert_id = 1

# Stockout alerts
stockout_inventory = inventory_df[inventory_df['risk_level'].isin(['high', 'medium'])]
for _, row in stockout_inventory.iterrows():
    severity = 'high' if row['risk_level'] == 'high' else 'medium'
    
    # Calculate recommended replenishment
    target_days = 30
    replenish_qty = int(row['avg_daily_sales'] * target_days - row['quantity_on_hand'])
    
    alerts.append({
        'alert_id': f"ALERT-{alert_id:04d}",
        'type': 'stockout_risk',
        'severity': severity,
        'sku': row['sku'],
        'location': row['location'],
        'current_inventory': row['quantity_on_hand'],
        'days_of_supply': row['days_of_supply'],
        'recommended_action': f"Replenish {replenish_qty} units",
        'estimated_stockout_date': (datetime.now() + timedelta(days=int(row['days_of_supply']))).strftime('%Y-%m-%d'),
        'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'status': 'active'
    })
    alert_id += 1

# Overstock alerts
overstock_inventory = inventory_df[inventory_df['risk_level'] == 'overstock']
for _, row in overstock_inventory.iterrows():
    excess_days = row['days_of_supply'] - 60
    excess_qty = int(row['avg_daily_sales'] * excess_days)
    
    # Get product cost for carrying cost calculation
    product = products_df[products_df['sku'] == row['sku']].iloc[0]
    carrying_cost = excess_qty * product['cost'] * 0.02  # 2% monthly rate
    
    alerts.append({
        'alert_id': f"ALERT-{alert_id:04d}",
        'type': 'overstock',
        'severity': 'medium',
        'sku': row['sku'],
        'location': row['location'],
        'current_inventory': row['quantity_on_hand'],
        'days_of_supply': row['days_of_supply'],
        'excess_quantity': excess_qty,
        'carrying_cost_monthly': round(carrying_cost, 2),
        'recommended_action': f"Discount 15-25% to clear {excess_qty} units",
        'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'status': 'active'
    })
    alert_id += 1

alerts_df = pd.DataFrame(alerts)
alerts_df.to_csv('data/alerts.csv', index=False)
print(f"   ✅ Created {len(alerts_df)} alerts ({len(stockout_inventory)} stockout, {len(overstock_inventory)} overstock)")

# ============================================================================
# 6. Generate Sample Forecasts (Pre-computed for demo)
# ============================================================================
print("\n6️⃣  Generating sample forecasts...")

forecasts = []
forecast_date = datetime.now()

for sku_data in products:
    sku = sku_data['sku']
    category = sku_data['category']
    
    for location in LOCATIONS:
        # Get recent sales trend
        recent_sales = sales_df[
            (sales_df['sku'] == sku) & 
            (sales_df['location'] == location)
        ].tail(30)
        
        if len(recent_sales) > 0:
            avg_daily = recent_sales['quantity'].mean()
            std_daily = recent_sales['quantity'].std()
        else:
            avg_daily = CATEGORIES[category]['base_demand'] / 7
            std_daily = avg_daily * 0.3
        
        # Generate 30-day forecast
        for day in range(1, 31):
            future_date = forecast_date + timedelta(days=day)
            
            # Add trend and seasonality
            trend = 1 + (day / 30) * random.uniform(-0.1, 0.2)
            day_of_week = future_date.weekday()
            weekly_factor = 1.2 if day_of_week in [5, 6] else 0.95
            
            # Point forecast
            forecast_value = avg_daily * trend * weekly_factor
            
            # Confidence intervals
            p10 = max(0, forecast_value - 1.28 * std_daily)
            p50 = forecast_value
            p90 = forecast_value + 1.28 * std_daily
            
            forecasts.append({
                'sku': sku,
                'location': location,
                'forecast_date': future_date.strftime('%Y-%m-%d'),
                'forecasted_demand': round(forecast_value, 2),
                'confidence_p10': round(p10, 2),
                'confidence_p50': round(p50, 2),
                'confidence_p90': round(p90, 2),
                'confidence_score': round(random.uniform(0.75, 0.95), 2),
                'model_version': 'v1.0',
                'generated_at': forecast_date.strftime('%Y-%m-%d %H:%M:%S')
            })

forecasts_df = pd.DataFrame(forecasts)
forecasts_df.to_csv('data/forecasts.csv', index=False)
print(f"   ✅ Created {len(forecasts_df):,} forecast records")

# ============================================================================
# 7. Generate Sample Recommendations
# ============================================================================
print("\n7️⃣  Generating sample recommendations...")

recommendations = []
rec_id = 1

# Select 20 random SKUs for recommendations
sample_skus = random.sample(products, 20)

for sku_data in sample_skus:
    sku = sku_data['sku']
    base_price = sku_data['base_price']
    cost = sku_data['cost']
    margin = sku_data['margin_percent'] / 100
    
    # Get inventory status
    sku_inventory = inventory_df[inventory_df['sku'] == sku].iloc[0]
    
    # Recommendation type based on inventory
    if sku_inventory['risk_level'] == 'overstock':
        # Clearance recommendation
        rec_type = 'clearance'
        discount = random.uniform(0.15, 0.30)
        recommended_price = base_price * (1 - discount)
        confidence = random.uniform(0.80, 0.92)
        
        # Impact estimation
        demand_lift = 1 + (discount * 2)  # Price elasticity
        revenue_impact = (recommended_price * demand_lift - base_price) * sku_inventory['avg_daily_sales'] * 30
        margin_impact = ((recommended_price - cost) / recommended_price - margin) * 100
        
        explanation = f"High inventory ({sku_inventory['days_of_supply']:.0f} days supply). Discount will accelerate sell-through and reduce carrying costs."
        top_factors = [
            {'factor': 'Excess Inventory', 'importance': 45},
            {'factor': 'Carrying Cost Risk', 'importance': 30},
            {'factor': 'Seasonal Demand Pattern', 'importance': 25}
        ]
        
    elif sku_inventory['risk_level'] in ['high', 'medium']:
        # Price increase recommendation (low stock)
        rec_type = 'price_optimization'
        price_increase = random.uniform(0.05, 0.15)
        recommended_price = base_price * (1 + price_increase)
        confidence = random.uniform(0.75, 0.88)
        
        # Impact estimation
        demand_reduction = 1 - (price_increase * 0.8)  # Price elasticity
        revenue_impact = (recommended_price * demand_reduction - base_price) * sku_inventory['avg_daily_sales'] * 30
        margin_impact = ((recommended_price - cost) / recommended_price - margin) * 100
        
        explanation = f"Low inventory ({sku_inventory['days_of_supply']:.0f} days supply). Price increase will optimize margin while managing demand."
        top_factors = [
            {'factor': 'Low Stock Levels', 'importance': 40},
            {'factor': 'Strong Recent Demand', 'importance': 35},
            {'factor': 'Competitor Pricing', 'importance': 25}
        ]
        
    else:
        # Regular price optimization
        rec_type = 'price_optimization'
        price_change = random.uniform(-0.05, 0.10)
        recommended_price = base_price * (1 + price_change)
        confidence = random.uniform(0.82, 0.95)
        
        # Impact estimation
        demand_change = 1 - (price_change * 1.2)
        revenue_impact = (recommended_price * demand_change - base_price) * sku_inventory['avg_daily_sales'] * 30
        margin_impact = ((recommended_price - cost) / recommended_price - margin) * 100
        
        explanation = f"Optimal price point based on demand elasticity and competitive positioning."
        top_factors = [
            {'factor': 'Demand Elasticity', 'importance': 40},
            {'factor': 'Competitor Pricing', 'importance': 35},
            {'factor': 'Historical Performance', 'importance': 25}
        ]
    
    recommendations.append({
        'recommendation_id': f"REC-{rec_id:04d}",
        'sku': sku,
        'type': rec_type,
        'current_price': round(base_price, 2),
        'recommended_price': round(recommended_price, 2),
        'price_change_percent': round((recommended_price / base_price - 1) * 100, 1),
        'confidence_score': round(confidence, 2),
        'estimated_revenue_impact': round(revenue_impact, 2),
        'estimated_margin_impact': round(margin_impact, 1),
        'explanation': explanation,
        'top_factors': json.dumps(top_factors),
        'status': 'pending',
        'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })
    rec_id += 1

recommendations_df = pd.DataFrame(recommendations)
recommendations_df.to_csv('data/recommendations.csv', index=False)
print(f"   ✅ Created {len(recommendations_df)} recommendations")

# ============================================================================
# 8. Generate Summary Statistics
# ============================================================================
print("\n8️⃣  Generating summary statistics...")

summary = {
    'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    'data_period': {
        'start_date': START_DATE.strftime('%Y-%m-%d'),
        'end_date': datetime.now().strftime('%Y-%m-%d'),
        'days': DAYS_HISTORY
    },
    'products': {
        'total_skus': len(products_df),
        'categories': list(CATEGORIES.keys()),
        'locations': LOCATIONS
    },
    'sales': {
        'total_transactions': len(sales_df),
        'total_revenue': round(sales_df['revenue'].sum(), 2),
        'avg_transaction_value': round(sales_df['revenue'].mean(), 2),
        'total_units_sold': int(sales_df['quantity'].sum())
    },
    'inventory': {
        'total_records': len(inventory_df),
        'stockout_risk_high': len(inventory_df[inventory_df['risk_level'] == 'high']),
        'stockout_risk_medium': len(inventory_df[inventory_df['risk_level'] == 'medium']),
        'overstock': len(inventory_df[inventory_df['risk_level'] == 'overstock']),
        'normal': len(inventory_df[inventory_df['risk_level'] == 'low'])
    },
    'alerts': {
        'total_active': len(alerts_df),
        'stockout_alerts': len(alerts_df[alerts_df['type'] == 'stockout_risk']),
        'overstock_alerts': len(alerts_df[alerts_df['type'] == 'overstock'])
    },
    'forecasts': {
        'total_forecasts': len(forecasts_df),
        'forecast_horizon_days': 30,
        'avg_confidence': round(forecasts_df['confidence_score'].mean(), 2)
    },
    'recommendations': {
        'total_recommendations': len(recommendations_df),
        'pending': len(recommendations_df[recommendations_df['status'] == 'pending']),
        'avg_confidence': round(recommendations_df['confidence_score'].mean(), 2),
        'total_potential_revenue_impact': round(recommendations_df['estimated_revenue_impact'].sum(), 2)
    }
}

with open('data/summary.json', 'w') as f:
    json.dump(summary, f, indent=2)

print(f"   ✅ Created summary statistics")

# ============================================================================
# 9. Print Summary Report
# ============================================================================
print("\n" + "="*70)
print("📊 DATA GENERATION COMPLETE!")
print("="*70)
print(f"\n📁 Files created in 'data/' directory:")
print(f"   • products.csv           - {len(products_df)} products")
print(f"   • sales_history.csv      - {len(sales_df):,} transactions")
print(f"   • inventory_current.csv  - {len(inventory_df)} inventory records")
print(f"   • pricing_history.csv    - {len(pricing_df)} pricing events")
print(f"   • alerts.csv             - {len(alerts_df)} active alerts")
print(f"   • forecasts.csv          - {len(forecasts_df):,} forecast records")
print(f"   • recommendations.csv    - {len(recommendations_df)} recommendations")
print(f"   • summary.json           - Summary statistics")

print(f"\n💰 Business Metrics:")
print(f"   • Total Revenue (90 days): ${summary['sales']['total_revenue']:,.2f}")
print(f"   • Total Units Sold: {summary['sales']['total_units_sold']:,}")
print(f"   • Avg Transaction Value: ${summary['sales']['avg_transaction_value']:.2f}")
print(f"   • Potential Revenue Impact: ${summary['recommendations']['total_potential_revenue_impact']:,.2f}")

print(f"\n⚠️  Alert Summary:")
print(f"   • High Stockout Risk: {summary['inventory']['stockout_risk_high']} SKUs")
print(f"   • Medium Stockout Risk: {summary['inventory']['stockout_risk_medium']} SKUs")
print(f"   • Overstock: {summary['inventory']['overstock']} SKUs")

print(f"\n🎯 Demo-Ready Features:")
print(f"   ✅ Realistic sales patterns with seasonality")
print(f"   ✅ Inventory scenarios (stockout, overstock, normal)")
print(f"   ✅ Price optimization recommendations")
print(f"   ✅ 30-day demand forecasts with confidence intervals")
print(f"   ✅ Actionable alerts with recommended actions")

print(f"\n🚀 Next Steps:")
print(f"   1. Review generated data in 'data/' directory")
print(f"   2. Wait for AWS credits to arrive")
print(f"   3. Run backend setup to upload data to S3/DynamoDB")
print(f"   4. Start building the prototype!")

print("\n" + "="*70)
print("✨ Ready to build a winning prototype! ✨")
print("="*70 + "\n")
