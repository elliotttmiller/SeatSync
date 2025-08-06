import React from 'react';
import PortfolioMetrics from './components/PortfolioMetrics';
import MarketTrends from './components/MarketTrends';
import MarketplaceAccounts from './components/MarketplaceAccounts';
import { usePortfolioData, useMarketTrends, useMarketplaceAccounts } from './hooks/useApi';

const App: React.FC = () => {
  const { data: portfolioData, loading: portfolioLoading, error: portfolioError } = usePortfolioData();
  const { data: trendsData, loading: trendsLoading, error: trendsError } = useMarketTrends();
  const { data: accountsData, loading: accountsLoading, error: accountsError, refetch: refetchAccounts } = useMarketplaceAccounts();

  return (
    <div className="App">
      <div className="header">
        <h1>🎫 SeatSync Dashboard</h1>
        <p>AI-Powered Sports Ticket Portfolio Management</p>
      </div>
      
      <div className="container">
        {/* Portfolio Overview */}
        {portfolioLoading ? (
          <div className="loading">Loading portfolio data...</div>
        ) : portfolioError ? (
          <div className="error">Error: {portfolioError}</div>
        ) : portfolioData ? (
          <PortfolioMetrics data={portfolioData} />
        ) : null}

        {/* Market Trends */}
        {trendsLoading ? (
          <div className="loading">Loading market trends...</div>
        ) : trendsError ? (
          <div className="error">Error: {trendsError}</div>
        ) : trendsData ? (
          <MarketTrends data={trendsData} />
        ) : null}

        {/* Marketplace Accounts */}
        {accountsLoading ? (
          <div className="loading">Loading marketplace accounts...</div>
        ) : accountsError ? (
          <div className="error">Error: {accountsError}</div>
        ) : (
          <MarketplaceAccounts 
            accounts={accountsData} 
            onAccountsUpdate={refetchAccounts}
          />
        )}

        {/* Footer */}
        <div className="card" style={{ textAlign: 'center', marginTop: '40px' }}>
          <h3>🚀 Phase 1 Implementation Complete</h3>
          <p>
            Backend services have been hardened with real database queries, 
            authentication system is operational, and marketplace integration 
            foundation is in place. Ready for Phase 2 AI model development!
          </p>
          <div style={{ display: 'flex', justifyContent: 'center', gap: '20px', marginTop: '20px' }}>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: '24px' }}>✅</div>
              <div style={{ fontSize: '12px', marginTop: '5px' }}>Auth System</div>
            </div>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: '24px' }}>✅</div>
              <div style={{ fontSize: '12px', marginTop: '5px' }}>Analytics</div>
            </div>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: '24px' }}>✅</div>
              <div style={{ fontSize: '12px', marginTop: '5px' }}>Marketplace</div>
            </div>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: '24px' }}>⏳</div>
              <div style={{ fontSize: '12px', marginTop: '5px' }}>AI Models</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default App;