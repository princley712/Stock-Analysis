"""
Technical indicators service.
Computes RSI, MACD, Moving Averages, Bollinger Bands using the `ta` library.
"""
import math

import numpy as np
import pandas as pd
import ta


def compute_indicators(df: pd.DataFrame) -> dict:
    """
    Given an OHLCV DataFrame, compute all technical indicators.
    Returns a dict with indicator values and buy/sell signals.
    """
    if df.empty or len(df) < 30:
        return {"error": "Insufficient data for indicator calculation"}

    close = df["Close"]
    high = df["High"]
    low = df["Low"]
    volume = df["Volume"]

    # --- RSI (14-period) ---
    rsi_indicator = ta.momentum.RSIIndicator(close=close, window=14)
    rsi_values = rsi_indicator.rsi()
    current_rsi = round(float(rsi_values.iloc[-1]), 2) if not rsi_values.empty else 50

    rsi_signal = "neutral"
    if current_rsi > 70:
        rsi_signal = "overbought"
    elif current_rsi < 30:
        rsi_signal = "oversold"

    # --- MACD (12, 26, 9) ---
    macd_indicator = ta.trend.MACD(close=close, window_slow=26, window_fast=12, window_sign=9)
    macd_line = macd_indicator.macd()
    signal_line = macd_indicator.macd_signal()
    macd_hist = macd_indicator.macd_diff()

    current_macd = round(float(macd_line.iloc[-1]), 4) if not macd_line.empty else 0
    current_signal = round(float(signal_line.iloc[-1]), 4) if not signal_line.empty else 0
    current_hist = round(float(macd_hist.iloc[-1]), 4) if not macd_hist.empty else 0

    macd_signal_dir = "bullish" if current_macd > current_signal else "bearish"

    # --- Moving Averages (SMA 20, 50, 200 & EMA 20, 50) ---
    sma_20 = round(float(ta.trend.SMAIndicator(close=close, window=20).sma_indicator().iloc[-1]), 2)
    sma_50 = round(float(ta.trend.SMAIndicator(close=close, window=50).sma_indicator().iloc[-1]), 2)

    sma_200 = None
    if len(df) >= 200:
        sma_200 = round(float(ta.trend.SMAIndicator(close=close, window=200).sma_indicator().iloc[-1]), 2)

    ema_20 = round(float(ta.trend.EMAIndicator(close=close, window=20).ema_indicator().iloc[-1]), 2)
    ema_50 = round(float(ta.trend.EMAIndicator(close=close, window=50).ema_indicator().iloc[-1]), 2)

    current_price = round(float(close.iloc[-1]), 2)

    # MA signals
    ma_signal = "bullish" if current_price > sma_20 > sma_50 else (
        "bearish" if current_price < sma_20 < sma_50 else "neutral"
    )

    # --- Bollinger Bands (20, 2) ---
    bb = ta.volatility.BollingerBands(close=close, window=20, window_dev=2)
    bb_upper = round(float(bb.bollinger_hband().iloc[-1]), 2)
    bb_middle = round(float(bb.bollinger_mavg().iloc[-1]), 2)
    bb_lower = round(float(bb.bollinger_lband().iloc[-1]), 2)

    bb_signal = "neutral"
    if current_price >= bb_upper:
        bb_signal = "overbought"
    elif current_price <= bb_lower:
        bb_signal = "oversold"

    # --- Volume Analysis ---
    avg_volume = int(volume.rolling(window=20).mean().iloc[-1])
    current_volume = int(volume.iloc[-1])
    volume_ratio = round(current_volume / avg_volume, 2) if avg_volume > 0 else 1.0

    # --- RSI history for chart ---
    rsi_history = [
        {"date": df.index[i].strftime("%Y-%m-%d"), "value": round(float(v), 2)}
        for i, v in enumerate(rsi_values)
        if not pd.isna(v)
    ][-30:]  # last 30 points

    # --- MACD history for chart ---
    macd_history = []
    for i in range(len(macd_line)):
        if not pd.isna(macd_line.iloc[i]):
            macd_history.append({
                "date": df.index[i].strftime("%Y-%m-%d"),
                "macd": round(float(macd_line.iloc[i]), 4),
                "signal": round(float(signal_line.iloc[i]), 4) if not pd.isna(signal_line.iloc[i]) else 0,
                "histogram": round(float(macd_hist.iloc[i]), 4) if not pd.isna(macd_hist.iloc[i]) else 0,
            })
    # --- Z-Score Probabilities ---

    def sigmoid(x):
        try:
            return 1 / (1 + math.exp(-x))
        except OverflowError:
            return 0.0 if x < 0 else 1.0

    def calc_z(series):
        valid = series.dropna()
        if len(valid) < 2 or valid.std() == 0:
            return 0.0
        return float((valid.iloc[-1] - valid.mean()) / valid.std())

    z_rsi = calc_z(rsi_values)
    p_rsi = 1 - sigmoid(z_rsi)

    bb_pos = (close - bb.bollinger_lband()) / (bb.bollinger_hband() - bb.bollinger_lband())
    z_bb = calc_z(bb_pos)
    p_bb = 1 - sigmoid(z_bb)

    # Trend (MACD + SMA50 ratio)
    p_macd = sigmoid(calc_z(macd_line))
    price_to_sma50 = close / ta.trend.SMAIndicator(close=close, window=50).sma_indicator()
    p_sma = sigmoid(calc_z(price_to_sma50))
    p_trend = (p_macd + p_sma) / 2.0

    z_vol = calc_z(volume)
    # Volume is often confirming trend, we use sigmoid(z_vol) 
    # but actual volume alone isn't directional. Let's use ADX or just trend * vol.
    # The prompt actually requested ADX.
    adx_ind = ta.trend.ADXIndicator(high=high, low=low, close=close, window=14)
    z_adx = calc_z(adx_ind.adx())
    p_volume_adx = sigmoid(z_adx)

    return {
        "rsi": {
            "value": current_rsi,
            "signal": rsi_signal,
            "history": rsi_history,
            "p": p_rsi,
        },
        "macd": {
            "macd": current_macd,
            "signal_line": current_signal,
            "histogram": current_hist,
            "signal": macd_signal_dir,
            "history": macd_history,
            "p": p_macd,
        },
        "moving_averages": {
            "sma_20": sma_20,
            "sma_50": sma_50,
            "sma_200": sma_200,
            "ema_20": ema_20,
            "ema_50": ema_50,
            "signal": ma_signal,
            "price": current_price,
            "p": p_sma,
        },
        "bollinger_bands": {
            "upper": bb_upper,
            "middle": bb_middle,
            "lower": bb_lower,
            "signal": bb_signal,
            "p": p_bb,
        },
        "volume": {
            "current": current_volume,
            "average_20d": avg_volume,
            "ratio": volume_ratio,
            "signal": "high" if volume_ratio > 1.5 else ("low" if volume_ratio < 0.5 else "normal"),
            "p": p_volume_adx,
        },
        "p_trend": p_trend,
    }


def get_technical_score(indicators: dict) -> dict:
    """
    Generate a technical score and confidence based on continuous probabilities.
    Weights: Trend: 0.4, Momentum/RSI: 0.2, Volatility/BB: 0.2, Volume/ADX: 0.2
    """
    if "error" in indicators:
        return {"score": 50.0, "confidence": 50.0}

    p_trend = indicators.get("p_trend", 0.5)
    p_rsi = indicators["rsi"].get("p", 0.5)
    p_bb = indicators["bollinger_bands"].get("p", 0.5)
    p_vol = indicators["volume"].get("p", 0.5)

    s_tech = (0.4 * p_trend) + (0.2 * p_rsi) + (0.2 * p_bb) + (0.2 * p_vol)
    score = round(s_tech * 100.0, 1)

    # Technical Confidence = 1 - variance
    probs = [p_trend, p_rsi, p_bb, p_vol]
    variance = np.var(probs)
    # the maximum variance of a [0,1] bounded value is 0.25 (when 0 and 1 are split equally)
    confidence = round(float((1 - (variance / 0.25)) * 100.0), 1)

    return {
        "score": max(0.0, min(100.0, score)),
        "confidence": max(0.0, min(100.0, confidence))
    }
