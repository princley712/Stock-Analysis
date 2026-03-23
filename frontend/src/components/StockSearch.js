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
          placeholder="Search stock (e.g. RELIANCE, TCS, AAPL)..."
          value={ticker}
          onChange={(e) => setTicker(e.target.value.toUpperCase())}
          maxLength={15}
          autoComplete="off"
          list="stock-suggestions"
        />
        <datalist id="stock-suggestions">
          <option value="RELIANCE" />
          <option value="TCS" />
          <option value="HDFCBANK" />
          <option value="INFY" />
          <option value="ICICIBANK" />
          <option value="SBIN" />
          <option value="BHARTIARTL" />
          <option value="ITC" />
          <option value="TATAMOTORS" />
          <option value="AAPL" />
          <option value="GOOG" />
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
