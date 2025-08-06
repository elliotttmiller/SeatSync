import React from 'react';
import { PortfolioSummary } from '../types/api';

interface PortfolioMetricsProps {
  data: PortfolioSummary;
}

const PortfolioMetrics: React.FC<PortfolioMetricsProps> = ({ data }) => {
  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(amount);
  };

  const formatPercentage = (value: number) => {
    return `${value >= 0 ? '+' : ''}${value.toFixed(1)}%`;
  };

  // Calculate ROI percentage
  const totalRoi = data.total_cost_basis > 0 
    ? ((data.realized_pnl + data.unrealized_pnl) / data.total_cost_basis) * 100 
    : 0;

  return (
    <div className="card">
      <h2>Portfolio Overview</h2>
      <div className="metrics-grid">
        <div className="metric">
          <h3>Total Season Tickets</h3>
          <div className="value">{data.total_tickets}</div>
        </div>
        <div className="metric">
          <h3>Active Listings</h3>
          <div className="value">{data.active_listings}</div>
        </div>
        <div className="metric">
          <h3>Total Portfolio Value</h3>
          <div className="value">{formatCurrency(data.total_value)}</div>
        </div>
        <div className="metric">
          <h3>Monthly Revenue</h3>
          <div className="value">{formatCurrency(data.monthly_revenue)}</div>
        </div>
        <div className="metric">
          <h3>Cost Basis</h3>
          <div className="value">{formatCurrency(data.total_cost_basis)}</div>
        </div>
        <div className="metric">
          <h3>Realized P&L</h3>
          <div className={`value ${data.realized_pnl >= 0 ? 'positive' : 'negative'}`}>
            {formatCurrency(data.realized_pnl)}
          </div>
        </div>
        <div className="metric">
          <h3>Unrealized P&L</h3>
          <div className={`value ${data.unrealized_pnl >= 0 ? 'positive' : 'negative'}`}>
            {formatCurrency(data.unrealized_pnl)}
          </div>
        </div>
        <div className="metric">
          <h3>Total ROI</h3>
          <div className={`value ${totalRoi >= 0 ? 'positive' : 'negative'}`}>
            {formatPercentage(totalRoi)}
          </div>
        </div>
        <div className="metric">
          <h3>Tickets Sold</h3>
          <div className="value">{data.tickets_sold}</div>
        </div>
      </div>
    </div>
  );
};

export default PortfolioMetrics;