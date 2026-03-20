'use client';

import { useEffect, useState } from 'react';

export default function BuySellMeter({ analysis }) {
  const [animatedScore, setAnimatedScore] = useState(0);

  const score = analysis?.buy_sell?.score ?? 50;
  const confidence = analysis?.buy_sell?.confidence ?? 0;
  const signal = analysis?.buy_sell?.signal ?? 'hold';
  const components = analysis?.buy_sell?.components ?? {};
  const mlDetails = analysis?.buy_sell?.ml_details ?? {};

  useEffect(() => {
    let start = 0;
    const duration = 1200;
    const startTime = performance.now();

    const animate = (currentTime) => {
      const elapsed = currentTime - startTime;
      const progress = Math.min(elapsed / duration, 1);
      // Ease out cubic
      const eased = 1 - Math.pow(1 - progress, 3);
      setAnimatedScore(Math.round(eased * score));
      if (progress < 1) requestAnimationFrame(animate);
    };

    requestAnimationFrame(animate);
  }, [score]);

  const getScoreColor = (s) => {
    if (s >= 75) return '#10b981'; // Strong Buy
    if (s >= 60) return '#34d399'; // Buy
    if (s >= 45) return '#f59e0b'; // Hold
    if (s >= 30) return '#f97316'; // Sell
    return '#ef4444';              // Strong Sell
  };

  const getSignalText = (s) => {
    const map = {
      strong_buy: 'Strong Buy',
      buy: 'Buy',
      hold: 'Hold',
      sell: 'Sell',
      strong_sell: 'Strong Sell',
    };
    return map[s] || 'Hold';
  };

  const color = getScoreColor(animatedScore);

  // SVG arc for semicircle gauge
  const radius = 85;
  const circumference = Math.PI * radius;
  const offset = circumference - (animatedScore / 100) * circumference;

  return (
    <div className="card buy-sell-card fade-in fade-in-delay-2">
      <div className="card-header">
        <span className="card-title">🎯 AI Analysis</span>
        <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
          <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
            Confidence: <strong style={{ color: '#6366f1' }}>{confidence}%</strong>
          </span>
          <span className={`card-badge ${
            score >= 60 ? 'badge-bullish' :
            score >= 45 ? 'badge-neutral' : 'badge-bearish'
          }`}>
            {getSignalText(signal)}
          </span>
        </div>
      </div>

      <div className="meter-container">
        {/* Semicircle Gauge */}
        <div className="meter-gauge">
          <svg viewBox="0 0 200 110">
            {/* Background arc */}
            <path
              d="M 15 100 A 85 85 0 0 1 185 100"
              fill="none"
              stroke="rgba(148, 163, 184, 0.1)"
              strokeWidth="12"
              strokeLinecap="round"
            />
            {/* Colored arc */}
            <path
              d="M 15 100 A 85 85 0 0 1 185 100"
              fill="none"
              stroke={color}
              strokeWidth="12"
              strokeLinecap="round"
              strokeDasharray={`${circumference}`}
              strokeDashoffset={offset}
              style={{
                transition: 'stroke-dashoffset 1.2s cubic-bezier(0.4, 0, 0.2, 1), stroke 0.5s',
                filter: `drop-shadow(0 0 8px ${color}40)`,
              }}
            />
            {/* Tick marks */}
            {[0, 25, 50, 75, 100].map((tick) => {
              const angle = Math.PI - (tick / 100) * Math.PI;
              const x1 = 100 + 73 * Math.cos(angle);
              const y1 = 100 - 73 * Math.sin(angle);
              const x2 = 100 + 80 * Math.cos(angle);
              const y2 = 100 - 80 * Math.sin(angle);
              return (
                <line
                  key={tick}
                  x1={x1} y1={y1} x2={x2} y2={y2}
                  stroke="rgba(148, 163, 184, 0.3)"
                  strokeWidth="1.5"
                />
              );
            })}
            {/* Labels */}
            <text x="8" y="115" fill="#64748b" fontSize="8" fontFamily="Inter">Sell</text>
            <text x="90" y="18" fill="#64748b" fontSize="8" fontFamily="Inter">Hold</text>
            <text x="175" y="115" fill="#64748b" fontSize="8" fontFamily="Inter">Buy</text>
          </svg>
        </div>

        {/* Score */}
        <div className="meter-score" style={{ color }}>{animatedScore}</div>
        <div className="meter-signal" style={{ color }}>{getSignalText(signal)}</div>

        {/* Breakdown */}
        <div className="meter-breakdown">
          <div className="breakdown-item">
            <div className="breakdown-label">ML Model</div>
            <div className="breakdown-value" style={{ color: getScoreColor(components.ml?.score ?? 50) }}>
              {components.ml?.score?.toFixed(0) ?? '—'}
            </div>
            <div className="breakdown-weight">{components.ml?.weight ?? '40%'}</div>
          </div>
          <div className="breakdown-item">
            <div className="breakdown-label">Technical</div>
            <div className="breakdown-value" style={{ color: getScoreColor(components.technical?.score ?? 50) }}>
              {components.technical?.score?.toFixed(0) ?? '—'}
            </div>
            <div className="breakdown-weight">{components.technical?.weight ?? '35%'}</div>
          </div>
          <div className="breakdown-item">
            <div className="breakdown-label">Sentiment</div>
            <div className="breakdown-value" style={{ color: getScoreColor(components.sentiment?.score ?? 50) }}>
              {components.sentiment?.score?.toFixed(0) ?? '—'}
            </div>
            <div className="breakdown-weight">{components.sentiment?.weight ?? '25%'}</div>
          </div>
        </div>

        {/* Value Trap Boost Notification */}
        {mlDetails.value_trap_boost && (
          <div style={{
            marginTop: '16px',
            padding: '8px',
            borderRadius: '8px',
            backgroundColor: 'rgba(52, 211, 153, 0.1)',
            border: '1px solid rgba(52, 211, 153, 0.2)',
            color: '#34d399',
            fontSize: '0.8rem',
            textAlign: 'center',
            fontWeight: 'bold',
          }}>
            🛡️ Value Signal: Stock is down &gt;50% with low RSI and high volume. Buy/Sell Score increased safely!
          </div>
        )}

        {/* Separate News Sentiment Meter */}
        <div style={{ marginTop: '30px', borderTop: '1px solid rgba(148, 163, 184, 0.1)', paddingTop: '20px' }}>
          <div style={{ textAlign: 'center', fontSize: '0.9rem', color: 'var(--text-muted)', marginBottom: '10px' }}>
            News Sentiment Meter
          </div>
          <div className="meter-score" style={{ 
            color: getScoreColor(components.sentiment?.score ?? 50), 
            fontSize: '2.5rem' 
          }}>
            {components.sentiment?.score?.toFixed(0) ?? 50}
          </div>
          <div className="meter-signal" style={{ 
            color: getScoreColor(components.sentiment?.score ?? 50),
            fontSize: '1rem'
          }}>
            {getSignalText(
              (components.sentiment?.score ?? 50) >= 75 ? 'strong_buy' :
              (components.sentiment?.score ?? 50) >= 60 ? 'buy' :
              (components.sentiment?.score ?? 50) >= 45 ? 'hold' :
              (components.sentiment?.score ?? 50) >= 30 ? 'sell' : 'strong_sell'
            )}
          </div>
        </div>

        {/* ML details */}
        {mlDetails.test_accuracy && (
          <div style={{
            marginTop: '16px',
            fontSize: '0.7rem',
            color: 'var(--text-muted)',
            textAlign: 'center',
          }}>
            ML Accuracy: {mlDetails.test_accuracy}% · Direction: {mlDetails.prediction} · Confidence: {mlDetails.confidence}%
          </div>
        )}
      </div>
    </div>
  );
}
