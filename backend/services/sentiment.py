"""
Sentiment analysis service using VADER (NLTK).
Replaces TextBlob with VADER and computes weighted averages based on time decay.
Computes sentiment confidence based on variance and article counts.
"""
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from datetime import datetime
import numpy as np
import math

try:
    sia = SentimentIntensityAnalyzer()
except LookupError:
    import nltk
    nltk.download('vader_lexicon')
    sia = SentimentIntensityAnalyzer()


def analyze_sentiment(text: str) -> dict:
    """
    Analyze sentiment of a single text string using VADER.
    """
    scores = sia.polarity_scores(text)
    polarity = scores["compound"]  # -1 to 1

    if polarity > 0.05:
        label = "positive"
    elif polarity < -0.05:
        label = "negative"
    else:
        label = "neutral"

    return {
        "polarity": round(polarity, 4),
        "subjectivity": 0.5, # Dummy to keep frontend happy
        "label": label,
    }


def analyze_news_sentiment(articles: list) -> dict:
    """
    Analyze sentiment applying exact formula from changes.txt.
    p_sent = (S_sent + 1) / 2
    Confidence based on variance & count.
    """
    if not articles:
        return {
            "articles": [],
            "aggregate": {
                "score": 50.0,
                "confidence": 0.0,
                "polarity": 0.0,
                "label": "neutral",
                "positive_count": 0,
                "negative_count": 0,
                "neutral_count": 0,
            },
        }

    analyzed = []
    polarities = []
    weights = []
    
    pos_count = 0
    neg_count = 0
    neu_count = 0

    now = datetime.now()

    for article in articles:
        sentiment = analyze_sentiment(article["title"])
        analyzed.append({
            **article,
            "sentiment": sentiment,
        })

        pol = sentiment["polarity"]
        polarities.append(pol)

        if sentiment["label"] == "positive":
            pos_count += 1
        elif sentiment["label"] == "negative":
            neg_count += 1
        else:
            neu_count += 1

        # Time decay
        curr_weight = 1.0
        try:
            pub_dt = datetime.strptime(article["published"], "%Y-%m-%d %H:%M")
            hours_ago = max(0, (now - pub_dt).total_seconds() / 3600.0)
            # Lambda = 0.05 gives ~14 hr half-life
            curr_weight = math.exp(-0.05 * hours_ago)
        except Exception:
            pass
        weights.append(curr_weight)

    total_weight = sum(weights)
    if total_weight > 0:
        avg_polarity = sum(p * w for p, w in zip(polarities, weights)) / total_weight
    else:
        avg_polarity = np.mean(polarities)

    # Probability Mapping
    p_sent = (avg_polarity + 1.0) / 2.0
    sentiment_score = round(p_sent * 100.0, 1)

    overall_label = "positive" if avg_polarity > 0.05 else ("negative" if avg_polarity < -0.05 else "neutral")

    # Confidence calculation: lower variance = higher confidence
    # Compund variance max is ~1.0. 
    var = np.var(polarities) if len(polarities) > 1 else 1.0
    # count factor
    count_factor = min(1.0, np.log1p(len(articles)) / np.log1p(10.0))
    
    confidence = max(0.0, (1.0 - var) * count_factor)
    confidence_score = round(confidence * 100.0, 1)

    return {
        "articles": analyzed,
        "aggregate": {
            "score": sentiment_score,
            "confidence": confidence_score,
            "polarity": round(avg_polarity, 4),
            "label": overall_label,
            "positive_count": pos_count,
            "negative_count": neg_count,
            "neutral_count": neu_count,
        },
    }
