import pandas as pd
import numpy as np

def detect_all_patterns(df: pd.DataFrame) -> list:
    """Detects both candlestick and chart patterns on the provided dataframe."""
    if df.empty or len(df) < 20:
        return []

    patterns = []
    
    # 1. Candlestick Patterns (Focus on the most recent completed candles)
    candles = detect_candlestick_patterns(df)
    patterns.extend(candles)

    # 2. Chart Patterns (Focus on the broader 30-60 day structure)
    chart = detect_chart_patterns(df)
    patterns.extend(chart)

    # Sort descending by confidence
    patterns.sort(key=lambda x: x["confidence"], reverse=True)
    return patterns

def detect_candlestick_patterns(df: pd.DataFrame) -> list:
    patterns = []
    
    # Needs at least 5 days to establish short term trend context
    if len(df) < 5:
        return patterns

    # Get the last two days for two-candle patterns
    prev = df.iloc[-2]
    curr = df.iloc[-1]
    
    date_curr = df.index[-1].isoformat() if hasattr(df.index[-1], 'isoformat') else str(df.index[-1])
    date_prev = df.index[-2].isoformat() if hasattr(df.index[-2], 'isoformat') else str(df.index[-2])
    
    # Price action info
    body_curr = abs(curr['Close'] - curr['Open'])
    range_curr = curr['High'] - curr['Low']
    
    body_prev = abs(prev['Close'] - prev['Open'])
    
    is_curr_bullish = curr['Close'] > curr['Open']
    is_curr_bearish = curr['Close'] < curr['Open']
    is_prev_bullish = prev['Close'] > prev['Open']
    is_prev_bearish = prev['Close'] < prev['Open']

    # 1. Doji
    if range_curr > 0 and body_curr <= (range_curr * 0.1):
        # Doji is a reversal signal, type depends on preceding trend
        trend_5d = df['Close'].iloc[-1] - df['Close'].iloc[-5]
        p_type = "Bullish" if trend_5d < 0 else "Bearish"
        patterns.append({
            "name": "Doji",
            "type": p_type,
            "confidence": 0.60,
            "dates": [date_curr]
        })

    # 2. Bullish Engulfing
    if is_prev_bearish and is_curr_bullish:
        if curr['Open'] <= prev['Close'] and curr['Close'] > prev['Open']:
            patterns.append({
                "name": "Bullish Engulfing",
                "type": "Bullish",
                "confidence": 0.85,
                "dates": [date_prev, date_curr]
            })

    # 3. Bearish Engulfing
    if is_prev_bullish and is_curr_bearish:
        if curr['Open'] >= prev['Close'] and curr['Close'] < prev['Open']:
            patterns.append({
                "name": "Bearish Engulfing",
                "type": "Bearish",
                "confidence": 0.85,
                "dates": [date_prev, date_curr]
            })

    # 4. Hammer (Bullish Reversal)
    # Long lower shadow, small body near the top
    lower_shadow = min(curr['Open'], curr['Close']) - curr['Low']
    upper_shadow = curr['High'] - max(curr['Open'], curr['Close'])
    
    if range_curr > 0 and lower_shadow > (2 * body_curr) and upper_shadow < (0.1 * range_curr):
        trend_5d = df['Close'].iloc[-1] - df['Close'].iloc[-5]
        if trend_5d < 0: # Ensure it occurs after a downtrend
            patterns.append({
                "name": "Hammer",
                "type": "Bullish",
                "confidence": 0.75,
                "dates": [date_curr]
            })

    # 5. Shooting Star (Bearish Reversal)
    # Long upper shadow, small body near the bottom
    if range_curr > 0 and upper_shadow > (2 * body_curr) and lower_shadow < (0.1 * range_curr):
        trend_5d = df['Close'].iloc[-1] - df['Close'].iloc[-5]
        if trend_5d > 0: # Ensure it occurs after an uptrend
            patterns.append({
                "name": "Shooting Star",
                "type": "Bearish",
                "confidence": 0.75,
                "dates": [date_curr]
            })

    return patterns

def detect_chart_patterns(df: pd.DataFrame) -> list:
    patterns = []
    
    # We need a decent window to detect macro chart patterns
    if len(df) < 40:
        return patterns
        
    window = df.tail(40).copy()
    
    # Find local minimums and maximums over a rolling 5-day window to identify pivots
    highs = window['High'].values
    lows = window['Low'].values
    closes = window['Close'].values
    dates = [d.isoformat() if hasattr(d, 'isoformat') else str(d) for d in window.index]
    
    pivot_highs = []
    pivot_lows = []
    
    # simple 5-bar pivot detection
    for i in range(2, len(window) - 2):
        if highs[i] > highs[i-1] and highs[i] > highs[i-2] and highs[i] > highs[i+1] and highs[i] > highs[i+2]:
            pivot_highs.append((i, highs[i]))
        if lows[i] < lows[i-1] and lows[i] < lows[i-2] and lows[i] < lows[i+1] and lows[i] < lows[i+2]:
            pivot_lows.append((i, lows[i]))

    # Double Bottom (W pattern)
    if len(pivot_lows) >= 2:
        # Check last two major lows
        idx1, low1 = pivot_lows[-2]
        idx2, low2 = pivot_lows[-1]
        
        # Ensure they are somewhat spaced out (at least 5 days) but not extremely far
        if 5 <= (idx2 - idx1) <= 25:
            # Check price similarity (within 2-3%)
            if abs(low1 - low2) / max(low1, low2) < 0.03:
                # Also ensure there was a peak between them
                between_highs = [h[1] for h in pivot_highs if idx1 < h[0] < idx2]
                if between_highs:
                    mid_high = max(between_highs)
                    # Current price needs to be breaking out or approaching the middle peak
                    curr_close = closes[-1]
                    if curr_close > (low1 * 1.02):
                        patterns.append({
                            "name": "Double Bottom",
                            "type": "Bullish",
                            "confidence": 0.82,
                            "dates": [dates[idx1], dates[idx2], dates[-1]]
                        })

    # Double Top (M pattern)
    if len(pivot_highs) >= 2:
        idx1, high1 = pivot_highs[-2]
        idx2, high2 = pivot_highs[-1]
        
        if 5 <= (idx2 - idx1) <= 25:
            if abs(high1 - high2) / max(high1, high2) < 0.03:
                curr_close = closes[-1]
                # Price has to be rejecting from the top
                if curr_close < (high2 * 0.98):
                    patterns.append({
                        "name": "Double Top",
                        "type": "Bearish",
                        "confidence": 0.82,
                        "dates": [dates[idx1], dates[idx2], dates[-1]]
                    })

    # Ascending / Descending Triangles via linear regression slope on highs/lows
    if len(pivot_highs) >= 3 and len(pivot_lows) >= 3:
        idx_start = min(pivot_highs[-3][0], pivot_lows[-3][0])
        latest_highs = [h[1] for h in pivot_highs[-3:]]
        latest_lows = [l[1] for l in pivot_lows[-3:]]
        
        high_variation = np.std(latest_highs) / np.mean(latest_highs)
        low_variation = np.std(latest_lows) / np.mean(latest_lows)
        
        lows_increasing = latest_lows[2] > latest_lows[1] > latest_lows[0]
        highs_decreasing = latest_highs[2] < latest_highs[1] < latest_highs[0]
        
        # Ascending Triangle (Flat tops, rising bottoms)
        if high_variation < 0.015 and lows_increasing:
            patterns.append({
                "name": "Ascending Triangle",
                "type": "Bullish",
                "confidence": 0.78,
                "dates": [dates[idx_start], dates[-1]]
            })
            
        # Descending Triangle (Flat bottoms, falling tops)
        elif low_variation < 0.015 and highs_decreasing:
            patterns.append({
                "name": "Descending Triangle",
                "type": "Bearish",
                "confidence": 0.78,
                "dates": [dates[idx_start], dates[-1]]
            })

    # Cup and Handle
    # Simulating rounded bottom detection: long consolidation, recent spike, small pullback
    if len(window) > 30 and len(pivot_highs) >= 2:
        left_lip_idx, left_lip_price = pivot_highs[0]
        right_lip_idx, right_lip_price = pivot_highs[-1] # nearest high
        
        # Lips should be somewhat equal
        if abs(left_lip_price - right_lip_price) / max(left_lip_price, right_lip_price) < 0.05:
            # The basin should be between them and roughly rounded/U-shaped (deepest point in the middle)
            basin_lows = [l for l in pivot_lows if left_lip_idx < l[0] < right_lip_idx]
            if basin_lows:
                deepest_low = min([l[1] for l in basin_lows])
                deepest_idx = min([l[0] for l in basin_lows if l[1] == deepest_low])
                # Ensure it's appropriately deep but not a crash (10-30% drop)
                drop = (left_lip_price - deepest_low) / left_lip_price
                if 0.10 <= drop <= 0.35:
                    # Current action must be a handle: small pullback from right lip, low volume preferred
                    curr_price = closes[-1]
                    pullback = (right_lip_price - curr_price) / right_lip_price
                    if 0.02 <= pullback <= 0.12:
                        patterns.append({
                            "name": "Cup and Handle",
                            "type": "Bullish",
                            "confidence": 0.88,
                            "dates": [dates[left_lip_idx], dates[deepest_idx], dates[right_lip_idx], dates[-1]]
                        })

    return patterns
