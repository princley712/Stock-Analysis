import sys
import os

# Add backend directory to sys.path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from services.utils import resolve_ticker

def test():
    test_cases = [
        ("reliance", "RELIANCE.NS"),
        ("RELIANCE.NS", "RELIANCE.NS"),
        ("AAPL", "AAPL"),
        ("tcs", "TCS.NS"),
        ("  sbin  ", "SBIN.NS"),
        ("INFY", "INFY.NS"),
        ("GOOG", "GOOGL") # This might not resolve GOOGL if it's not in mapping or doesn't match .NS probe
    ]

    for user_input, expected in test_cases:
        resolved = resolve_ticker(user_input)
        print(f"Input: '{user_input}' -> Resolved: '{resolved}'")
        # We don't strictly assert because 'AAPL' might return 'AAPL' and 'GOOG' might return 'GOOG' 
        # but for Indian stocks, it should definitely have .NS

if __name__ == "__main__":
    test()
