import sys
import os

# Add backend directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'backend')))

from backend.services.news import fetch_news

def test_fetch_news():
    ticker = "AAPL"
    print(f"Fetching news for {ticker}...")
    news = fetch_news(ticker)
    
    if news:
        print(f"Successfully fetched {len(news)} articles.")
        # Debug: check yfinance news if it's there
        import yfinance as yf
        raw_news = yf.Ticker(ticker).news
        if raw_news:
             print("\nRaw first news item:")
             print(raw_news[0])
        
        for i, article in enumerate(news[:3]):
            print(f"\nArticle {i+1}:")
            print(f"Title: {article['title']}")
            print(f"Source: {article['source']}")
            print(f"Published: {article['published']}")
            print(f"Link: {article['link']}")
    else:
        print("Failed to fetch news.")

if __name__ == "__main__":
    test_fetch_news()
