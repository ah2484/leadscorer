from app.storeleads_client import StoreLeadsClient

client = StoreLeadsClient()

# Test various URL formats
test_urls = [
    "gymshark.com",
    "www.gymshark.com",
    "https://www.gymshark.com",
    "http://gymshark.com",
    "https:/www.gymshark.com",  # Common typo
    "GYMSHARK.COM",  # Uppercase
    "gymshark.com/",  # Trailing slash
    "https://gymshark.com/collections/mens",  # With path
    "gymshark.com:443",  # With port
    "  gymshark.com  ",  # With spaces
]

print("Testing URL extraction:")
print("-" * 40)

for url in test_urls:
    extracted = client._extract_domain(url)
    print(f"Input: '{url}'")
    print(f"Output: '{extracted}'")
    print()

# All should output: 'gymshark.com'