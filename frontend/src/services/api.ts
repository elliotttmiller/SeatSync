import { PortfolioSummary, MarketTrends, MarketplaceAccount, UserPerformance } from '../types/api';

const API_BASE_URL = 'http://localhost:8000/api/v1';

class ApiService {
  async getPortfolioSummary(): Promise<PortfolioSummary> {
    const response = await fetch(`${API_BASE_URL}/analytics/portfolio-summary`);
    if (!response.ok) {
      throw new Error('Failed to fetch portfolio summary');
    }
    return response.json();
  }

  async getMarketTrends(): Promise<MarketTrends> {
    const response = await fetch(`${API_BASE_URL}/analytics/market-trends`);
    if (!response.ok) {
      throw new Error('Failed to fetch market trends');
    }
    return response.json();
  }

  async getUserPerformance(): Promise<UserPerformance> {
    const response = await fetch(`${API_BASE_URL}/analytics/user-performance`);
    if (!response.ok) {
      throw new Error('Failed to fetch user performance');
    }
    return response.json();
  }

  async getMarketplaceAccounts(): Promise<MarketplaceAccount[]> {
    const response = await fetch(`${API_BASE_URL}/marketplace/accounts`);
    if (!response.ok) {
      throw new Error('Failed to fetch marketplace accounts');
    }
    return response.json();
  }

  async syncMarketplaceData(): Promise<any> {
    const response = await fetch(`${API_BASE_URL}/marketplace/sync`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
    });
    if (!response.ok) {
      throw new Error('Failed to sync marketplace data');
    }
    return response.json();
  }
}

export const apiService = new ApiService();