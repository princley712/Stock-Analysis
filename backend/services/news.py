"""
News fetching service.
Scrapes Google News RSS for stock-related headlines.
"""
import time
import requests
from bs4 import BeautifulSoup
from datetime import datetime

# Cache for news results
_news_cache = {}
NEWS_CACHE_TTL = 300  # 5 minutes


def fetch_news(ticker: str, limit: int = 10) -> list:
    """
    Fetch news headlines for a stock ticker from Google News RSS.
    Returns list of dicts with title, source, link, published date.
    """
    cache_key = ticker.upper()
    now = time.time()

    if cache_key in _news_cache and (now - _news_cache[cache_key]["timestamp"]) < NEWS_CACHE_TTL:
        return _news_cache[cache_key]["data"]

    try:
        # Google News RSS search
        url = f"https://news.google.com/rss/search?q={ticker}+stock&hl=en-US&gl=US&ceid=US:en"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, "xml")
        items = soup.find_all("item", limit=limit)

        articles = []
        for item in items:
            title = item.title.text if item.title else "No title"
            link = item.link.text if item.link else ""
            source = item.source.text if item.source else "Unknown"

            # Parse publication date
            pub_date = ""
            if item.pubDate:
                try:
                    dt = datetime.strptime(item.pubDate.text, "%a, %d %b %Y %H:%M:%S %Z")
                    pub_date = dt.strftime("%Y-%m-%d %H:%M")
                except Exception:
                    pub_date = item.pubDate.text

            articles.append({
                "title": title,
                "source": source,
                "link": link,
                "published": pub_date,
            })

        _news_cache[cache_key] = {"data": articles, "timestamp": now}
        return articles

    except Exception as e:
        # Return empty list on failure, don't break the app
        print(f"News fetch error for {ticker}: {e}")
        return []
