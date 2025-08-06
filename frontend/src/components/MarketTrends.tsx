import React from 'react';
import { MarketTrends } from '../types/api';

interface MarketTrendsProps {
  data: MarketTrends;
}

const MarketTrendsComponent: React.FC<MarketTrendsProps> = ({ data }) => {
  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(amount);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString();
  };

  const getSentimentColor = (sentiment: string) => {
    switch (sentiment.toLowerCase()) {
      case 'bullish':
        return 'positive';
      case 'bearish':
        return 'negative';
      default:
        return '';
    }
  };

  return (
    <div className="card">
      <h2>Market Trends & Analysis</h2>
      
      <div className="metrics-grid">
        <div className="metric">
          <h3>Market Sentiment</h3>
          <div className={`value ${getSentimentColor(data.market_sentiment)}`}>
            {data.market_sentiment.charAt(0).toUpperCase() + data.market_sentiment.slice(1)}
          </div>
        </div>
        <div className="metric">
          <h3>Recent Activity</h3>
          <div className="value">{data.recent_activity} listings</div>
        </div>
      </div>

      {data.price_trends.length > 0 && (
        <div style={{ marginTop: '20px' }}>
          <h3>Recent Price Trends</h3>
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr style={{ backgroundColor: '#f5f5f5' }}>
                  <th style={{ padding: '10px', textAlign: 'left', border: '1px solid #ddd' }}>
                    Game Date
                  </th>
                  <th style={{ padding: '10px', textAlign: 'left', border: '1px solid #ddd' }}>
                    Average Price
                  </th>
                  <th style={{ padding: '10px', textAlign: 'left', border: '1px solid #ddd' }}>
                    Listings
                  </th>
                </tr>
              </thead>
              <tbody>
                {data.price_trends.map((trend, index) => (
                  <tr key={index}>
                    <td style={{ padding: '10px', border: '1px solid #ddd' }}>
                      {formatDate(trend.date)}
                    </td>
                    <td style={{ padding: '10px', border: '1px solid #ddd' }}>
                      {formatCurrency(trend.avg_price)}
                    </td>
                    <td style={{ padding: '10px', border: '1px solid #ddd' }}>
                      {trend.listing_count}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {Object.keys(data.demand_forecast).length > 0 && (
        <div style={{ marginTop: '20px' }}>
          <h3>AI Demand Forecast</h3>
          {Object.entries(data.demand_forecast).map(([model, forecast]) => (
            <div key={model} className="metric">
              <h3>{model.replace('_', ' ').toUpperCase()}</h3>
              <div className="value">
                {formatCurrency(forecast.avg_prediction)} 
                <small style={{ fontSize: '14px', marginLeft: '10px' }}>
                  ({(forecast.avg_confidence * 100).toFixed(0)}% confidence)
                </small>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default MarketTrendsComponent;