import requests
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('STORELEADS_API_KEY')
print(f"Using API key: {api_key[:10]}...")

# Test direct API call
url = "https://storeleads.app/json/api/v1/all/domain/gymshark.com"
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

print(f"\nTesting URL: {url}")
print(f"Headers: {headers}")

response = requests.get(url, headers=headers)
print(f"\nStatus Code: {response.status_code}")
print(f"Response Headers: {dict(response.headers)}")

if response.status_code == 200:
    data = response.json()
    print(f"\nResponse Data (first 500 chars):")
    import json
    print(json.dumps(data, indent=2)[:500])
else:
    print(f"\nError Response: {response.text}")