
"""
Technical indicators service (PRODUCTION SAFE).
Handles NaN, empty data, and unstable API responses.
"""

import math
import numpy as np
import pandas as pd
import ta


# ---------- SAFE HELPERS ----------

def safe_last(series, default=0.0):
    try:
        if series is None or len(series) == 0:
            return default
        val = series.iloc[-1]
        if pd.isna(val):
            return default
        return float(val)
    except Exception:
        return default


def calc_z(series):
    try:
        valid = series.dropna()
        if len(valid) < 2 or valid.std() == 0:
            return 0.0
        return float((valid.iloc[-1] - valid.mean()) / valid.std())
    except Exception:
        return 0.0


def sigmoid(x):
    try:
        return 1 / (1 + math.exp(-x))
    except OverflowError:
        return 0.0 if x < 0 else 1.0


# ---------- MAIN FUNCTION ----------

def compute_indicators(df: pd.DataFrame) -> dict:
    try:
        if df is None or df.empty or len(df) < 30:
            return {"error": "Insufficient data"}

        # Clean data
        df = df.copy()
        df = df.ffill()
        # Ensure required columns exist
        if "Close" not in df.columns:
            if "Adj Close" in df.columns:
                df["Close"] = df["Adj Close"]
            else:
                return {"error": "No Close price available"}

        required_cols = ["Close", "High", "Low", "Volume"]
        for col in required_cols:
            if col not in df.columns:
                return {"error": f"Missing column: {col}"}

        close = df["Close"]
        high = df["High"]
        low = df["Low"]
        volume = df["Volume"]

        # ---------- RSI ----------
        rsi_values = ta.momentum.RSIIndicator(close=close, window=14).rsi()
        current_rsi = round(safe_last(rsi_values, 50), 2)

        rsi_signal = "neutral"
        if current_rsi > 70:
            rsi_signal = "overbought"
        elif current_rsi < 30:
            rsi_signal = "oversold"

        # ---------- MACD ----------
        macd_ind = ta.trend.MACD(close=close)
        macd_line = macd_ind.macd()
        signal_line = macd_ind.macd_signal()
        macd_hist = macd_ind.macd_diff()

        current_macd = round(safe_last(macd_line), 4)
        current_signal = round(safe_last(signal_line), 4)
        current_hist = round(safe_last(macd_hist), 4)

        macd_signal_dir = "bullish" if current_macd > current_signal else "bearish"

        # ---------- MOVING AVERAGES ----------
        sma_20 = round(safe_last(ta.trend.SMAIndicator(close, 20).sma_indicator()), 2)
        sma_50 = round(safe_last(ta.trend.SMAIndicator(close, 50).sma_indicator()), 2)

        sma_200 = None
        if len(df) >= 200:
            sma_200 = round(safe_last(ta.trend.SMAIndicator(close, 200).sma_indicator()), 2)

        ema_20 = round(safe_last(ta.trend.EMAIndicator(close, 20).ema_indicator()), 2)
        ema_50 = round(safe_last(ta.trend.EMAIndicator(close, 50).ema_indicator()), 2)

        current_price = round(safe_last(close), 2)

        if current_price > sma_20 > sma_50:
            ma_signal = "bullish"
        elif current_price < sma_20 < sma_50:
            ma_signal = "bearish"
        else:
            ma_signal = "neutral"

        # ---------- BOLLINGER ----------
        bb = ta.volatility.BollingerBands(close=close)
        bb_upper = round(safe_last(bb.bollinger_hband()), 2)
        bb_middle = round(safe_last(bb.bollinger_mavg()), 2)
        bb_lower = round(safe_last(bb.bollinger_lband()), 2)

        bb_signal = "neutral"
        if current_price >= bb_upper:
            bb_signal = "overbought"
        elif current_price <= bb_lower:
            bb_signal = "oversold"

        # ---------- VOLUME ----------
        avg_volume = int(safe_last(volume.rolling(20).mean(), 1))
        current_volume = int(safe_last(volume, 0))
        volume_ratio = round(current_volume / avg_volume, 2) if avg_volume > 0 else 1.0

        # ---------- HISTORY ----------
        rsi_history = [
            {"date": str(df.index[i])[:10], "value": round(float(v), 2)}
            for i, v in enumerate(rsi_values)
            if not pd.isna(v)
        ][-30:]

        macd_history = []
        for i in range(len(macd_line)):
            if not pd.isna(macd_line.iloc[i]):
                macd_history.append({
                    "date": str(df.index[i])[:10],
                    "macd": round(float(macd_line.iloc[i]), 4),
                    "signal": round(float(signal_line.iloc[i]), 4) if not pd.isna(signal_line.iloc[i]) else 0,
                    "histogram": round(float(macd_hist.iloc[i]), 4) if not pd.isna(macd_hist.iloc[i]) else 0,
                })

        # ---------- PROBABILITIES ----------
        z_rsi = calc_z(rsi_values)
        p_rsi = 1 - sigmoid(z_rsi)

        bb_pos = (close - bb.bollinger_lband()) / (bb.bollinger_hband() - bb.bollinger_lband())
        p_bb = 1 - sigmoid(calc_z(bb_pos))

        p_macd = sigmoid(calc_z(macd_line))
        p_sma = sigmoid(calc_z(close / ta.trend.SMAIndicator(close, 50).sma_indicator()))
        p_trend = (p_macd + p_sma) / 2

        adx = ta.trend.ADXIndicator(high, low, close).adx()
        p_volume_adx = sigmoid(calc_z(adx))

        return {
            "rsi": {"value": current_rsi, "signal": rsi_signal, "history": rsi_history, "p": p_rsi},
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

    except Exception as e:
        print("INDICATOR CRASH:", e)
        return {"error": str(e)}


# ---------- TECH SCORE ----------

def get_technical_score(indicators: dict) -> dict:
    try:
        if "error" in indicators:
            return {"score": 50.0, "confidence": 50.0}

        p_trend = indicators.get("p_trend", 0.5)
        p_rsi = indicators["rsi"].get("p", 0.5)
        p_bb = indicators["bollinger_bands"].get("p", 0.5)
        p_vol = indicators["volume"].get("p", 0.5)

        score = round((0.4*p_trend + 0.2*p_rsi + 0.2*p_bb + 0.2*p_vol) * 100, 1)

        variance = np.var([p_trend, p_rsi, p_bb, p_vol])
        confidence = round((1 - (variance / 0.25)) * 100, 1)

        return {
            "score": max(0.0, min(100.0, score)),
            "confidence": max(0.0, min(100.0, confidence))
        }

    except Exception:
        return {"score": 50.0, "confidence": 50.0}