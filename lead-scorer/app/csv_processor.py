import pandas as pd
import asyncio
from typing import List, Dict
from datetime import datetime
from tqdm import tqdm
import os

from .storeleads_client import StoreLeadsClient
from .companyenrich_client import CompanyEnrichClient
from .lead_scorer import LeadScorer
from .scoring_utils import should_use_companyenrich

class CSVProcessor:
    def __init__(self):
        self.storeleads_client = StoreLeadsClient()
        self.companyenrich_client = CompanyEnrichClient()
        self.scorer = LeadScorer()

    def read_input_csv(self, file_path: str) -> List[str]:
        try:
            # Try reading with different error handling strategies
            try:
                # First attempt: standard CSV reading
                df = pd.read_csv(file_path)
            except (pd.errors.ParserError, pd.errors.EmptyDataError) as e:
                # If that fails, try reading line by line as simple text
                try:
                    with open(file_path, 'r') as f:
                        lines = f.readlines()

                    # Skip header if it looks like a header
                    if lines and any(h in lines[0].lower() for h in ['domain', 'website', 'url']):
                        lines = lines[1:]

                    # Clean each line
                    domains = []
                    for line in lines:
                        line = line.strip()
                        if line:
                            # Remove quotes and take first part if there are delimiters
                            line = line.replace('"', '').replace("'", '')
                            if ',' in line:
                                line = line.split(',')[0]
                            elif '\t' in line:
                                line = line.split('\t')[0]
                            line = line.strip()
                            if line:
                                domains.append(line)

                    # Create DataFrame from cleaned domains
                    df = pd.DataFrame({'domain': domains})
                    print(f"Read {len(domains)} domains from file")

                except Exception as read_error:
                    print(f"Error reading file line by line: {str(read_error)}")
                    # Last resort: try pandas with minimal parsing
                    df = pd.read_csv(file_path, header=None, names=['domain'], sep='\n', engine='python')
                    print("Warning: Reading file as single column")

            if 'website' in df.columns:
                websites = df['website'].tolist()
            elif 'domain' in df.columns:
                websites = df['domain'].tolist()
            elif 'url' in df.columns:
                websites = df['url'].tolist()
            else:
                websites = df.iloc[:, 0].tolist()

            websites = [str(w).strip() for w in websites if pd.notna(w) and str(w).strip()]

            # Cap at 4000 domains
            if len(websites) > 4000:
                print(f"Warning: Input contains {len(websites)} domains. Limiting to first 4000.")
                websites = websites[:4000]

            return websites
        except Exception as e:
            raise ValueError(f"Error reading CSV file: {str(e)}")

    async def process_websites(self, websites: List[str], session_id: str = None, progress_callback=None) -> pd.DataFrame:
        print(f"\nProcessing {len(websites)} websites...")

        # Progress tracking variables
        storeleads_total = len(websites)
        storeleads_current = 0
        companyenrich_total = 0
        companyenrich_current = 0
        scoring_total = len(websites)
        scoring_current = 0

        def update_progress(stage: str = None, message: str = None, error: str = None):
            if progress_callback:
                progress_data = {
                    'storeleads': {'current': storeleads_current, 'total': storeleads_total},
                    'companyenrich': {'current': companyenrich_current, 'total': companyenrich_total},
                    'scoring': {'current': scoring_current, 'total': scoring_total}
                }
                progress_callback(progress_data, stage, message, error)

        # First try Store Leads API for all domains
        pbar = tqdm(total=len(websites), desc="Fetching data from Store Leads API")

        update_progress('storeleads', "Starting Store Leads API fetch...", None)

        def storeleads_progress():
            nonlocal storeleads_current
            storeleads_current += 1
            pbar.update(1)
            update_progress('storeleads', f"Fetched {storeleads_current}/{storeleads_total} from Store Leads")

        storeleads_results = await self.storeleads_client.fetch_multiple_domains(websites, progress_callback=storeleads_progress)
        pbar.close()

        # Collect domains that need CompanyEnrich fallback
        failed_domains = []
        final_results = []

        for result in storeleads_results:
            # Use the same logic as API to determine if we need CompanyEnrich
            if should_use_companyenrich(result):
                failed_domains.append(result['domain'])
                final_results.append(result)  # Keep for now, will replace if CompanyEnrich has data
            else:
                final_results.append(result)

        # Try Company Enrich API for failed domains
        if failed_domains:
            companyenrich_total = len(failed_domains)
            print(f"\nFetching additional data from Company Enrich API for {len(failed_domains)} domains...")
            pbar = tqdm(total=len(failed_domains), desc="Fetching from Company Enrich")

            update_progress('companyenrich', f"Starting Company Enrich API for {len(failed_domains)} domains...", None)

            for i, domain in enumerate(failed_domains):
                companyenrich_current = i + 1
                try:
                    enrich_result = self.companyenrich_client.fetch_company_data(domain)
                    if enrich_result['success']:
                        # Replace the failed result with Company Enrich data
                        for j, result in enumerate(final_results):
                            if result['domain'] == domain:
                                final_results[j] = enrich_result
                                break
                    update_progress('companyenrich', f"Fetched {companyenrich_current}/{companyenrich_total} from Company Enrich")
                except Exception as e:
                    update_progress('companyenrich', None, f"Error fetching {domain}: {str(e)}")
                pbar.update(1)

            pbar.close()

        api_results = final_results

        print("\nScoring leads...")
        scored_results = []

        update_progress('scoring', "Starting lead scoring...", None)

        for idx, result in enumerate(tqdm(api_results, desc="Calculating lead scores")):
            scoring_current = idx + 1
            try:
                score_data = self.scorer.calculate_score(result)
                update_progress('scoring', f"Scored {scoring_current}/{scoring_total} leads")
            except Exception as e:
                update_progress('scoring', None, f"Error scoring {result.get('domain', 'unknown')}: {str(e)}")
                # Create a minimal score data for failed scoring
                score_data = {
                    'domain': result.get('domain', 'unknown'),
                    'score': 0,
                    'grade': 'F',
                    'priority': 'Error',
                    'metrics': {},
                    'breakdown': {}
                }

            # Core scoring fields
            row = {
                'domain': score_data['domain'],
                'score': score_data['score'],
                'grade': score_data['grade'],
                'priority': score_data['priority'],
                'data_source': score_data['metrics'].get('data_source', 'StoreLeads') if 'metrics' in score_data else 'Unknown',

                # Company info
                'company_name': score_data['metrics'].get('name', '') if 'metrics' in score_data else '',
                'website': score_data['metrics'].get('website', '') if 'metrics' in score_data else '',
                'type': score_data['metrics'].get('type', '') if 'metrics' in score_data else '',

                # Revenue and size metrics
                'yearly_revenue': score_data['metrics'].get('yearly_revenue', 0) if 'metrics' in score_data else 0,
                'revenue_range': score_data['metrics'].get('revenue_range', '') if 'metrics' in score_data else '',
                'employee_count': score_data['metrics'].get('employee_count', 0) if 'metrics' in score_data else 0,
                'employee_range': score_data['metrics'].get('employee_range', '') if 'metrics' in score_data else '',

                # Industry and categories
                'industry': score_data['metrics'].get('industry', '') if 'metrics' in score_data else '',
                'industries': score_data['metrics'].get('industries', '') if 'metrics' in score_data else '',
                'categories': score_data['metrics'].get('categories', '') if 'metrics' in score_data else '',

                # Location
                'country': score_data['metrics'].get('country_name', score_data['metrics'].get('country', '')) if 'metrics' in score_data else '',
                'country_code': score_data['metrics'].get('country_code', '') if 'metrics' in score_data else '',
                'state': score_data['metrics'].get('state', '') if 'metrics' in score_data else '',
                'state_code': score_data['metrics'].get('state_code', '') if 'metrics' in score_data else '',
                'city': score_data['metrics'].get('city', '') if 'metrics' in score_data else '',
                'address': score_data['metrics'].get('address', '') if 'metrics' in score_data else '',
                'postal_code': score_data['metrics'].get('postal_code', '') if 'metrics' in score_data else '',
                'phone': score_data['metrics'].get('phone', '') if 'metrics' in score_data else '',

                # Financial details
                'stock_symbol': score_data['metrics'].get('stock_symbol', '') if 'metrics' in score_data else '',
                'stock_exchange': score_data['metrics'].get('stock_exchange', '') if 'metrics' in score_data else '',
                'total_funding': score_data['metrics'].get('total_funding', 0) if 'metrics' in score_data else 0,
                'funding_stage': score_data['metrics'].get('funding_stage', '') if 'metrics' in score_data else '',
                'funding_rounds': score_data['metrics'].get('funding_rounds', 0) if 'metrics' in score_data else 0,
                'last_funding_amount': score_data['metrics'].get('last_funding_amount', 0) if 'metrics' in score_data else 0,
                'last_funding_type': score_data['metrics'].get('last_funding_type', '') if 'metrics' in score_data else '',

                # Company metadata
                'founded_year': score_data['metrics'].get('founded_year', 0) if 'metrics' in score_data else 0,
                'page_rank': score_data['metrics'].get('page_rank', 0) if 'metrics' in score_data else 0,
                'technologies': score_data['metrics'].get('technologies', '') if 'metrics' in score_data else '',
                'keywords': score_data['metrics'].get('keywords', '') if 'metrics' in score_data else '',

                # Social presence
                'linkedin_url': score_data['metrics'].get('linkedin_url', '') if 'metrics' in score_data else '',
                'twitter_url': score_data['metrics'].get('twitter_url', '') if 'metrics' in score_data else '',
                'facebook_url': score_data['metrics'].get('facebook_url', '') if 'metrics' in score_data else '',
                'crunchbase_url': score_data['metrics'].get('crunchbase_url', '') if 'metrics' in score_data else '',

                # E-commerce specific (from StoreLeads)
                'platform': score_data['metrics'].get('platform', '') if 'metrics' in score_data else '',
                'monthly_visits': score_data['metrics'].get('monthly_visits', 0) if 'metrics' in score_data else 0,
                'platform_rank': score_data['metrics'].get('platform_rank', 0) if 'metrics' in score_data else 0,
                'rank_percentile': score_data['metrics'].get('rank_percentile', 0) if 'metrics' in score_data else 0,
                'product_count': score_data['metrics'].get('product_count', 0) if 'metrics' in score_data else 0,
                'monthly_app_spend': score_data['metrics'].get('monthly_app_spend', 0) if 'metrics' in score_data else 0,

                # Score breakdown
                'revenue_contrib': score_data['breakdown'].get('revenue_contribution', 0) if 'breakdown' in score_data else 0,
                'size_contrib': score_data['breakdown'].get('size_contribution', 0) if 'breakdown' in score_data else 0,
                'traffic_contrib': score_data['breakdown'].get('traffic_contribution', 0) if 'breakdown' in score_data else 0,
                'rank_contrib': score_data['breakdown'].get('rank_contribution', 0) if 'breakdown' in score_data else 0
            }

            if 'reason' in score_data:
                row['notes'] = score_data['reason']

            scored_results.append(row)

        df = pd.DataFrame(scored_results)
        df = df.sort_values('score', ascending=False)
        df = df.reset_index(drop=True)
        df.index += 1

        return df

    def save_results(self, df: pd.DataFrame, output_path: str = None) -> str:
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"output/lead_scores_{timestamp}.csv"

        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        df.to_csv(output_path)
        return output_path

    def generate_summary(self, df: pd.DataFrame) -> Dict:
        summary = {
            'total_leads': len(df),
            'average_score': df['score'].mean(),
            'score_distribution': {
                'A+': len(df[df['grade'] == 'A+']),
                'A': len(df[df['grade'] == 'A']),
                'B+': len(df[df['grade'] == 'B+']),
                'B': len(df[df['grade'] == 'B']),
                'C+': len(df[df['grade'] == 'C+']),
                'C': len(df[df['grade'] == 'C']),
                'D': len(df[df['grade'] == 'D']),
                'F': len(df[df['grade'] == 'F'])
            },
            'priority_distribution': {
                'Very High': len(df[df['priority'] == 'Very High']),
                'High': len(df[df['priority'] == 'High']),
                'Medium': len(df[df['priority'] == 'Medium']),
                'Low': len(df[df['priority'] == 'Low']),
                'Very Low': len(df[df['priority'] == 'Very Low']),
                'No Data': len(df[df['priority'] == 'No Data'])
            },
            'top_10_leads': df.head(10)[['domain', 'score', 'grade', 'priority', 'yearly_revenue', 'employee_count']].to_dict('records')
        }
        return summary