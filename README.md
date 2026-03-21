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

### AWS EC2 (t2.micro) with Docker

1. Launch an **Ubuntu 22.04 t2.micro** instance on AWS.
2. In EC2 Security Groups, allow **HTTP (80)** and **Custom TCP (8000)** traffic.
3. SSH into your instance and install Docker & Docker Compose:
   ```bash
   sudo apt update
   sudo apt install docker.io docker-compose git -y
   sudo usermod -aG docker ubuntu
   # Re-login or run: newgrp docker
   ```
4. Clone your repository:
   ```bash
   git clone <your-repo-url>
   cd <your-repo-folder>
   ```
5. Set your EC2 public IP and start the containers:
   ```bash
   export EC2_PUBLIC_IP="your.ec2.public.ip.here"
   docker-compose up -d --build
   ```
6. Access your dashboard at `http://your.ec2.public.ip.here`

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
| **AWS EC2 t2.micro** | 1GB RAM can be tight for NextJS builds and ML | Docker Compose handles resource isolation, multi-stage NextJS build keeps final image small |

---

## Project Structure

```
timepass/
├── docker-compose.yml           # AWS deployment config
├── backend/
│   ├── Dockerfile
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
│   ├── Dockerfile
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
