"""
Stock data service using yfinance.
Fetches OHLCV data with in-memory caching to minimize API calls.
"""
import time

import yfinance as yf
import pandas as pd

# In-memory cache: { ticker: { "data": ..., "info": ..., "timestamp": ... } }
_cache = {}
CACHE_TTL = 30  # seconds


def get_stock_data(ticker: str, period: str = "1mo", interval: str = "1d") -> dict:
    """
    Fetch OHLCV data for a ticker. Returns dict with price history and stock info.
    Uses a 30-second cache to avoid hammering Yahoo Finance.
    """
    cache_key = f"{ticker}_{period}_{interval}"
    now = time.time()

    if cache_key in _cache and (now - _cache[cache_key]["timestamp"]) < CACHE_TTL:
        return _cache[cache_key]["data"]

    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period=period, interval=interval)

        if hist.empty:
            return {"error": f"No data found for {ticker}"}

        # Try to get stock info with a strict timeout to avoid hanging
        import concurrent.futures
        info = {}
        executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
        future = executor.submit(lambda: stock.info)
        try:
            # 3 second timeout for info fetching
            fetched_info = future.result(timeout=3)
            if isinstance(fetched_info, dict):
                info = fetched_info
        except Exception as e:
            print(f"yfinance info fetch timed out/failed for {ticker}: {e}")
        finally:
            executor.shutdown(wait=False)
        
        # Fallbacks for price data if info fails or is missing
        current_price = info.get("currentPrice") or info.get("regularMarketPrice")
        if not current_price and not hist.empty:
            current_price = float(hist["Close"].iloc[-1])
            
        previous_close = info.get("previousClose") or info.get("regularMarketPreviousClose")
        if not previous_close and len(hist) > 1:
            previous_close = float(hist["Close"].iloc[-2])
        elif not previous_close and not hist.empty:
            # Fallback to Open if we only have 1 day of data
            previous_close = float(hist["Open"].iloc[0])
            
        current_price = current_price or 0.0
        previous_close = previous_close or 0.0

        change = current_price - previous_close if current_price and previous_close else 0
        change_pct = (change / previous_close * 100) if previous_close else 0

        # Format OHLCV data
        ohlcv = []
        for idx, row in hist.iterrows():
            ohlcv.append({
                "date": idx.strftime("%Y-%m-%d %H:%M"),
                "open": round(float(row["Open"]), 2),
                "high": round(float(row["High"]), 2),
                "low": round(float(row["Low"]), 2),
                "close": round(float(row["Close"]), 2),
                "volume": int(row["Volume"]),
            })

        # Calculate 52-week values if missing (roughly 252 trading days)
        # We might not have 252 days in this hist request, but return what we have
        high_52 = info.get("fiftyTwoWeekHigh", round(float(hist["High"].max()), 2) if not hist.empty else 0)
        low_52 = info.get("fiftyTwoWeekLow", round(float(hist["Low"].min()), 2) if not hist.empty else 0)

        result = {
            "ticker": ticker.upper(),
            "name": info.get("shortName", ticker.upper()),
            "current_price": round(current_price, 2),
            "previous_close": round(previous_close, 2),
            "change": round(change, 2),
            "change_percent": round(change_pct, 2),
            "volume": info.get("volume", int(hist["Volume"].iloc[-1]) if not hist.empty else 0),
            "market_cap": info.get("marketCap", 0),
            "fifty_two_week_high": high_52,
            "fifty_two_week_low": low_52,
            "currency": info.get("currency", "USD"),
            "exchange": info.get("exchange", ""),
            "ohlcv": ohlcv,
        }

        _cache[cache_key] = {"data": result, "timestamp": now}
        return result

    except Exception as e:
        return {"error": str(e), "ticker": ticker.upper()}


def get_intraday_data(ticker: str) -> dict:
    """Fetch intraday data (5-minute candles for last 5 days)."""
    return get_stock_data(ticker, period="5d", interval="5m")


def get_historical_data(ticker: str, period: str = "6mo") -> pd.DataFrame:
    """
    Return raw DataFrame for use in technical indicators and ML model.
    """
    cache_key = f"{ticker}_df_{period}"
    now = time.time()

    if cache_key in _cache and (now - _cache[cache_key]["timestamp"]) < CACHE_TTL:
        return _cache[cache_key]["data"]

    try:
        stock = yf.Ticker(ticker)
        df = stock.history(period=period, interval="1d")

        if not df.empty:
            _cache[cache_key] = {"data": df, "timestamp": now}

        return df
    except Exception:
        return pd.DataFrame()
