import os
import requests
import asyncio
import aiohttp
from typing import Dict, List, Optional
from dotenv import load_dotenv
import time
from urllib.parse import urlparse

load_dotenv()

class StoreLeadsClient:
    def __init__(self):
        self.api_key = os.getenv('STORELEADS_API_KEY')
        if not self.api_key:
            raise ValueError("STORELEADS_API_KEY not found in environment variables")

        self.base_url = "https://storeleads.app/json/api/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        self.rate_limit = int(os.getenv('API_RATE_LIMIT', 5))
        self.last_request_time = 0

    def _extract_domain(self, url: str) -> str:
        # Clean up the URL first
        url = url.strip()

        # Fix common typos like https:/www. (missing second slash)
        url = url.replace('https:/www.', 'https://www.')
        url = url.replace('http:/www.', 'http://www.')

        # Add protocol if missing
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url

        # Parse the URL
        parsed = urlparse(url)
        domain = parsed.netloc or parsed.path

        # Remove www. prefix
        domain = domain.replace('www.', '')

        # Remove any trailing slashes or paths
        domain = domain.split('/')[0]

        # Remove any port numbers
        domain = domain.split(':')[0]

        return domain.lower()

    def _rate_limit_wait(self):
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        min_interval = 1.0 / self.rate_limit

        if time_since_last < min_interval:
            time.sleep(min_interval - time_since_last)

        self.last_request_time = time.time()

    async def fetch_domain_data_async(self, session: aiohttp.ClientSession, domain: str) -> Dict:
        domain = self._extract_domain(domain)
        url = f"{self.base_url}/all/domain/{domain}"

        try:
            async with session.get(url, headers=self.headers) as response:
                if response.status == 200:
                    data = await response.json()
                    # Extract the nested 'domain' data if it exists
                    domain_data = data.get('domain', data)
                    return {
                        'domain': domain,
                        'success': True,
                        'data': domain_data
                    }
                elif response.status == 404:
                    return {
                        'domain': domain,
                        'success': False,
                        'error': 'Domain not found in Store Leads database'
                    }
                else:
                    return {
                        'domain': domain,
                        'success': False,
                        'error': f'API error: {response.status}'
                    }
        except Exception as e:
            return {
                'domain': domain,
                'success': False,
                'error': str(e)
            }

    async def fetch_multiple_domains(self, domains: List[str], progress_callback=None) -> List[Dict]:
        results = []

        connector = aiohttp.TCPConnector(limit=self.rate_limit)
        timeout = aiohttp.ClientTimeout(total=30)

        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
            semaphore = asyncio.Semaphore(self.rate_limit)

            async def fetch_with_semaphore(domain):
                async with semaphore:
                    result = await self.fetch_domain_data_async(session, domain)
                    if progress_callback:
                        progress_callback()
                    await asyncio.sleep(1.0 / self.rate_limit)
                    return result

            tasks = [fetch_with_semaphore(domain) for domain in domains]
            results = await asyncio.gather(*tasks)

        return results

    def fetch_domain_data(self, domain: str) -> Dict:
        self._rate_limit_wait()
        domain = self._extract_domain(domain)
        url = f"{self.base_url}/all/domain/{domain}"

        try:
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                data = response.json()
                # Extract the nested 'domain' data if it exists
                domain_data = data.get('domain', data)
                return {
                    'domain': domain,
                    'success': True,
                    'data': domain_data
                }
            elif response.status_code == 404:
                return {
                    'domain': domain,
                    'success': False,
                    'error': 'Domain not found in Store Leads database'
                }
            else:
                return {
                    'domain': domain,
                    'success': False,
                    'error': f'API error: {response.status_code}'
                }
        except Exception as e:
            return {
                'domain': domain,
                'success': False,
                'error': str(e)
            }