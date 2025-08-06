export interface PortfolioSummary {
  total_tickets: number;
  total_value: number;
  active_listings: number;
  monthly_revenue: number;
  total_cost_basis: number;
  unrealized_pnl: number;
  realized_pnl: number;
  tickets_sold: number;
}

export interface MarketTrends {
  price_trends: PriceTrend[];
  demand_forecast: Record<string, any>;
  market_sentiment: string;
  recent_activity: number;
}

export interface PriceTrend {
  date: string;
  avg_price: number;
  listing_count: number;
}

export interface MarketplaceAccount {
  id: string;
  platform: string;
  account_id?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface UserPerformance {
  total_roi: number;
  best_performing_team?: string;
  worst_performing_team?: string;
  avg_sale_time: number;
  success_rate: number;
  team_metrics: TeamMetric[];
}

export interface TeamMetric {
  team: string;
  roi: number;
  total_listings: number;
  sold_count: number;
  success_rate: number;
}