import sys
from pathlib import Path

# Add project root to sys.path so `app` package can be imported when running this script
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from fastapi.testclient import TestClient
from app.mainn import app

client = TestClient(app)

resp = client.get('/product', params={'name': 'Realme Model Air'})
print('status_code =', resp.status_code)
print('response =', resp.json())
