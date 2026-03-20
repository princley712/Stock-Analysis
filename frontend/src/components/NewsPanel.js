'use client';

export default function NewsPanel({ news }) {
  const articles = news?.articles || [];
  const aggregate = news?.aggregate || {};

  const total = (aggregate.positive_count || 0) + (aggregate.negative_count || 0) + (aggregate.neutral_count || 0);

  return (
    <div className="card news-card fade-in fade-in-delay-3">
      <div className="card-header">
        <span className="card-title">📰 News & Sentiment</span>
        {aggregate.label && (
          <span className={`card-badge ${
            aggregate.label === 'positive' ? 'badge-bullish' :
            aggregate.label === 'negative' ? 'badge-bearish' : 'badge-neutral'
          }`}>
            {aggregate.label}
          </span>
        )}
      </div>

      {/* Sentiment Summary */}
      {total > 0 && (
        <div className="sentiment-summary" style={{ marginBottom: '20px' }}>
          <div className="sentiment-score-ring">
            <svg viewBox="0 0 100 100">
              <circle
                cx="50" cy="50" r="42"
                fill="none"
                stroke="rgba(148, 163, 184, 0.1)"
                strokeWidth="6"
              />
              <circle
                cx="50" cy="50" r="42"
                fill="none"
                stroke={
                  aggregate.score >= 60 ? '#10b981' :
                  aggregate.score >= 40 ? '#f59e0b' : '#ef4444'
                }
                strokeWidth="6"
                strokeDasharray={`${(aggregate.score / 100) * 264} 264`}
                strokeLinecap="round"
              />
            </svg>
            <div className="sentiment-score-text">
              <span className="sentiment-score-value" style={{
                color: aggregate.score >= 60 ? '#10b981' :
                       aggregate.score >= 40 ? '#f59e0b' : '#ef4444'
              }}>
                {Math.round(aggregate.score)}
              </span>
              <span className="sentiment-score-label">Sentiment</span>
            </div>
          </div>
          <div className="sentiment-bars">
            <div className="sentiment-bar-row">
              <span className="sentiment-bar-label">Positive</span>
              <div className="sentiment-bar-track">
                <div
                  className="sentiment-bar-fill"
                  style={{
                    width: `${total > 0 ? (aggregate.positive_count / total * 100) : 0}%`,
                    background: '#10b981',
                  }}
                />
              </div>
              <span className="sentiment-bar-count">{aggregate.positive_count || 0}</span>
            </div>
            <div className="sentiment-bar-row">
              <span className="sentiment-bar-label">Neutral</span>
              <div className="sentiment-bar-track">
                <div
                  className="sentiment-bar-fill"
                  style={{
                    width: `${total > 0 ? (aggregate.neutral_count / total * 100) : 0}%`,
                    background: '#f59e0b',
                  }}
                />
              </div>
              <span className="sentiment-bar-count">{aggregate.neutral_count || 0}</span>
            </div>
            <div className="sentiment-bar-row">
              <span className="sentiment-bar-label">Negative</span>
              <div className="sentiment-bar-track">
                <div
                  className="sentiment-bar-fill"
                  style={{
                    width: `${total > 0 ? (aggregate.negative_count / total * 100) : 0}%`,
                    background: '#ef4444',
                  }}
                />
              </div>
              <span className="sentiment-bar-count">{aggregate.negative_count || 0}</span>
            </div>
          </div>
        </div>
      )}

      {/* News List */}
      <div className="news-list">
        {articles.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '40px 0', color: 'var(--text-muted)' }}>
            No news available
          </div>
        ) : (
          articles.map((article, i) => (
            <a
              key={i}
              href={article.link}
              target="_blank"
              rel="noopener noreferrer"
              className="news-item"
              id={`news-item-${i}`}
            >
              <div className="news-title">{article.title}</div>
              <div className="news-meta">
                <span className="news-source">
                  {article.source} {article.published ? `· ${article.published}` : ''}
                </span>
                {article.sentiment && (
                  <span className={`news-sentiment-badge sentiment-${article.sentiment.label}`}>
                    {article.sentiment.label}
                    {' '}
                    {article.sentiment.polarity > 0 ? '+' : ''}{article.sentiment.polarity.toFixed(2)}
                  </span>
                )}
              </div>
            </a>
          ))
        )}
      </div>
    </div>
  );
}
