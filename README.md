# StockPulse AI — AI-Powered Stock Analysis

A full-stack stock analysis dashboard with technical indicators, news sentiment, and ML-driven Buy/Sell signals.

**100% free** — no paid APIs, no subscriptions.

![Tech Stack](https://img.shields.io/badge/FastAPI-Python-009688?style=flat-square) ![Frontend](https://img.shields.io/badge/Next.js-React-000?style=flat-square) ![ML](https://img.shields.io/badge/ML-Random_Forest-orange?style=flat-square)

---

## Features

- **Live Stock Data** — Real-time prices via Yahoo Finance (yfinance)
- **Price Charts** — Interactive Chart.js with volume overlay
- **Technical Indicators** — RSI, MACD, Moving Averages, Bollinger Bands
- **News Sentiment** — Google News headlines with TextBlob sentiment analysis
- **ML Predictions** — Random Forest classifier predicting price direction
- **Buy/Sell Score** — Composite 0–100 score combining ML (40%), technical (35%), and sentiment (25%)
- **Auto-Polling** — Dashboard refreshes every 10 seconds

---

## Quick Start

### Prerequisites

- **Python 3.9+** & **pip**
- **Node.js 18+** & **npm**

### 1. Backend Setup

```bash
cd backend
pip install -r requirements.txt
python -m textblob.download_corpora
python main.py
```

Backend runs at **http://localhost:8000**

Verify: `curl http://localhost:8000/api/health`

### 2. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at **http://localhost:3000**

### 3. Use the App

1. Open http://localhost:3000
2. Type a ticker (e.g., **RELIANCE.NS**, **TCS.NS**, **HDFCBANK.NS**)
3. Click **Analyze**
4. Dashboard auto-refreshes every 10 seconds

---

## Troubleshooting / Restarting the Application

If you encounter issues like "Could not fetch stock data" or port conflicts, you may need to completely cleanly restart the applications. 

### 1. Stop Existing Servers
If your ports `8000` or `3000` are stuck, run the following in your terminal to kill all Python (`backend`) and Node (`frontend`) processes:

```powershell
taskkill /F /IM python.exe
taskkill /F /IM node.exe
```

### 2. Start Backend Fresh
```bash
cd backend
python -m textblob.download_corpora
python main.py
```

### 3. Start Frontend Fresh
(In a separate terminal)
```bash
cd frontend
npm run dev
```

---

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /api/health` | Health check |
| `GET /api/stock/{ticker}` | Price data + OHLCV history |
| `GET /api/stock/{ticker}/intraday` | 5-minute intraday candles |
| `GET /api/indicators/{ticker}` | RSI, MACD, MAs, Bollinger Bands |
| `GET /api/news/{ticker}` | News headlines with sentiment |
| `GET /api/analysis/{ticker}` | Full AI analysis with Buy/Sell score |

---

## Deployment (Free Tier)

### Backend → Render

1. Push `backend/` to GitHub
2. Create a new **Web Service** on [render.com](https://render.com)
3. Connect your repo, set root directory to `backend`
4. Build command: `pip install -r requirements.txt`
5. Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

### Frontend → Vercel

1. Push `frontend/` to GitHub
2. Import on [vercel.com](https://vercel.com)
3. Set environment variable: `NEXT_PUBLIC_API_URL=https://your-backend.onrender.com`
4. Deploy

---

## Architecture

```
Frontend (Next.js / Vercel)
    ↓ fetch every 10s
Backend (FastAPI / Render)
    ├── yfinance → Stock Data + OHLCV
    ├── ta library → RSI, MACD, MAs, Bollinger
    ├── Google News RSS → Headlines
    ├── TextBlob → Sentiment Scores
    └── scikit-learn RF → ML Predictions
         ↓
    Buy/Sell Score (0-100)
```

---

## Trade-offs

| Free Resource | Limitation | Mitigation |
|---------------|------------|------------|
| **yfinance** | Rate-limited, may break if Yahoo changes HTML | 30s server cache, 10s polling |
| **Google News RSS** | ~10 headlines, no deep search | Sufficient for sentiment signal |
| **TextBlob** | Generic, not finance-tuned | Lightweight; swap for FinBERT in production |
| **Render free tier** | 512MB RAM, spins down after 15min | TextBlob keeps RAM low; cold start ~30s |
| **Vercel free tier** | 100GB bandwidth/mo | Plenty for personal/demo use |

---

## Project Structure

```
timepass/
├── backend/
│   ├── main.py                  # FastAPI app
│   ├── requirements.txt         # Python dependencies
│   ├── render.yaml              # Render config
│   └── services/
│       ├── stock_data.py        # yfinance + caching
│       ├── indicators.py        # RSI, MACD, MAs
│       ├── news.py              # Google News RSS
│       ├── sentiment.py         # TextBlob sentiment
│       └── ml_model.py          # Random Forest + scoring
├── frontend/
│   ├── package.json
│   ├── next.config.js
│   ├── vercel.json
│   └── src/
│       ├── app/
│       │   ├── layout.js
│       │   ├── page.js          # Main dashboard
│       │   └── globals.css      # Design system
│       └── components/
│           ├── StockSearch.js
│           ├── StockHeader.js
│           ├── StockChart.js
│           ├── IndicatorsPanel.js
│           ├── NewsPanel.js
│           └── BuySellMeter.js
└── README.md
```
