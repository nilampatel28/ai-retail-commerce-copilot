import React, { useState } from 'react';

interface Alert {
  alert_id: string;
  type: string;
  severity: string;
  sku: string;
  location: string;
  recommended_action: string;
}

interface Recommendation {
  recommendation_id: string;
  sku: string;
  type: string;
  current_price: number;
  recommended_price: number;
  price_change_percent: number;
  estimated_revenue_impact: number;
}

const Dashboard: React.FC = () => {
  const [alerts] = useState<Alert[]>([
    { alert_id: 'ALERT-001', type: 'stockout_risk', severity: 'high', sku: 'SKU-046', location: 'Store-LA', recommended_action: 'Replenish 1,603 units immediately' },
    { alert_id: 'ALERT-002', type: 'stockout_risk', severity: 'high', sku: 'SKU-023', location: 'Store-NY', recommended_action: 'Replenish 892 units within 2 days' },
    { alert_id: 'ALERT-003', type: 'stockout_risk', severity: 'medium', sku: 'SKU-015', location: 'Store-CHI', recommended_action: 'Replenish 445 units within 5 days' },
    { alert_id: 'ALERT-004', type: 'stockout_risk', severity: 'high', sku: 'SKU-031', location: 'Store-SF', recommended_action: 'Replenish 1,234 units immediately' },
    { alert_id: 'ALERT-005', type: 'stockout_risk', severity: 'medium', sku: 'SKU-042', location: 'Store-LA', recommended_action: 'Replenish 678 units within 4 days' },
    { alert_id: 'ALERT-006', type: 'stockout_risk', severity: 'high', sku: 'SKU-008', location: 'Store-NY', recommended_action: 'Replenish 2,100 units immediately' },
    { alert_id: 'ALERT-007', type: 'stockout_risk', severity: 'medium', sku: 'SKU-019', location: 'Store-CHI', recommended_action: 'Replenish 567 units within 3 days' },
    { alert_id: 'ALERT-008', type: 'stockout_risk', severity: 'high', sku: 'SKU-027', location: 'Store-SF', recommended_action: 'Replenish 1,890 units immediately' }
  ]);

  const [recommendations] = useState<Recommendation[]>([
    { recommendation_id: 'REC-001', sku: 'SKU-010', type: 'price_optimization', current_price: 171.02, recommended_price: 175.10, price_change_percent: 2.4, estimated_revenue_impact: 5283 },
    { recommendation_id: 'REC-002', sku: 'SKU-023', type: 'price_optimization', current_price: 89.50, recommended_price: 92.75, price_change_percent: 3.6, estimated_revenue_impact: 8942 },
    { recommendation_id: 'REC-003', sku: 'SKU-046', type: 'clearance', current_price: 245.00, recommended_price: 220.50, price_change_percent: -10.0, estimated_revenue_impact: 12457 },
    { recommendation_id: 'REC-004', sku: 'SKU-015', type: 'price_optimization', current_price: 134.99, recommended_price: 139.99, price_change_percent: 3.7, estimated_revenue_impact: 6789 },
    { recommendation_id: 'REC-005', sku: 'SKU-031', type: 'promotional', current_price: 199.99, recommended_price: 189.99, price_change_percent: -5.0, estimated_revenue_impact: 15235 },
    { recommendation_id: 'REC-006', sku: 'SKU-008', type: 'price_optimization', current_price: 299.99, recommended_price: 309.99, price_change_percent: 3.3, estimated_revenue_impact: 18456 },
    { recommendation_id: 'REC-007', sku: 'SKU-019', type: 'clearance', current_price: 159.99, recommended_price: 143.99, price_change_percent: -10.0, estimated_revenue_impact: 9876 },
    { recommendation_id: 'REC-008', sku: 'SKU-027', type: 'price_optimization', current_price: 449.99, recommended_price: 469.99, price_change_percent: 4.4, estimated_revenue_impact: 22890 },
    { recommendation_id: 'REC-009', sku: 'SKU-035', type: 'promotional', current_price: 79.99, recommended_price: 74.99, price_change_percent: -6.3, estimated_revenue_impact: 5678 },
    { recommendation_id: 'REC-010', sku: 'SKU-042', type: 'price_optimization', current_price: 189.99, recommended_price: 194.99, price_change_percent: 2.6, estimated_revenue_impact: 7890 }
  ]);

  const highAlerts = alerts.filter(a => a.severity === 'high').length;
  const mediumAlerts = alerts.filter(a => a.severity === 'medium').length;
  const totalRevImpact = recommendations.reduce((sum, r) => sum + r.estimated_revenue_impact, 0);

  return (
    <div className="space-y-6">
      {/* Metrics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">High Priority Alerts</p>
              <p className="text-3xl font-bold text-red-600 mt-2">{highAlerts}</p>
            </div>
            <div className="w-12 h-12 bg-red-100 rounded-lg flex items-center justify-center">
              <span className="text-2xl">⚠️</span>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Medium Priority Alerts</p>
              <p className="text-3xl font-bold text-yellow-600 mt-2">{mediumAlerts}</p>
            </div>
            <div className="w-12 h-12 bg-yellow-100 rounded-lg flex items-center justify-center">
              <span className="text-2xl">⚡</span>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Revenue Opportunity</p>
              <p className="text-3xl font-bold text-green-600 mt-2">
                ${totalRevImpact.toLocaleString()}
              </p>
            </div>
            <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
              <span className="text-2xl">💰</span>
            </div>
          </div>
        </div>
      </div>

      {/* Alerts Table */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900">Active Alerts</h2>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Severity</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">SKU</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Location</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Type</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {alerts.map((alert) => (
                <tr key={alert.alert_id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                      alert.severity === 'high' 
                        ? 'bg-red-100 text-red-800' 
                        : 'bg-yellow-100 text-yellow-800'
                    }`}>
                      {alert.severity}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {alert.sku}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                    {alert.location}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                    {alert.type.replace('_', ' ')}
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-600">
                    {alert.recommended_action}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Recommendations Table */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900">Pricing Recommendations</h2>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">SKU</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Current Price</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Recommended</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Change</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Impact</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {recommendations.map((rec) => (
                <tr key={rec.recommendation_id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {rec.sku}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                    ${rec.current_price.toFixed(2)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 font-medium">
                    ${rec.recommended_price.toFixed(2)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`text-sm font-medium ${
                      rec.price_change_percent > 0 ? 'text-green-600' : 'text-red-600'
                    }`}>
                      {rec.price_change_percent > 0 ? '+' : ''}{rec.price_change_percent.toFixed(1)}%
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-green-600 font-medium">
                    +${rec.estimated_revenue_impact.toLocaleString()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
