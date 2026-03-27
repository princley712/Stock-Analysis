'use client';

import { useState, useEffect, useCallback, useRef } from 'react';
import StockSearch from '../components/StockSearch';
import StockHeader from '../components/StockHeader';
import StockChart from '../components/StockChart';
import IndicatorsPanel from '../components/IndicatorsPanel';
import NewsPanel from '../components/NewsPanel';
import BuySellMeter from '../components/BuySellMeter';
import PatternsPanel from '../components/PatternsPanel';

const API_BASE = '';
const POLL_INTERVAL = 10000; // 10 seconds

const RANGES = [
  { label: '1D', value: '1d', interval: '5m' },
  { label: '1W', value: '5d', interval: '15m' },
  { label: '1M', value: '1mo', interval: '1d' },
  { label: '6M', value: '6mo', interval: '1d' },
  { label: '1Y', value: '1y', interval: '1d' },
  { label: '5Y', value: '5y', interval: '1wk' },
  { label: 'MAX', value: 'max', interval: '1mo' }
];

export default function Dashboard() {
  const [ticker, setTicker] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const [stockData, setStockData] = useState(null);
  const [indicators, setIndicators] = useState(null);
  const [news, setNews] = useState(null);
  const [analysis, setAnalysis] = useState(null);
  const [lastUpdated, setLastUpdated] = useState(null);
  
  const [activeRange, setActiveRange] = useState(RANGES[3]); // Default 6M
  const activeRangeRef = useRef(RANGES[3]);
  const [focusedPattern, setFocusedPattern] = useState(null);

  const pollingRef = useRef(null);
  const isFirstLoad = useRef(true);

  const fetchAllData = useCallback(async (t, showLoading = true) => {
    if (!t) return;

    if (showLoading) setLoading(true);
    setError('');

    const range = activeRangeRef.current;

    try {
      const [stockRes, indicatorsRes, newsRes, analysisRes] = await Promise.allSettled([
        fetch(`${API_BASE}/api/stock/${t}?period=${range.value}&interval=${range.interval}`).then(r => r.ok ? r.json() : Promise.reject(r)),
        fetch(`${API_BASE}/api/indicators/${t}`).then(r => r.ok ? r.json() : Promise.reject(r)),
        fetch(`${API_BASE}/api/news/${t}`).then(r => r.ok ? r.json() : Promise.reject(r)),
        fetch(`${API_BASE}/api/analysis/${t}`).then(r => r.ok ? r.json() : Promise.reject(r)),
      ]);

      if (stockRes.status === 'fulfilled') {
        const data = stockRes.value;
        setStockData(data);
        // Sync resolved ticker back to state if it changed (e.g. RELIANCE -> RELIANCE.NS)
        if (data.ticker && data.ticker !== t) {
          setTicker(data.ticker);
        }
      } else {
        setError(`Could not fetch stock data for ${t}`);
      }

      if (indicatorsRes.status === 'fulfilled') setIndicators(indicatorsRes.value);
      if (newsRes.status === 'fulfilled') setNews(newsRes.value);
      if (analysisRes.status === 'fulfilled') setAnalysis(analysisRes.value);

      setLastUpdated(new Date());
    } catch (err) {
      setError('Failed to fetch data. Is the backend running?');
    } finally {
      setLoading(false);
    }
  }, []);

  const handleSearch = useCallback((t) => {
    setTicker(t);
    isFirstLoad.current = true;

    // Clear old data
    setStockData(null);
    setIndicators(null);
    setNews(null);
    setAnalysis(null);

    // Clear existing polling
    if (pollingRef.current) clearInterval(pollingRef.current);

    // Fetch immediately
    fetchAllData(t, true);

    // Start polling
    pollingRef.current = setInterval(() => {
      fetchAllData(t, false);
    }, POLL_INTERVAL);
  }, [fetchAllData]);

  const handleRangeChange = async (range) => {
    setFocusedPattern(null); // Reset focus when switching ranges
    setActiveRange(range);
    activeRangeRef.current = range;
    if (!ticker) return;

    try {
      const res = await fetch(`${API_BASE}/api/stock/${ticker}?period=${range.value}&interval=${range.interval}`);
      if (res.ok) {
        const data = await res.json();
        setStockData(data);
      }
    } catch (err) {
      console.error(err);
    }
  };

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (pollingRef.current) clearInterval(pollingRef.current);
    };
  }, []);

  return (
    <div className="app-container">
      {/* Header */}
      <header className="app-header">
        <div className="logo">
          <div className="logo-icon">⚡</div>
          <div>
            <h1>StockPulse AI</h1>
            <span>Real-time AI Stock Analysis</span>
          </div>
        </div>
        <div className="header-status">
          {ticker && (
            <div className="live-indicator">
              <span className="live-dot" />
              <span>Polling every 10s</span>
            </div>
          )}
          {lastUpdated && (
            <div className="live-indicator" style={{ opacity: 0.7 }}>
              Updated {lastUpdated.toLocaleTimeString()}
            </div>
          )}
        </div>
      </header>

      {/* Search */}
      <StockSearch onSearch={handleSearch} loading={loading} />

      {/* Error */}
      {error && (
        <div className="error-banner">
          <span>⚠️</span> {error}
        </div>
      )}

      {/* Loading */}
      {loading && !stockData && (
        <div className="loading-container">
          <div className="loading-spinner" />
          <div className="loading-text">
            Analyzing {ticker}... Running ML model, computing indicators, fetching news...
          </div>
        </div>
      )}

      {/* Empty State */}
      {!ticker && !loading && (
        <div className="empty-state">
          <div className="empty-icon">📊</div>
          <div className="empty-title">Welcome to StockPulse AI</div>
          <div className="empty-desc">
            Enter a stock ticker above to get AI-powered analysis with
            technical indicators, news sentiment, and Buy/Sell recommendations.
          </div>
        </div>
      )}

      {/* Dashboard Grid */}
      {stockData && (
        <div className="dashboard-grid">
          <StockHeader data={stockData} />
          <StockChart 
            ohlcv={stockData.ohlcv} 
            ranges={RANGES} 
            activeRange={activeRange} 
            onRangeChange={handleRangeChange} 
            focusedPattern={focusedPattern}
            onClearFocus={() => setFocusedPattern(null)}
          />
          <BuySellMeter analysis={analysis} />
          <PatternsPanel patterns={analysis?.patterns} onSelectPattern={(p) => setFocusedPattern(p)} />
          <IndicatorsPanel indicators={indicators} />
          <NewsPanel news={news} />
        </div>
      )}
    </div>
  );
}
