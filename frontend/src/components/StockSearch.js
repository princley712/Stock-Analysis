'use client';

import { useState } from 'react';

export default function StockSearch({ onSearch, loading }) {
  const [ticker, setTicker] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    const value = ticker.trim().toUpperCase();
    if (value) onSearch(value);
  };

  return (
    <div className="search-container">
      <form onSubmit={handleSubmit} className="search-wrapper">
        <span className="search-icon">🔍</span>
        <input
          id="stock-search-input"
          type="text"
          className="search-input"
          placeholder="Search ticker (e.g. RELIANCE.NS, TCS.NS)..."
          value={ticker}
          onChange={(e) => setTicker(e.target.value.toUpperCase())}
          maxLength={15}
          autoComplete="off"
          list="stock-suggestions"
        />
        <datalist id="stock-suggestions">
          <option value="RELIANCE.NS" />
          <option value="TCS.NS" />
          <option value="HDFCBANK.NS" />
          <option value="INFY.NS" />
          <option value="ICICIBANK.NS" />
          <option value="SBIN.NS" />
          <option value="BHARTIARTL.NS" />
          <option value="ITC.NS" />
          <option value="TATAMOTORS.NS" />
          <option value="LTMINDTREE.NS" />
        </datalist>
        <button
          id="stock-search-btn"
          type="submit"
          className="search-btn"
          disabled={!ticker.trim() || loading}
        >
          {loading ? 'Analyzing...' : 'Analyze'}
        </button>
      </form>
    </div>
  );
}
