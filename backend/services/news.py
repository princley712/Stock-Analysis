"""
News fetching service.
Scrapes Google News RSS for stock-related headlines.
"""
import time
import yfinance as yf
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
        # 1. Try yfinance news first (more reliable on AWS), with 5-second timeout
        import concurrent.futures
        ticker_obj = yf.Ticker(ticker)
        
        executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
        future = executor.submit(lambda: ticker_obj.news)
        try:
            # 5 second timeout to prevent hanging the API
            yf_news = future.result(timeout=5)
        except concurrent.futures.TimeoutError:
            print(f"yfinance news fetch timed out for {ticker}")
            yf_news = None
        except Exception as e:
            print(f"yfinance news fetch failed for {ticker}: {e}")
            yf_news = None
        finally:
            executor.shutdown(wait=False)
        
        if yf_news:
            articles = []
            for item in yf_news[:limit]:
<<<<<<< HEAD
                # New yfinance format with 'content' dict
                if "content" in item:
                    content = item["content"]
                    pub_date_str = content.get("pubDate", "")
                    pub_date = ""
                    if pub_date_str:
                        # e.g., '2026-04-08T20:32:00Z'
                        try:
                            dt = datetime.strptime(pub_date_str, "%Y-%m-%dT%H:%M:%SZ")
                            pub_date = dt.strftime("%Y-%m-%d %H:%M")
                        except Exception:
                            pub_date = pub_date_str

                    title = content.get("title", "No title")
                    
                    provider = content.get("provider", {})
                    source = provider.get("displayName", "Unknown") if isinstance(provider, dict) else "Unknown"
                    
                    click_url = content.get("clickThroughUrl")
                    canonical_url = content.get("canonicalUrl", {})
                    
                    if click_url and isinstance(click_url, dict) and click_url.get("url"):
                        link = click_url.get("url")
                    elif canonical_url and isinstance(canonical_url, dict) and canonical_url.get("url"):
                        link = canonical_url.get("url")
                    else:
                        link = ""
                # Old yfinance format
                else:
=======
                # Check for new yfinance format where data is nested in "content"
                if "content" in item and isinstance(item["content"], dict):
                    content = item["content"]
                    title = content.get("title", "No title")
                    source = content.get("provider", {}).get("displayName", "Unknown")
                    
                    # Sometimes link is inside clickThroughUrl -> url
                    click_data = content.get("clickThroughUrl", {})
                    link = click_data.get("url", "") if isinstance(click_data, dict) else ""
                    
                    pub_date = ""
                    pub_time = content.get("pubDate", "")
                    if pub_time:
                        try:
                            # Usually ISO8601 like 2024-04-05T12:00:00Z
                            dt = datetime.fromisoformat(str(pub_time).replace("Z", "+00:00"))
                            pub_date = dt.strftime("%Y-%m-%d %H:%M")
                        except Exception:
                            pub_date = str(pub_time)[:16]
                else:
                    # Old flat format
                    title = item.get("title", "No title")
                    source = item.get("publisher", "Unknown")
                    link = item.get("link", "")
                    
>>>>>>> 1c2a67b43ccb0e4b96f497e12ec973f5e4716840
                    pub_time = item.get("providerPublishTime", 0)
                    pub_date = ""
                    if pub_time:
                        try:
                            dt = datetime.fromtimestamp(pub_time)
                            pub_date = dt.strftime("%Y-%m-%d %H:%M")
                        except Exception:
                            pub_date = str(pub_time)
<<<<<<< HEAD
                    
                    title = item.get("title", "No title")
                    source = item.get("publisher", "Unknown")
                    link = item.get("link", "")
=======
>>>>>>> 1c2a67b43ccb0e4b96f497e12ec973f5e4716840

                articles.append({
                    "title": title,
                    "source": source,
                    "link": link,
                    "published": pub_date,
                })
            
            if articles:
                _news_cache[cache_key] = {"data": articles, "timestamp": now}
                return articles

        # 2. Fallback to Google News RSS (useful for local dev)
        url = f"https://news.google.com/rss/search?q={ticker}+stock&hl=en-US&gl=US&ceid=US:en"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        response = requests.get(url, headers=headers, timeout=3)
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

        if articles:
            _news_cache[cache_key] = {"data": articles, "timestamp": now}
            return articles
        
        return []

    except Exception as e:
        # Return empty list on failure, don't break the app
        print(f"News fetch error for {ticker}: {e}")
        return []