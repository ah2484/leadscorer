import os
import requests
import asyncio
import aiohttp
from typing import Dict, List, Optional
from dotenv import load_dotenv
from urllib.parse import urlparse

load_dotenv()

class CompanyEnrichClient:
    def __init__(self):
        self.api_key = os.getenv('COMPANYENRICH_API_KEY')
        if not self.api_key:
            raise ValueError("COMPANYENRICH_API_KEY not found in environment variables")

        self.base_url = "https://api.companyenrich.com/companies/enrich"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def _extract_domain(self, url: str) -> str:
        # Clean up the URL first
        url = url.strip()

        # Fix common typos
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

    def _parse_revenue(self, revenue_str: str) -> float:
        """Convert revenue strings like 'over-1b' to numeric values"""
        if not revenue_str:
            return 0

        revenue_map = {
            'over-10b': 15000000000,
            'over-1b': 5000000000,
            '500m-1b': 750000000,
            '100m-500m': 300000000,
            '50m-100m': 75000000,
            '10m-50m': 30000000,
            '1m-10m': 5000000,
            'under-1m': 500000,
            '0-1m': 500000
        }

        return revenue_map.get(revenue_str.lower(), 0)

    def _parse_employees(self, employee_str: str) -> int:
        """Convert employee strings like 'over-10K' to numeric values"""
        if not employee_str:
            return 0

        employee_map = {
            'over-10k': 15000,
            'over-10000': 15000,
            '5k-10k': 7500,
            '5000-10000': 7500,
            '1k-5k': 3000,
            '1000-5000': 3000,
            '500-1k': 750,
            '500-1000': 750,
            '250-500': 375,
            '100-250': 175,
            '50-100': 75,
            '20-50': 35,
            '10-20': 15,
            '5-10': 7,
            '1-5': 3,
            'under-10': 5,
            '0-10': 5
        }

        return employee_map.get(employee_str.lower(), 0)

    async def fetch_company_data_async(self, session: aiohttp.ClientSession, domain: str) -> Dict:
        domain = self._extract_domain(domain)
        url = f"{self.base_url}?domain={domain}"

        try:
            async with session.get(url, headers=self.headers) as response:
                if response.status == 200:
                    data = await response.json()

                    # Parse and normalize the data for scoring - include ALL available fields
                    normalized_data = {
                        'name': data.get('name', domain),
                        'domain': domain,
                        'website': data.get('website', ''),
                        'industry': data.get('industry', 'Unknown'),
                        'industries': ', '.join(data.get('industries', [])) if data.get('industries') else '',
                        'type': data.get('type', ''),
                        'categories': ', '.join(data.get('categories', [])) if data.get('categories') else '',
                        'description': data.get('description', ''),
                        'keywords': ', '.join(data.get('keywords', [])) if data.get('keywords') else '',
                        'technologies': ', '.join(data.get('technologies', [])) if data.get('technologies') else '',
                        'founded_year': data.get('founded_year', 0),
                        'page_rank': data.get('page_rank', 0),

                        # Parse revenue and employees for scoring
                        'estimated_sales_yearly': self._parse_revenue(data.get('revenue', '')),
                        'employee_count': self._parse_employees(data.get('employees', '')),

                        # Raw values for display
                        'revenue_range': data.get('revenue', 'Unknown'),
                        'employee_range': data.get('employees', 'Unknown'),

                        # Location details
                        'country_code': data.get('location', {}).get('country', {}).get('code', 'Unknown'),
                        'country_name': data.get('location', {}).get('country', {}).get('name', ''),
                        'state': data.get('location', {}).get('state', {}).get('name', ''),
                        'state_code': data.get('location', {}).get('state', {}).get('code', ''),
                        'city': data.get('location', {}).get('city', {}).get('name', ''),
                        'address': data.get('location', {}).get('address', ''),
                        'postal_code': data.get('location', {}).get('postal_code', ''),
                        'phone': data.get('location', {}).get('phone', ''),

                        # Financial details
                        'stock_symbol': data.get('financial', {}).get('stock_symbol', ''),
                        'stock_exchange': data.get('financial', {}).get('stock_exchange', ''),
                        'total_funding': data.get('financial', {}).get('total_funding', 0),
                        'funding_stage': data.get('financial', {}).get('funding_stage', ''),
                        'funding_date': data.get('financial', {}).get('funding_date', ''),

                        # Funding history
                        'funding_rounds': len(data.get('financial', {}).get('funding', [])) if data.get('financial', {}).get('funding') else 0,
                        'last_funding_amount': data.get('financial', {}).get('funding', [{}])[0].get('amount', 0) if data.get('financial', {}).get('funding') else 0,
                        'last_funding_type': data.get('financial', {}).get('funding', [{}])[0].get('type', '') if data.get('financial', {}).get('funding') else '',

                        # Social presence
                        'linkedin_url': data.get('socials', {}).get('linkedin_url', ''),
                        'linkedin_id': data.get('socials', {}).get('linkedin_id', ''),
                        'twitter_url': data.get('socials', {}).get('twitter_url', ''),
                        'facebook_url': data.get('socials', {}).get('facebook_url', ''),
                        'instagram_url': data.get('socials', {}).get('instagram_url', ''),
                        'youtube_url': data.get('socials', {}).get('youtube_url', ''),
                        'crunchbase_url': data.get('socials', {}).get('crunchbase_url', ''),
                        'angellist_url': data.get('socials', {}).get('angellist_url', ''),
                        'g2_url': data.get('socials', {}).get('g2_url', ''),

                        # Additional metadata
                        'logo_url': data.get('logo_url', ''),
                        'seo_description': data.get('seo_description', ''),
                        'naics_codes': ', '.join(data.get('naics_codes', [])) if data.get('naics_codes') else '',
                        'subsidiaries': ', '.join(data.get('subsidiaries', [])) if data.get('subsidiaries') else '',

                        # Platform indicator (for scoring logic)
                        'platform': 'B2B/Enterprise',
                        'data_source': 'CompanyEnrich'
                    }

                    return {
                        'domain': domain,
                        'success': True,
                        'data': normalized_data
                    }
                elif response.status == 404:
                    return {
                        'domain': domain,
                        'success': False,
                        'error': 'Company not found in Company Enrich database'
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

    def fetch_company_data(self, domain: str) -> Dict:
        domain = self._extract_domain(domain)
        url = f"{self.base_url}?domain={domain}"

        try:
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                data = response.json()

                # Parse and normalize the data for scoring - include ALL available fields
                normalized_data = {
                    'name': data.get('name', domain),
                    'domain': domain,
                    'website': data.get('website', ''),
                    'industry': data.get('industry', 'Unknown'),
                    'industries': ', '.join(data.get('industries', [])) if data.get('industries') else '',
                    'type': data.get('type', ''),
                    'categories': ', '.join(data.get('categories', [])) if data.get('categories') else '',
                    'description': data.get('description', ''),
                    'keywords': ', '.join(data.get('keywords', [])) if data.get('keywords') else '',
                    'technologies': ', '.join(data.get('technologies', [])) if data.get('technologies') else '',
                    'founded_year': data.get('founded_year', 0),
                    'page_rank': data.get('page_rank', 0),

                    # Parse revenue and employees for scoring
                    'estimated_sales_yearly': self._parse_revenue(data.get('revenue', '')),
                    'employee_count': self._parse_employees(data.get('employees', '')),

                    # Raw values for display
                    'revenue_range': data.get('revenue', 'Unknown'),
                    'employee_range': data.get('employees', 'Unknown'),

                    # Location details
                    'country_code': data.get('location', {}).get('country', {}).get('code', 'Unknown'),
                    'country_name': data.get('location', {}).get('country', {}).get('name', ''),
                    'state': data.get('location', {}).get('state', {}).get('name', ''),
                    'state_code': data.get('location', {}).get('state', {}).get('code', ''),
                    'city': data.get('location', {}).get('city', {}).get('name', ''),
                    'address': data.get('location', {}).get('address', ''),
                    'postal_code': data.get('location', {}).get('postal_code', ''),
                    'phone': data.get('location', {}).get('phone', ''),

                    # Financial details
                    'stock_symbol': data.get('financial', {}).get('stock_symbol', ''),
                    'stock_exchange': data.get('financial', {}).get('stock_exchange', ''),
                    'total_funding': data.get('financial', {}).get('total_funding', 0),
                    'funding_stage': data.get('financial', {}).get('funding_stage', ''),
                    'funding_date': data.get('financial', {}).get('funding_date', ''),

                    # Funding history
                    'funding_rounds': len(data.get('financial', {}).get('funding', [])) if data.get('financial', {}).get('funding') else 0,
                    'last_funding_amount': data.get('financial', {}).get('funding', [{}])[0].get('amount', 0) if data.get('financial', {}).get('funding') else 0,
                    'last_funding_type': data.get('financial', {}).get('funding', [{}])[0].get('type', '') if data.get('financial', {}).get('funding') else '',

                    # Social presence
                    'linkedin_url': data.get('socials', {}).get('linkedin_url', ''),
                    'linkedin_id': data.get('socials', {}).get('linkedin_id', ''),
                    'twitter_url': data.get('socials', {}).get('twitter_url', ''),
                    'facebook_url': data.get('socials', {}).get('facebook_url', ''),
                    'instagram_url': data.get('socials', {}).get('instagram_url', ''),
                    'youtube_url': data.get('socials', {}).get('youtube_url', ''),
                    'crunchbase_url': data.get('socials', {}).get('crunchbase_url', ''),
                    'angellist_url': data.get('socials', {}).get('angellist_url', ''),
                    'g2_url': data.get('socials', {}).get('g2_url', ''),

                    # Additional metadata
                    'logo_url': data.get('logo_url', ''),
                    'seo_description': data.get('seo_description', ''),
                    'naics_codes': ', '.join(data.get('naics_codes', [])) if data.get('naics_codes') else '',
                    'subsidiaries': ', '.join(data.get('subsidiaries', [])) if data.get('subsidiaries') else '',

                    # Platform indicator (for scoring logic)
                    'platform': 'B2B/Enterprise',
                    'data_source': 'CompanyEnrich'
                }

                return {
                    'domain': domain,
                    'success': True,
                    'data': normalized_data
                }
            elif response.status_code == 404:
                return {
                    'domain': domain,
                    'success': False,
                    'error': 'Company not found in Company Enrich database'
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