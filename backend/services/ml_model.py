"""
ML model service for stock prediction using XGBoost.
Computes 5-day horizon and dynamically weights components using confidence.
"""
import numpy as np
import pandas as pd
import math
from xgboost import XGBClassifier
from sklearn.preprocessing import StandardScaler
import ta
import traceback

def prepare_features(df: pd.DataFrame) -> pd.DataFrame:
    features = pd.DataFrame(index=df.index)
    close = df["Close"]
    volume = df["Volume"]

    # Price-based
    features["returns_1d"] = close.pct_change(1)
    features["returns_3d"] = close.pct_change(3)
    features["returns_5d"] = close.pct_change(5)
    features["returns_10d"] = close.pct_change(10)

    # Volatility
    features["volatility_10d"] = close.pct_change().rolling(10).std()

    # RSI & MACD
    features["rsi"] = ta.momentum.RSIIndicator(close=close, window=14).rsi()
    macd = ta.trend.MACD(close=close)
    features["macd"] = macd.macd()
    features["macd_hist"] = macd.macd_diff()

    # BB width
    bb = ta.volatility.BollingerBands(close=close, window=20, window_dev=2)
    features["bb_width"] = (bb.bollinger_hband() - bb.bollinger_lband()) / bb.bollinger_mavg()

    # Volume z-score
    vol_mean = volume.rolling(20).mean()
    vol_std = volume.rolling(20).std()
    features["vol_zscore"] = (volume - vol_mean) / vol_std

    # ADX
    adx_ind = ta.trend.ADXIndicator(high=df["High"], low=df["Low"], close=close, window=14)
    features["adx"] = adx_ind.adx()

    features = features.dropna()
    return features


def calculate_entropy_confidence(p: float) -> float:
    # bounds
    p = max(1e-5, min(1 - 1e-5, p))
    # entropy H = -p log(p) - (1-p) log(1-p)
    # log base 2 so max entropy is 1.0 (when p=0.5)
    h = -p * math.log2(p) - (1-p) * math.log2(1-p)
    return max(0.0, (1.0 - h) * 100.0)


def train_and_predict(df: pd.DataFrame, horizon_days: int = 5) -> dict:
    if df.empty or len(df) < 60:
        return {"prediction": "hold", "confidence": 0.0, "ml_score": 50.0}

    try:
        features = prepare_features(df)
        if len(features) < 40:
            return {"prediction": "hold", "confidence": 0.0, "ml_score": 50.0}

        # Dynamic threshold mapping
        if horizon_days <= 10:
            threshold = 0.02
        elif horizon_days <= 30:
            threshold = 0.05
        else:
            threshold = 0.10

        # Target: horizon_days return
        close_aligned = df["Close"].loc[features.index]
        return_hd = (close_aligned.shift(-horizon_days) / close_aligned) - 1.0
        
        target = pd.Series(index=features.index, dtype=float)
        target.loc[return_hd > threshold] = 1.0
        target.loc[return_hd < -threshold] = 0.0

        # Create training set by dropping NaNs in target (which ignores middle returns and the latest days)
        valid = target.notna()
        features_train = features[valid]
        target_train = target[valid]

        if len(features_train) < 20:
            return {"prediction": "hold", "confidence": 0.0, "ml_score": 50.0}

        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(features_train)
        y = target_train.values

        # train test split
        split_idx = int(len(X_scaled) * 0.8)
        X_train, X_test = X_scaled[:split_idx], X_scaled[split_idx:]
        y_train, y_test = y[:split_idx], y[split_idx:]

        model = XGBClassifier(
            n_estimators=100,
            max_depth=4,
            learning_rate=0.05,
            objective="binary:logistic",
            eval_metric="logloss",
            random_state=42
        )
        model.fit(X_train, y_train)

        # Predict latest row (predict next 5 days)
        latest_features = scaler.transform(features.iloc[[-1]])
        prob = model.predict_proba(latest_features)[0]
        
        p_up = float(prob[1]) if len(prob) > 1 else (float(prob[0]) if model.classes_[0] == 1 else 1-float(prob[0]))
        
        ml_score = round(p_up * 100.0, 1)
        confidence = round(calculate_entropy_confidence(p_up), 1)

        prediction = "buy" if p_up > 0.55 else ("sell" if p_up < 0.45 else "hold")
        
        test_acc = float(model.score(X_test, y_test)) * 100 if len(X_test) > 0 else 0
        test_accuracy = round(test_acc, 1)

        # Feature importances
        importance_dict = {}
        if hasattr(model, 'feature_importances_'):
            for name, imp in zip(features.columns, model.feature_importances_):
                importance_dict[name] = round(float(imp), 4)
            importance_dict = dict(sorted(importance_dict.items(), key=lambda x: x[1], reverse=True)[:5])

        return {
            "prediction": prediction,
            "confidence": confidence,
            "ml_score": ml_score,
            "test_accuracy": test_accuracy,
            "feature_importances": importance_dict,
        }

    except Exception as e:
        print(f"ML Model Error: {e}")
        traceback.print_exc()
        return {"prediction": "hold", "confidence": 0.0, "ml_score": 50.0, "error": str(e)}


def compute_buy_sell_score(
    df: pd.DataFrame,
    tech_score: float,
    tech_conf: float,
    sent_score: float,
    sent_conf: float,
) -> dict:
    horizons = {
        "short_term": {"days": 5, "name": "Short Term (1W)"},
        "medium_term": {"days": 21, "name": "Medium Term (1M)"},
        "long_term": {"days": 126, "name": "Long Term (6M)"}
    }

    results = {}

    for key, info in horizons.items():
        ml_result = train_and_predict(df, horizon_days=info["days"])
        
        ml_score = ml_result.get("ml_score", 50.0)
        ml_conf = ml_result.get("confidence", 0.0)

        # Dynamic Weighting Formula:
        b_ml, b_tech, b_sent = 0.5, 0.3, 0.2
        
        # Adjust technical weight for long term (technical drops, ML/Fundamentals increase theoretically)
        if key == "long_term":
            b_ml, b_tech, b_sent = 0.6, 0.2, 0.2
        
        w_ml = b_ml * (ml_conf / 100.0)
        w_tech = b_tech * (tech_conf / 100.0)
        w_sent = b_sent * (sent_conf / 100.0)
        
        total_w = w_ml + w_tech + w_sent

        if total_w <= 0.001:
            eff_ml, eff_tech, eff_sent = b_ml, b_tech, b_sent
        else:
            eff_ml = w_ml / total_w
            eff_tech = w_tech / total_w
            eff_sent = w_sent / total_w

        composite = (ml_score * eff_ml) + (tech_score * eff_tech) + (sent_score * eff_sent)
        composite = round(max(0, min(100, composite)), 1)

        override_applied = False
        if df is not None and not df.empty and len(df) > 20:
            max_high = df["High"].max()
            current_price = df["Close"].iloc[-1]
            
            rsi_series = ta.momentum.RSIIndicator(close=df["Close"], window=14).rsi().dropna()
            rsi_val = rsi_series.iloc[-1] if not rsi_series.empty else 50
            
            avg_vol = df["Volume"].rolling(20).mean().iloc[-1]
            curr_vol = df["Volume"].iloc[-1]

            if max_high > 0:
                drop_pct = (max_high - current_price) / max_high
                if drop_pct > 0.50 and rsi_val < 30 and (avg_vol > 0 and curr_vol > 2 * avg_vol):
                    override_applied = True
                    # Only apply value trap boost on medium and long term
                    if key != "short_term":
                        composite = min(100.0, composite + 10.0)

        if composite >= 75: signal = "strong_buy"
        elif composite >= 60: signal = "buy"
        elif composite >= 45: signal = "hold"
        elif composite >= 30: signal = "sell"
        else: signal = "strong_sell"

        overall_conf = round(
            ((ml_conf * b_ml) + (tech_conf * b_tech) + (sent_conf * b_sent)) / (b_ml + b_tech + b_sent),
            1
        )

        results[key] = {
            "name": info["name"],
            "score": composite,
            "confidence": overall_conf,
            "signal": signal,
            "components": {
                "ml": {"score": round(ml_score, 1), "weight": f"{round(eff_ml*100)}%"},
                "technical": {"score": round(tech_score, 1), "weight": f"{round(eff_tech*100)}%"},
                "sentiment": {"score": round(sent_score, 1), "weight": f"{round(eff_sent*100)}%"},
            },
            "ml_details": {
                "prediction": ml_result.get("prediction", "hold"),
                "confidence": ml_conf,
                "test_accuracy": ml_result.get("test_accuracy", 0),
                "top_features": ml_result.get("feature_importances", {}),
                "value_trap_boost": override_applied,
            },
        }

    return results
