import React, { useState } from 'react';
import PortfolioMetrics from './components/PortfolioMetrics';
import MarketTrends from './components/MarketTrends';
import MarketplaceAccounts from './components/MarketplaceAccounts';
import AIChatInterface from './components/AIChatInterface';
import AIInsightsDashboard from './components/AIInsightsDashboard';
import { usePortfolioData, useMarketTrends, useMarketplaceAccounts } from './hooks/useApi';

const App: React.FC = () => {
  const { data: portfolioData, loading: portfolioLoading, error: portfolioError } = usePortfolioData();
  const { data: trendsData, loading: trendsLoading, error: trendsError } = useMarketTrends();
  const { data: accountsData, loading: accountsLoading, error: accountsError, refetch: refetchAccounts } = useMarketplaceAccounts();
  
  const [activeTab, setActiveTab] = useState<'dashboard' | 'ai-insights' | 'ai-chat'>('dashboard');

  const renderTabContent = () => {
    switch (activeTab) {
      case 'ai-insights':
        return <AIInsightsDashboard />;
      case 'ai-chat':
        return (
          <div style={{ maxWidth: '800px', margin: '0 auto', padding: '20px' }}>
            <AIChatInterface />
          </div>
        );
      case 'dashboard':
      default:
        return (
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
          </div>
        );
    }
  };

  return (
    <div className="App">
      <div className="header">
        <h1>🎫 SeatSync Dashboard</h1>
        <p>AI-Powered Sports Ticket Portfolio Management</p>
        
        {/* Navigation Tabs */}
        <div style={{ 
          display: 'flex', 
          justifyContent: 'center', 
          gap: '20px', 
          marginTop: '20px',
          borderBottom: '1px solid #ddd',
          paddingBottom: '10px'
        }}>
          <button
            onClick={() => setActiveTab('dashboard')}
            style={{
              padding: '10px 20px',
              border: 'none',
              background: activeTab === 'dashboard' ? '#007bff' : 'transparent',
              color: activeTab === 'dashboard' ? 'white' : '#007bff',
              borderRadius: '5px',
              cursor: 'pointer',
              fontWeight: 'bold'
            }}
          >
            📊 Portfolio Dashboard
          </button>
          <button
            onClick={() => setActiveTab('ai-insights')}
            style={{
              padding: '10px 20px',
              border: 'none',
              background: activeTab === 'ai-insights' ? '#007bff' : 'transparent',
              color: activeTab === 'ai-insights' ? 'white' : '#007bff',
              borderRadius: '5px',
              cursor: 'pointer',
              fontWeight: 'bold'
            }}
          >
            🤖 AI Insights
          </button>
          <button
            onClick={() => setActiveTab('ai-chat')}
            style={{
              padding: '10px 20px',
              border: 'none',
              background: activeTab === 'ai-chat' ? '#007bff' : 'transparent',
              color: activeTab === 'ai-chat' ? 'white' : '#007bff',
              borderRadius: '5px',
              cursor: 'pointer',
              fontWeight: 'bold'
            }}
          >
            💬 AI Assistant
          </button>
        </div>
      </div>
      
      {renderTabContent()}

      {/* Updated Footer showing Phase 2 & 3 completion */}
      {activeTab === 'dashboard' && (
        <div className="container">
          <div className="card" style={{ textAlign: 'center', marginTop: '40px' }}>
            <h3>🚀 Phase 2 & 3 Implementation Complete</h3>
            <p>
              Advanced AI intelligence layer and automation systems are now operational!
              Enjoy intelligent portfolio management, predictive analytics, automated optimization,
              and conversational AI assistance.
            </p>
            <div style={{ display: 'flex', justifyContent: 'center', gap: '20px', marginTop: '20px' }}>
              <div style={{ textAlign: 'center' }}>
                <div style={{ fontSize: '24px' }}>✅</div>
                <div style={{ fontSize: '12px', marginTop: '5px' }}>Phase 1 Foundation</div>
              </div>
              <div style={{ textAlign: 'center' }}>
                <div style={{ fontSize: '24px' }}>✅</div>
                <div style={{ fontSize: '12px', marginTop: '5px' }}>Phase 2 AI Intelligence</div>
              </div>
              <div style={{ textAlign: 'center' }}>
                <div style={{ fontSize: '24px' }}>✅</div>
                <div style={{ fontSize: '12px', marginTop: '5px' }}>Phase 3 Automation</div>
              </div>
              <div style={{ textAlign: 'center' }}>
                <div style={{ fontSize: '24px' }}>🎯</div>
                <div style={{ fontSize: '12px', marginTop: '5px' }}>Production Ready</div>
              </div>
            </div>
            <div style={{ marginTop: '20px', fontSize: '14px', color: '#666' }}>
              <strong>New Capabilities:</strong> AI Price Prediction • Smart Portfolio Optimization • 
              Predictive Alerts • Conversational AI • Automated Trading Strategies • Market Sentiment Analysis
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default App;