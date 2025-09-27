import asyncio
from app.storeleads_client import StoreLeadsClient
import json

async def test_domains():
    client = StoreLeadsClient()

    # Test with various types of domains
    test_domains = [
        "apple.com",
        "gymshark.com",  # Known Shopify store
        "fashionnova.com",  # Known e-commerce
        "allbirds.com",  # Known DTC brand
        "mvmtwatches.com",  # Known Shopify store
    ]

    print("Testing Store Leads API with different domains:\n")

    for domain in test_domains:
        print(f"Testing {domain}...")
        result = client.fetch_domain_data(domain)

        if result['success']:
            data = result['data']
            print(f"✓ Found data for {domain}")
            print(f"  - Platform: {data.get('platform', 'N/A')}")
            print(f"  - Yearly Sales: ${data.get('estimated_sales_yearly', 0):,.0f}")
            print(f"  - Employees: {data.get('employee_count', 0)}")
            print(f"  - Rank: {data.get('platform_rank', 'N/A')}")
        else:
            print(f"✗ No data for {domain}: {result.get('error', 'Unknown error')}")
        print()

if __name__ == "__main__":
    asyncio.run(test_domains())