import React, { useState } from 'react';
import { MarketplaceAccount } from '../types/api';
import { apiService } from '../services/api';

interface MarketplaceAccountsProps {
  accounts: MarketplaceAccount[];
  onAccountsUpdate: () => void;
}

const MarketplaceAccounts: React.FC<MarketplaceAccountsProps> = ({ 
  accounts, 
  onAccountsUpdate 
}) => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSync = async () => {
    setIsLoading(true);
    setError(null);
    try {
      await apiService.syncMarketplaceData();
      onAccountsUpdate(); // Refresh accounts data
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Sync failed');
    } finally {
      setIsLoading(false);
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString();
  };

  const getPlatformLogo = (platform: string) => {
    const platformMap: Record<string, string> = {
      stubhub: '🎫',
      seatgeek: '🪑',
      ticketmaster: '🎭'
    };
    return platformMap[platform.toLowerCase()] || '🏟️';
  };

  return (
    <div className="card">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h2>Marketplace Connections</h2>
        <button 
          onClick={handleSync}
          disabled={isLoading}
          style={{
            backgroundColor: '#1976d2',
            color: 'white',
            border: 'none',
            padding: '10px 20px',
            borderRadius: '4px',
            cursor: isLoading ? 'not-allowed' : 'pointer',
            opacity: isLoading ? 0.6 : 1
          }}
        >
          {isLoading ? 'Syncing...' : 'Sync All Platforms'}
        </button>
      </div>

      {error && (
        <div className="error">
          Error: {error}
        </div>
      )}

      {accounts.length === 0 ? (
        <div className="loading">
          No marketplace accounts connected. Connect your accounts to start managing your listings.
        </div>
      ) : (
        <div>
          {accounts.map((account) => (
            <div key={account.id} className="marketplace-account">
              <div style={{ display: 'flex', alignItems: 'center', gap: '15px' }}>
                <span style={{ fontSize: '24px' }}>
                  {getPlatformLogo(account.platform)}
                </span>
                <div>
                  <h3 style={{ margin: '0 0 5px 0' }}>
                    {account.platform.charAt(0).toUpperCase() + account.platform.slice(1)}
                  </h3>
                  {account.account_id && (
                    <p style={{ margin: '0', color: '#666', fontSize: '14px' }}>
                      Account: {account.account_id}
                    </p>
                  )}
                  <p style={{ margin: '0', color: '#666', fontSize: '12px' }}>
                    Connected: {formatDate(account.created_at)}
                  </p>
                </div>
              </div>
              <div>
                <span className={account.is_active ? 'status-active' : 'status-inactive'}>
                  {account.is_active ? 'Active' : 'Inactive'}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}

      <div style={{ marginTop: '20px', padding: '15px', backgroundColor: '#f8f9fa', borderRadius: '4px' }}>
        <h4 style={{ margin: '0 0 10px 0' }}>Platform Integration Status</h4>
        <p style={{ margin: '0', fontSize: '14px', color: '#666' }}>
          {accounts.length} marketplace{accounts.length !== 1 ? 's' : ''} connected. 
          {accounts.filter(a => a.is_active).length} active platform{accounts.filter(a => a.is_active).length !== 1 ? 's' : ''}.
        </p>
      </div>
    </div>
  );
};

export default MarketplaceAccounts;