"""
AI-Powered Stock Analysis API
FastAPI backend serving stock data, technical indicators, news sentiment, and ML predictions.
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from services.stock_data import get_stock_data, get_intraday_data, get_historical_data
from services.indicators import compute_indicators, get_technical_score
from services.news import fetch_news
from services.sentiment import analyze_news_sentiment
from services.ml_model import train_and_predict, compute_buy_sell_score


app = FastAPI(
    title="StockPulse AI",
    description="AI-powered stock analysis with technical indicators, sentiment, and ML predictions",
    version="1.0.0",
)

# CORS — allow frontend origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "service": "StockPulse AI"}


@app.get("/api/stock/{ticker}")
async def get_stock(ticker: str, period: str = "6mo", interval: str = "1d"):
    """
    Get stock price data and OHLCV history.
    Returns current price, change, volume, and candlestick data.
    """
    data = get_stock_data(ticker.upper(), period=period, interval=interval)
    if "error" in data and "ohlcv" not in data:
        raise HTTPException(status_code=404, detail=data["error"])
    return data


@app.get("/api/stock/{ticker}/intraday")
async def get_stock_intraday(ticker: str):
    """Get intraday data (5-minute candles, last 5 days)."""
    data = get_intraday_data(ticker.upper())
    if "error" in data and "ohlcv" not in data:
        raise HTTPException(status_code=404, detail=data["error"])
    return data


@app.get("/api/indicators/{ticker}")
async def get_indicators(ticker: str):
    """
    Get technical indicators for a stock.
    Returns RSI, MACD, Moving Averages, Bollinger Bands, and volume analysis.
    """
    df = get_historical_data(ticker.upper(), period="6mo")
    if df.empty:
        raise HTTPException(status_code=404, detail=f"No historical data for {ticker}")

    indicators = compute_indicators(df)
    if "error" in indicators:
        raise HTTPException(status_code=400, detail=indicators["error"])

    return indicators


@app.get("/api/news/{ticker}")
async def get_news(ticker: str):
    """
    Get news articles with sentiment analysis for a stock.
    Returns headlines from Google News with TextBlob sentiment scores.
    """
    articles = fetch_news(ticker.upper())
    result = analyze_news_sentiment(articles)
    return result


@app.get("/api/analysis/{ticker}")
async def get_full_analysis(ticker: str):
    """
    Full AI analysis: combines stock data, indicators, sentiment, and ML prediction
    into a Buy/Sell score (0-100).
    """
    ticker = ticker.upper()

    # 1. Get historical data
    df = get_historical_data(ticker, period="6mo")
    if df.empty:
        raise HTTPException(status_code=404, detail=f"No data found for {ticker}")

    # 2. Compute technical indicators
    indicators = compute_indicators(df)
    tech_dict = get_technical_score(indicators) if "error" not in indicators else {"score": 50.0, "confidence": 0.0}
    technical_score = tech_dict["score"]
    technical_confidence = tech_dict["confidence"]

    # 3. Get news sentiment
    articles = fetch_news(ticker)
    sentiment = analyze_news_sentiment(articles)
    sentiment_score = sentiment["aggregate"]["score"]
    sentiment_confidence = sentiment["aggregate"]["confidence"]

    # 4. ML prediction
    ml_result = train_and_predict(df)

    # 5. Composite Buy/Sell score
    buy_sell = compute_buy_sell_score(
        ml_result, 
        technical_score, technical_confidence, 
        sentiment_score, sentiment_confidence, 
        df
    )

    return {
        "ticker": ticker,
        "buy_sell": buy_sell,
        "indicators": indicators if "error" not in indicators else None,
        "sentiment": sentiment["aggregate"],
        "news_count": len(sentiment["articles"]),
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
