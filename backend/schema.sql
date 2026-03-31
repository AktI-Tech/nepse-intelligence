-- NEPSE Intelligence Database Schema

-- Indices (NSE, Banking, etc.)
CREATE TABLE IF NOT EXISTS indices (
  id SERIAL PRIMARY KEY,
  symbol VARCHAR(50) UNIQUE NOT NULL,
  name VARCHAR(255) NOT NULL,
  current_value DECIMAL(10, 2),
  points_change DECIMAL(10, 2),
  percent_change DECIMAL(5, 2),
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Individual stocks
CREATE TABLE IF NOT EXISTS stocks (
  id SERIAL PRIMARY KEY,
  symbol VARCHAR(50) UNIQUE NOT NULL,
  name VARCHAR(255) NOT NULL,
  sector VARCHAR(100),
  current_price DECIMAL(10, 2),
  open_price DECIMAL(10, 2),
  high_price DECIMAL(10, 2),
  low_price DECIMAL(10, 2),
  volume BIGINT,
  market_cap DECIMAL(15, 2),
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Market data snapshots (for historical tracking)
CREATE TABLE IF NOT EXISTS market_data (
  id SERIAL PRIMARY KEY,
  symbol VARCHAR(50) NOT NULL,
  price DECIMAL(10, 2),
  volume BIGINT,
  timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (symbol) REFERENCES stocks(symbol) ON DELETE CASCADE
);

-- Index historical data
CREATE TABLE IF NOT EXISTS index_history (
  id SERIAL PRIMARY KEY,
  index_id INT NOT NULL,
  value DECIMAL(10, 2),
  points_change DECIMAL(10, 2),
  percent_change DECIMAL(5, 2),
  timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (index_id) REFERENCES indices(id) ON DELETE CASCADE
);

-- Trading strategies & signals (for future ML models)
CREATE TABLE IF NOT EXISTS trading_signals (
  id SERIAL PRIMARY KEY,
  symbol VARCHAR(50) NOT NULL,
  signal_type VARCHAR(50), -- 'buy', 'sell', 'hold', 'alert'
  confidence DECIMAL(3, 2),
  reason TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (symbol) REFERENCES stocks(symbol) ON DELETE CASCADE
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_market_data_symbol ON market_data(symbol);
CREATE INDEX IF NOT EXISTS idx_market_data_timestamp ON market_data(timestamp);
CREATE INDEX IF NOT EXISTS idx_index_history_timestamp ON index_history(timestamp);
CREATE INDEX IF NOT EXISTS idx_trading_signals_symbol ON trading_signals(symbol);
