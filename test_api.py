import urllib.request
import traceback

try:
    print("Requesting...")
    req = urllib.request.urlopen("http://localhost:8000/api/analysis/AAPL", timeout=5)
    print(req.read().decode('utf-8')[:200])
except Exception as e:
    print("ERROR:")
    traceback.print_exc()
