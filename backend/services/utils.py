import yfinance as yf

# Local mapping for very common Indian stocks that users might just type the name of
COMMON_INDIAN_STOCKS = {
    "RELIANCE": "RELIANCE.NS",
    "TCS": "TCS.NS",
    "HDFC": "HDFCBANK.NS",
    "HDFCBANK": "HDFCBANK.NS",
    "INFY": "INFY.NS",
    "INFOSYS": "INFY.NS",
    "ICICI": "ICICIBANK.NS",
    "ICICIBANK": "ICICIBANK.NS",
    "SBIN": "SBIN.NS",
    "SBI": "SBIN.NS",
    "BHARTIARTL": "BHARTIARTL.NS",
    "AIRTEL": "BHARTIARTL.NS",
    "ITC": "ITC.NS",
    "KOTAKBANK": "KOTAKBANK.NS",
    "KOTAK": "KOTAKBANK.NS",
    "LT": "LT.NS",
    "LARSEN": "LT.NS",
    "AXISBANK": "AXISBANK.NS",
    "AXIS": "AXISBANK.NS",
    "ASIANPAINT": "ASIANPAINT.NS",
    "MARUTI": "MARUTI.NS",
    "TITAN": "TITAN.NS",
    "BAJFINANCE": "BAJFINANCE.NS",
    "WIPRO": "WIPRO.NS",
    "ADANIENT": "ADANIENT.NS",
    "ADANI": "ADANIENT.NS"
}

def resolve_ticker(user_input: str) -> str:
    """
    Intelligently resolves a user's stock search input into a valid ticker.
    Specifically handles Indian NSE stocks automatically.
    """
    if not user_input:
        return ""
        
    # 1. Clean input
    ticker = user_input.strip().upper()
    
    # 2. Check common mapping
    if ticker in COMMON_INDIAN_STOCKS:
        return COMMON_INDIAN_STOCKS[ticker]
        
    # 3. If it already has a suffix (.NS, .BO, etc.), return as is
    if "." in ticker:
        return ticker
        
    # 4. Try to see if it's an Indian stock by appending .NS
    # We test if {TICKER}.NS is a valid ticker with data
    try:
        india_ticker = f"{ticker}.NS"
        stock = yf.Ticker(india_ticker)
        # Check if we can get some basic info or if it's just a placeholder
        # Most valid tickers will have a 'symbol' or 'shortName' in info
        if stock.info and 'symbol' in stock.info:
            return india_ticker
    except Exception:
        # If any error in probing, fallback to original
        pass
        
    # 5. Fallback to original input
    return ticker
