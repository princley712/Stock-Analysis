'use client';

export default function StockHeader({ data }) {
  if (!data) return null;

  const isPositive = data.change >= 0;
  const arrow = isPositive ? '▲' : '▼';

  const formatNumber = (num) => {
    if (!num) return '—';
    if (num >= 1e7) return `₹${(num / 1e7).toFixed(2)}Cr`;
    if (num >= 1e5) return `₹${(num / 1e5).toFixed(2)}L`;
    return `₹${num.toLocaleString('en-IN')}`;
  };

  const formatVolume = (num) => {
    if (!num) return '—';
    if (num >= 1e9) return `${(num / 1e9).toFixed(1)}B`;
    if (num >= 1e6) return `${(num / 1e6).toFixed(1)}M`;
    if (num >= 1e3) return `${(num / 1e3).toFixed(1)}K`;
    return num.toLocaleString();
  };

  return (
    <div className="card stock-header-card fade-in">
      <div className="stock-info">
        <div className="stock-main">
          <div className="stock-ticker">{data.ticker}</div>
          <div className="stock-name">{data.name} · {data.exchange}</div>
          <div>
            <span className="stock-price">
              {data.currency === 'INR' ? '₹' : '$'}{data.current_price?.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
            </span>
            <span className={`stock-change ${isPositive ? 'positive' : 'negative'}`}>
              {arrow} {Math.abs(data.change)?.toFixed(2)} ({Math.abs(data.change_percent)?.toFixed(2)}%)
            </span>
          </div>
        </div>
        <div className="stock-meta">
          <div className="meta-item">
            <div className="meta-label">Volume</div>
            <div className="meta-value">{formatVolume(data.volume)}</div>
          </div>
          <div className="meta-item">
            <div className="meta-label">Market Cap</div>
            <div className="meta-value">{formatNumber(data.market_cap)}</div>
          </div>
          <div className="meta-item">
            <div className="meta-label">52W High</div>
            <div className="meta-value">₹{data.fifty_two_week_high?.toFixed(2)}</div>
          </div>
          <div className="meta-item">
            <div className="meta-label">52W Low</div>
            <div className="meta-value">₹{data.fifty_two_week_low?.toFixed(2)}</div>
          </div>
        </div>
      </div>
    </div>
  );
}
