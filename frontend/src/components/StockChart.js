'use client';

import { useRef } from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Tooltip,
  Legend,
  TimeScale,
  TimeSeriesScale,
} from 'chart.js';
import { Chart, Bar } from 'react-chartjs-2';
import 'chartjs-adapter-date-fns';
import { CandlestickController, CandlestickElement } from 'chartjs-chart-financial';
import annotationPlugin from 'chartjs-plugin-annotation';

ChartJS.register(
  CategoryScale,
  LinearScale,
  TimeScale,
  TimeSeriesScale,
  BarElement,
  Tooltip,
  Legend,
  CandlestickController,
  CandlestickElement,
  annotationPlugin
);

export default function StockChart({ ohlcv, ranges = [], activeRange = {}, onRangeChange = () => {}, focusedPattern = null, onClearFocus = () => {} }) {
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

  // Format explicitly for chartjs-chart-financial: { x: timestamp, o: open, h: high, l: low, c: close }
  const financialData = ohlcv.map(d => ({
    x: new Date(d.date).getTime(),
    o: d.open,
    h: d.high,
    l: d.low,
    c: d.close,
  }));

  const closes = ohlcv.map(d => d.close);
  const volumes = ohlcv.map(d => d.volume);

  const isUp = closes[closes.length - 1] >= closes[0];

  const priceData = {
    datasets: [
      {
        label: 'Price',
        data: financialData,
        color: {
          up: '#10b981',
          down: '#ef4444',
          unchanged: '#94a3b8',
        },
        borderColor: {
          up: '#10b981',
          down: '#ef4444',
          unchanged: '#94a3b8',
        },
        borderWidth: 1.5,
      },
    ],
  };

  const isIntraday = activeRange?.value === '1d' || activeRange?.value === '5d';

  const priceOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: false },
      annotation: {
        annotations: focusedPattern && focusedPattern.dates && focusedPattern.dates.length > 0 ? {
          patternHighlight: focusedPattern.dates.length > 1 ? {
            type: 'box',
            xMin: new Date(focusedPattern.dates[0]).getTime(),
            xMax: new Date(focusedPattern.dates[focusedPattern.dates.length - 1]).getTime(),
            backgroundColor: focusedPattern.type === 'Bullish' ? 'rgba(16, 185, 129, 0.2)' : 'rgba(239, 68, 68, 0.2)',
            borderColor: focusedPattern.type === 'Bullish' ? '#10b981' : '#ef4444',
            borderWidth: 2,
            drawTime: 'beforeDatasetsDraw',
            label: {
              content: focusedPattern.name,
              position: 'top',
              display: true,
              backgroundColor: focusedPattern.type === 'Bullish' ? '#10b981' : '#ef4444',
              color: '#fff',
            }
          } : {
            type: 'line',
            scaleID: 'x',
            value: new Date(focusedPattern.dates[0]).getTime(),
            borderColor: focusedPattern.type === 'Bullish' ? '#10b981' : '#ef4444',
            borderWidth: 3,
            label: {
              content: focusedPattern.name,
              display: true,
              position: 'top',
              backgroundColor: focusedPattern.type === 'Bullish' ? '#10b981' : '#ef4444',
              color: '#fff',
            }
          }
        } : {}
      },
      tooltip: {
        backgroundColor: 'rgba(17, 24, 39, 0.95)',
        titleColor: '#f1f5f9',
        bodyColor: '#94a3b8',
        borderColor: 'rgba(148, 163, 184, 0.2)',
        borderWidth: 1,
        padding: 12,
        displayColors: false,
        titleFont: { family: 'Inter', size: 12 },
        bodyFont: { family: 'Inter', size: 11 },
        callbacks: {
          label: (ctx) => {
            const p = ctx.raw;
            return [
              `O: ₹${p.o.toFixed(2)}`,
              `H: ₹${p.h.toFixed(2)}`,
              `L: ₹${p.l.toFixed(2)}`,
              `C: ₹${p.c.toFixed(2)}`
            ];
          },
        },
      },
    },
    scales: {
      x: {
        type: 'timeseries',
        time: {
          unit: isIntraday ? 'hour' : 'day',
          displayFormats: {
            hour: 'HH:mm',
            day: 'MMM d'
          }
        },
        grid: { color: 'rgba(148, 163, 184, 0.06)' },
        ticks: {
          color: '#64748b',
          font: { size: 10 },
          maxTicksLimit: 10,
        },
      },
      y: {
        position: 'right',
        grid: { color: 'rgba(148, 163, 184, 0.06)' },
        ticks: {
          color: '#64748b',
          font: { family: 'Inter', size: 10 },
          callback: (val) => `₹${val.toFixed(0)}`,
        },
      },
    },
  };

  // Volume chart uses simple date strings for x-axis as labels to sync roughly
  const labels = ohlcv.map(d => d.date);
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
        padding: 5,
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

  // Build the normal chart card (always rendered cleanly)
  const chartCard = (
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
        <Chart ref={chartRef} type="candlestick" data={priceData} options={priceOptions} />
      </div>
      <div style={{ height: '60px', marginTop: '8px' }}>
        <Bar data={volumeData} options={volumeOptions} />
      </div>
    </div>
  );

  // Pattern focus overlay — rendered as a SEPARATE sibling, never touches the card
  const patternOverlay = focusedPattern ? (
    <div style={{
      position: 'fixed',
      top: 0, left: 0, right: 0, bottom: 0,
      backgroundColor: 'rgba(2, 6, 23, 0.92)',
      backdropFilter: 'blur(12px)',
      zIndex: 9999,
      display: 'flex',
      flexDirection: 'column',
      justifyContent: 'center',
      alignItems: 'center',
      padding: '30px',
      animation: 'fadeIn 0.3s ease'
    }}>
      {/* Close button */}
      <button 
        onClick={onClearFocus}
        style={{
          position: 'absolute',
          top: '24px',
          right: '32px',
          background: 'rgba(239, 68, 68, 0.15)',
          color: '#f87171',
          border: '1px solid rgba(239, 68, 68, 0.3)',
          padding: '8px 20px',
          borderRadius: '8px',
          cursor: 'pointer',
          fontWeight: '600',
          zIndex: 10000,
          fontSize: '0.9rem',
          transition: 'all 0.2s',
        }}
        onMouseOver={(e) => { e.currentTarget.style.background = '#ef4444'; e.currentTarget.style.color = '#fff'; }}
        onMouseOut={(e) => { e.currentTarget.style.background = 'rgba(239, 68, 68, 0.15)'; e.currentTarget.style.color = '#f87171'; }}
      >
        ✖ Exit Pattern View
      </button>

      {/* Pattern title */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        gap: '12px',
        marginBottom: '20px',
      }}>
        <span style={{ fontSize: '1.4rem', fontWeight: '700', color: '#f1f5f9' }}>
          🔍 {focusedPattern.name}
        </span>
        <span style={{
          padding: '4px 12px',
          borderRadius: '20px',
          fontSize: '0.75rem',
          fontWeight: '600',
          background: focusedPattern.type === 'Bullish' ? 'rgba(16, 185, 129, 0.15)' : 'rgba(239, 68, 68, 0.15)',
          color: focusedPattern.type === 'Bullish' ? '#10b981' : '#ef4444',
          border: `1px solid ${focusedPattern.type === 'Bullish' ? 'rgba(16, 185, 129, 0.3)' : 'rgba(239, 68, 68, 0.3)'}`,
        }}>
          {focusedPattern.type} • {Math.round(focusedPattern.confidence * 100)}%
        </span>
      </div>

      {/* Modal chart */}
      <div style={{
        width: '85%',
        maxWidth: '1200px',
        height: '65vh',
        background: 'rgba(15, 23, 42, 0.6)',
        border: '1px solid rgba(148, 163, 184, 0.1)',
        borderRadius: '16px',
        padding: '20px',
        boxShadow: '0 25px 60px rgba(0, 0, 0, 0.5)',
      }}>
        <Chart type="candlestick" data={priceData} options={priceOptions} />
      </div>

      {/* Volume in modal */}
      <div style={{ width: '85%', maxWidth: '1200px', height: '50px', marginTop: '8px' }}>
        <Bar data={volumeData} options={volumeOptions} />
      </div>
    </div>
  ) : null;

  return (
    <>
      {chartCard}
      {patternOverlay}
    </>
  );
}
