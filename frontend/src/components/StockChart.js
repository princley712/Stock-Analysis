'use client';

import { useRef, useEffect } from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Filler,
  Tooltip,
  Legend,
} from 'chart.js';
import { Line, Bar } from 'react-chartjs-2';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Filler,
  Tooltip,
  Legend
);

export default function StockChart({ ohlcv, ranges = [], activeRange = {}, onRangeChange = () => {} }) {
  const chartRef = useRef(null);

  if (!ohlcv || ohlcv.length === 0) {
    return (
      <div className="card chart-card fade-in fade-in-delay-1">
        <div className="card-header">
          <span className="card-title">📈 Price Chart</span>
        </div>
        <div style={{ textAlign: 'center', padding: '60px 0', color: 'var(--text-muted)' }}>
          No chart data available
        </div>
      </div>
    );
  }

  const labels = ohlcv.map(d => {
    const parts = d.date.split(' ');
    return parts[0].slice(5); // MM-DD
  });
  const closes = ohlcv.map(d => d.close);
  const volumes = ohlcv.map(d => d.volume);

  const isUp = closes[closes.length - 1] >= closes[0];
  const lineColor = isUp ? '#10b981' : '#ef4444';
  const fillColor = isUp ? 'rgba(16, 185, 129, 0.08)' : 'rgba(239, 68, 68, 0.08)';

  const priceData = {
    labels,
    datasets: [
      {
        label: 'Close Price',
        data: closes,
        borderColor: lineColor,
        backgroundColor: fillColor,
        borderWidth: 2,
        fill: true,
        tension: 0.3,
        pointRadius: 0,
        pointHoverRadius: 5,
        pointHoverBackgroundColor: lineColor,
        pointHoverBorderColor: '#fff',
        pointHoverBorderWidth: 2,
      },
    ],
  };

  const priceOptions = {
    responsive: true,
    maintainAspectRatio: false,
    interaction: {
      mode: 'index',
      intersect: false,
    },
    plugins: {
      legend: { display: false },
      tooltip: {
        backgroundColor: 'rgba(17, 24, 39, 0.95)',
        titleColor: '#f1f5f9',
        bodyColor: '#94a3b8',
        borderColor: 'rgba(148, 163, 184, 0.2)',
        borderWidth: 1,
        padding: 12,
        displayColors: false,
        titleFont: { family: 'JetBrains Mono', size: 12 },
        bodyFont: { family: 'JetBrains Mono', size: 11 },
        callbacks: {
          label: (ctx) => `₹${ctx.parsed.y.toFixed(2)}`,
        },
      },
    },
    scales: {
      x: {
        grid: { color: 'rgba(148, 163, 184, 0.06)' },
        ticks: {
          color: '#64748b',
          font: { size: 10 },
          maxTicksLimit: 12,
        },
      },
      y: {
        position: 'right',
        grid: { color: 'rgba(148, 163, 184, 0.06)' },
        ticks: {
          color: '#64748b',
          font: { family: 'JetBrains Mono', size: 10 },
          callback: (val) => `₹${val.toFixed(0)}`,
        },
      },
    },
  };

  // Volume chart
  const maxVolume = Math.max(...volumes);
  const volumeData = {
    labels,
    datasets: [
      {
        label: 'Volume',
        data: volumes,
        backgroundColor: volumes.map((_, i) =>
          i > 0 && closes[i] >= closes[i - 1]
            ? 'rgba(16, 185, 129, 0.35)'
            : 'rgba(239, 68, 68, 0.35)'
        ),
        borderRadius: 2,
      },
    ],
  };

  const volumeOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: false },
      tooltip: {
        backgroundColor: 'rgba(17, 24, 39, 0.95)',
        titleColor: '#f1f5f9',
        bodyColor: '#94a3b8',
        borderColor: 'rgba(148, 163, 184, 0.2)',
        borderWidth: 1,
        padding: 10,
        displayColors: false,
        callbacks: {
          label: (ctx) => {
            const v = ctx.parsed.y;
            if (v >= 1e6) return `${(v / 1e6).toFixed(1)}M`;
            if (v >= 1e3) return `${(v / 1e3).toFixed(0)}K`;
            return v.toString();
          },
        },
      },
    },
    scales: {
      x: {
        display: false,
      },
      y: {
        display: false,
        max: maxVolume * 2,
      },
    },
  };

  return (
    <div className="card chart-card fade-in fade-in-delay-1">
      <div className="card-header" style={{ flexWrap: 'wrap', gap: '10px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <span className="card-title">📈 Price Chart</span>
          <span className={`card-badge ${isUp ? 'badge-bullish' : 'badge-bearish'}`}>
            {isUp ? 'Trending Up' : 'Trending Down'}
          </span>
        </div>

        {ranges.length > 0 && (
          <div style={{ display: 'flex', gap: '4px', background: 'rgba(15, 23, 42, 0.4)', padding: '4px', borderRadius: '6px' }}>
            {ranges.map((r) => (
              <button
                key={r.value}
                onClick={() => onRangeChange(r)}
                style={{
                  background: activeRange.value === r.value ? '#6366f1' : 'transparent',
                  color: activeRange.value === r.value ? '#fff' : '#64748b',
                  border: 'none',
                  padding: '4px 8px',
                  fontSize: '0.75rem',
                  borderRadius: '4px',
                  cursor: 'pointer',
                  fontWeight: activeRange.value === r.value ? '600' : '400',
                  transition: 'all 0.2s',
                }}
              >
                {r.label}
              </button>
            ))}
          </div>
        )}
      </div>
      <div className="chart-container">
        <Line ref={chartRef} data={priceData} options={priceOptions} />
      </div>
      <div style={{ height: '60px', marginTop: '8px' }}>
        <Bar data={volumeData} options={volumeOptions} />
      </div>
    </div>
  );
}
