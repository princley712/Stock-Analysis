'use client';

export default function IndicatorsPanel({ indicators }) {
  if (!indicators) {
    return (
      <div className="card indicators-card fade-in fade-in-delay-2">
        <div className="card-header">
          <span className="card-title">📊 Technical Indicators</span>
        </div>
        <div style={{ textAlign: 'center', padding: '40px 0', color: 'var(--text-muted)' }}>
          No indicator data
        </div>
      </div>
    );
  }

  const { rsi, macd, moving_averages, bollinger_bands, volume } = indicators;

  const getSignalColor = (signal) => {
    if (['bullish', 'oversold', 'high'].includes(signal)) return 'positive';
    if (['bearish', 'overbought'].includes(signal)) return 'negative';
    return '';
  };

  return (
    <div className="card indicators-card fade-in fade-in-delay-2">
      <div className="card-header">
        <span className="card-title">📊 Technical Indicators</span>
        <span className={`card-badge ${
          moving_averages?.signal === 'bullish' ? 'badge-bullish' :
          moving_averages?.signal === 'bearish' ? 'badge-bearish' : 'badge-neutral'
        }`}>
          {moving_averages?.signal || 'neutral'}
        </span>
      </div>
      <div className="indicators-grid">
        {/* RSI */}
        <div className="indicator-item">
          <div className="indicator-label">RSI (14)</div>
          <div className={`indicator-value ${getSignalColor(rsi?.signal)}`}>
            {rsi?.value ?? '—'}
          </div>
          <div className={`indicator-signal ${getSignalColor(rsi?.signal)}`}>
            {rsi?.signal ?? 'neutral'}
          </div>
        </div>

        {/* MACD */}
        <div className="indicator-item">
          <div className="indicator-label">MACD</div>
          <div className={`indicator-value ${getSignalColor(macd?.signal)}`}>
            {macd?.macd ?? '—'}
          </div>
          <div className={`indicator-signal ${getSignalColor(macd?.signal)}`}>
            {macd?.signal ?? 'neutral'}
          </div>
        </div>

        {/* SMA 20 */}
        <div className="indicator-item">
          <div className="indicator-label">SMA 20</div>
          <div className="indicator-value">
            ₹{moving_averages?.sma_20 ?? '—'}
          </div>
          <div className={`indicator-signal ${
            moving_averages?.price > moving_averages?.sma_20 ? 'positive' : 'negative'
          }`}>
            {moving_averages?.price > moving_averages?.sma_20 ? 'Above' : 'Below'}
          </div>
        </div>

        {/* SMA 50 */}
        <div className="indicator-item">
          <div className="indicator-label">SMA 50</div>
          <div className="indicator-value">
            ₹{moving_averages?.sma_50 ?? '—'}
          </div>
          <div className={`indicator-signal ${
            moving_averages?.price > moving_averages?.sma_50 ? 'positive' : 'negative'
          }`}>
            {moving_averages?.price > moving_averages?.sma_50 ? 'Above' : 'Below'}
          </div>
        </div>

        {/* Bollinger Bands */}
        <div className="indicator-item">
          <div className="indicator-label">Bollinger</div>
          <div className={`indicator-value ${getSignalColor(bollinger_bands?.signal)}`}>
            {bollinger_bands?.signal ?? '—'}
          </div>
          <div className="indicator-signal" style={{ color: 'var(--text-muted)', fontSize: '0.65rem' }}>
            {bollinger_bands?.lower} — {bollinger_bands?.upper}
          </div>
        </div>

        {/* Volume */}
        <div className="indicator-item">
          <div className="indicator-label">Volume Ratio</div>
          <div className={`indicator-value ${getSignalColor(volume?.signal)}`}>
            {volume?.ratio ?? '—'}x
          </div>
          <div className={`indicator-signal ${getSignalColor(volume?.signal)}`}>
            {volume?.signal ?? 'normal'}
          </div>
        </div>
      </div>
    </div>
  );
}
