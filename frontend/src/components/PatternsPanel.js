'use client';

export default function PatternsPanel({ patterns, onSelectPattern }) {
  if (!patterns || patterns.length === 0) {
    return (
      <div className="card fade-in fade-in-delay-3">
        <div className="card-header">
          <span className="card-title">🔍 Detected Patterns</span>
        </div>
        <div style={{ padding: '30px', textAlign: 'center', color: 'var(--text-muted)' }}>
          No significant classic chart or candlestick patterns detected recently.
        </div>
      </div>
    );
  }

  return (
    <div className="card fade-in fade-in-delay-3">
      <div className="card-header">
        <span className="card-title">🔍 Detected Patterns (Click to View)</span>
        <span className="card-badge badge-neutral">{patterns.length} Active</span>
      </div>

      <div style={{ padding: '20px', display: 'flex', flexDirection: 'column', gap: '12px' }}>
        {patterns.map((p, idx) => (
          <div 
            key={idx} 
            onClick={() => onSelectPattern && onSelectPattern(p)}
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              padding: '16px',
              borderRadius: '8px',
              background: 'rgba(15, 23, 42, 0.4)',
              borderLeft: p.type === 'Bullish' ? '4px solid #10b981' : '4px solid #ef4444',
              cursor: 'pointer',
              transition: 'transform 0.2s'
            }}
            onMouseOver={(e) => e.currentTarget.style.transform = 'scale(1.02)'}
            onMouseOut={(e) => e.currentTarget.style.transform = 'scale(1)'}
          >
            <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
              <strong style={{ fontSize: '1rem', color: '#f8fafc' }}>{p.name}</strong>
              <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                Classification: {p.type === 'Bullish' ? '🟢 Bullish' : '🔴 Bearish'}
              </span>
            </div>
            
            <div style={{ textAlign: 'right' }}>
              <div style={{ fontSize: '1.2rem', fontWeight: 'bold', color: '#6366f1' }}>
                {Math.round(p.confidence * 100)}%
              </div>
              <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>Confidence</div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
