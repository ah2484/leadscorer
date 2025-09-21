import requests
import os
import json
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('STORELEADS_API_KEY')

url = "https://storeleads.app/json/api/v1/all/domain/gymshark.com"
headers = {
    "Authorization": f"Bearer {api_key}",
}

response = requests.get(url, headers=headers)
if response.status_code == 200:
    data = response.json()

    # Print the full structure to understand the response
    print("Full JSON structure (keys at root level):")
    print(list(data.keys()))
    print()

    # Check if there's a 'domain' key
    if 'domain' in data:
        print("Keys in 'domain':")
        print(list(data['domain'].keys()))
        print()

        # Look for sales/revenue data
        domain_data = data['domain']
        print("Looking for sales/revenue fields:")
        for key in domain_data.keys():
            if 'sale' in key.lower() or 'revenue' in key.lower() or 'employee' in key.lower():
                print(f"  {key}: {domain_data[key]}")

        print("\nAll numeric fields:")
        for key, value in domain_data.items():
            if isinstance(value, (int, float)) and value != 0:
                print(f"  {key}: {value}")