import React from 'react';
import { useLiveMarket } from '../hooks/useQueries';
import '../styles/Dashboard.css';

interface Stock {
  symbol: string;
  companyName: string;
  ltp: number;
  change: number;
  percentChange: number;
  volume: number;
}

const Dashboard: React.FC = () => {
  const { data: marketData, isLoading, error } = useLiveMarket();

  if (isLoading) return <div className="dashboard-loading">Loading market data...</div>;
  if (error) return <div className="dashboard-error">Error loading market data</div>;

  const stocks: Stock[] = marketData?.data?.data || [];
  const gainers = stocks.slice().sort((a, b) => (b.change || 0) - (a.change || 0)).slice(0, 5);
  const losers = stocks.slice().sort((a, b) => (a.change || 0) - (b.change || 0)).slice(0, 5);

  return (
    <div className="dashboard">
      <h1>NEPSE Market Dashboard</h1>
      
      <div className="dashboard-grid">
        <div className="dashboard-section">
          <h2>📈 Top Gainers</h2>
          <table className="market-table">
            <thead>
              <tr>
                <th>Symbol</th>
                <th>Company</th>
                <th>LTP</th>
                <th>Change</th>
                <th>%</th>
              </tr>
            </thead>
            <tbody>
              {gainers.map((stock) => (
                <tr key={stock.symbol} className="positive">
                  <td className="symbol">{stock.symbol}</td>
                  <td>{stock.companyName}</td>
                  <td className="price">{stock.ltp?.toFixed(2)}</td>
                  <td className="change">{stock.change?.toFixed(2)}</td>
                  <td className="percent">{stock.percentChange?.toFixed(2)}%</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div className="dashboard-section">
          <h2>📉 Top Losers</h2>
          <table className="market-table">
            <thead>
              <tr>
                <th>Symbol</th>
                <th>Company</th>
                <th>LTP</th>
                <th>Change</th>
                <th>%</th>
              </tr>
            </thead>
            <tbody>
              {losers.map((stock) => (
                <tr key={stock.symbol} className="negative">
                  <td className="symbol">{stock.symbol}</td>
                  <td>{stock.companyName}</td>
                  <td className="price">{stock.ltp?.toFixed(2)}</td>
                  <td className="change">{stock.change?.toFixed(2)}</td>
                  <td className="percent">{stock.percentChange?.toFixed(2)}%</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <div className="dashboard-section full-width">
        <h2>All Stocks ({stocks.length})</h2>
        <table className="market-table full-width-table">
          <thead>
            <tr>
              <th>Symbol</th>
              <th>Company</th>
              <th>LTP</th>
              <th>Change</th>
              <th>%</th>
              <th>Volume</th>
            </tr>
          </thead>
          <tbody>
            {stocks.map((stock) => (
              <tr key={stock.symbol} className={stock.percentChange > 0 ? 'positive' : 'negative'}>
                <td className="symbol">{stock.symbol}</td>
                <td>{stock.companyName}</td>
                <td className="price">{stock.ltp?.toFixed(2)}</td>
                <td className="change">{stock.change?.toFixed(2)}</td>
                <td className="percent">{stock.percentChange?.toFixed(2)}%</td>
                <td>{(stock.volume || 0).toLocaleString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default Dashboard;
