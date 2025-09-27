import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('COMPANYENRICH_API_KEY')
print(f"Using API key: {api_key[:10]}...")

# Test with Apple
domain = "apple.com"
url = f"https://api.companyenrich.com/companies/enrich?domain={domain}"

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

print(f"\nTesting URL: {url}")
response = requests.get(url, headers=headers)

print(f"Status Code: {response.status_code}")

if response.status_code == 200:
    data = response.json()
    print("\nFull response structure:")
    print(json.dumps(data, indent=2))
else:
    print(f"Error: {response.text}")