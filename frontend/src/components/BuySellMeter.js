'use client';

import { useEffect, useState, useMemo } from 'react';

export default function BuySellMeter({ analysis }) {
  const [animatedScore, setAnimatedScore] = useState(0);
  const [activeTab, setActiveTab] = useState('medium_term');

  // Parse horizons from backend response
  const horizons = useMemo(() => {
    return analysis?.buy_sell || {};
  }, [analysis]);

  // Determine initial active tab based on highest confidence
  useEffect(() => {
    if (Object.keys(horizons).length > 0) {
      let bestTab = 'medium_term';
      let maxConf = -1;
      for (const [key, data] of Object.entries(horizons)) {
        if (data.confidence > maxConf) {
          maxConf = data.confidence;
          bestTab = key;
        }
      }
      setActiveTab(bestTab);
    }
  }, [horizons]);

  // Extract currently active data
  const currentData = horizons[activeTab] || {};
  const score = currentData.score ?? 50;
  const confidence = currentData.confidence ?? 0;
  const signal = currentData.signal ?? 'hold';
  const components = currentData.components ?? {};
  const mlDetails = currentData.ml_details ?? {};
  const timeframeName = currentData.name ?? 'Analysis';

  useEffect(() => {
    let start = 0;
    const duration = 800;
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
  }, [score, activeTab]);

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
      <div className="card-header" style={{ flexDirection: 'column', alignItems: 'flex-start', gap: '12px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', width: '100%', alignItems: 'center' }}>
          <span className="card-title">🎯 AI Signals</span>
          <span className={`card-badge ${
            score >= 60 ? 'badge-bullish' :
            score >= 45 ? 'badge-neutral' : 'badge-bearish'
          }`}>
            {getSignalText(signal)}
          </span>
        </div>

        {/* Timeframe Tabs */}
        {Object.keys(horizons).length > 0 && (
          <div style={{ display: 'flex', gap: '8px', width: '100%', background: 'rgba(15, 23, 42, 0.4)', padding: '4px', borderRadius: '8px' }}>
            {Object.entries(horizons).map(([key, data]) => {
              const isActive = activeTab === key;
              return (
                <button
                  key={key}
                  onClick={() => setActiveTab(key)}
                  style={{
                    flex: 1,
                    background: isActive ? '#6366f1' : 'transparent',
                    color: isActive ? '#fff' : '#94a3b8',
                    border: isActive ? '1px solid #818cf8' : '1px solid transparent',
                    padding: '6px 8px',
                    fontSize: '0.75rem',
                    borderRadius: '6px',
                    cursor: 'pointer',
                    fontWeight: isActive ? '600' : '400',
                    transition: 'all 0.2s',
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'center',
                    gap: '2px'
                  }}
                >
                  <span style={{ fontSize: '0.8rem' }}>{data.name.split(' ')[0]}</span>
                  <span style={{ fontSize: '0.65rem', opacity: 0.8 }}>Conf: {data.confidence}%</span>
                </button>
              );
            })}
          </div>
        )}
      </div>

      <div className="meter-container" style={{ marginTop: '10px' }}>
        <div style={{ textAlign: 'center', fontSize: '0.9rem', color: '#818cf8', fontWeight: '500', marginBottom: '10px' }}>
          {timeframeName} Outlook
        </div>
        
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
                transition: 'stroke-dashoffset 0.8s cubic-bezier(0.4, 0, 0.2, 1), stroke 0.5s',
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
        <div className="meter-signal" style={{ color }}>{getSignalText(signal)} ({timeframeName.split(' ')[0]})</div>

        {/* Breakdown */}
        <div className="meter-breakdown">
          <div className="breakdown-item">
            <div className="breakdown-label">ML Model</div>
            <div className="breakdown-value" style={{ color: getScoreColor(components.ml?.score ?? 50) }}>
              {components.ml?.score?.toFixed(0) ?? '—'}
            </div>
            <div className="breakdown-weight">{components.ml?.weight ?? '-'}</div>
          </div>
          <div className="breakdown-item">
            <div className="breakdown-label">Technical</div>
            <div className="breakdown-value" style={{ color: getScoreColor(components.technical?.score ?? 50) }}>
              {components.technical?.score?.toFixed(0) ?? '—'}
            </div>
            <div className="breakdown-weight">{components.technical?.weight ?? '-'}</div>
          </div>
          <div className="breakdown-item">
            <div className="breakdown-label">Sentiment</div>
            <div className="breakdown-value" style={{ color: getScoreColor(components.sentiment?.score ?? 50) }}>
              {components.sentiment?.score?.toFixed(0) ?? '—'}
            </div>
            <div className="breakdown-weight">{components.sentiment?.weight ?? '-'}</div>
          </div>
          <div className="breakdown-item">
            <div className="breakdown-label">Patterns</div>
            <div className="breakdown-value" style={{ color: getScoreColor(components.patterns?.score ?? 50) }}>
              {components.patterns?.score?.toFixed(0) ?? '—'}
            </div>
            <div className="breakdown-weight">{components.patterns?.weight ?? '-'}</div>
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
            🛡️ Deep Value Found: Stock is heavily oversold. Added safe rebound premium.
          </div>
        )}

        {/* ML details */}
        {mlDetails.test_accuracy && (
          <div style={{
            marginTop: '16px',
            fontSize: '0.75rem',
            color: 'var(--text-muted)',
            textAlign: 'center',
            background: 'rgba(15, 23, 42, 0.3)',
            padding: '8px',
            borderRadius: '6px'
          }}>
            <strong>AI Confidence: {confidence}%</strong><br/>
            Next Phase Prediction: <span style={{ color: mlDetails.prediction === 'buy' ? '#34d399' : mlDetails.prediction === 'sell' ? '#ef4444' : '#f59e0b' }}>{mlDetails.prediction.toUpperCase()}</span>
          </div>
        )}
      </div>
    </div>
  );
}
