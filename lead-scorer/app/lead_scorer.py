from typing import Dict, Optional
import math

class LeadScorer:
    def __init__(self):
        self.revenue_brackets = {
            'very_high': 10000000,
            'high': 1000000,
            'medium': 100000,
            'low': 10000
        }

        self.employee_brackets = {
            'enterprise': 100,
            'mid_market': 25,
            'small': 10,
            'micro': 1
        }

    def calculate_score(self, domain_data: Dict) -> Dict:
        if not domain_data.get('success'):
            return {
                'domain': domain_data.get('domain', 'unknown'),
                'score': 0,
                'grade': 'F',
                'priority': 'No Data',
                'reason': domain_data.get('error', 'No data available'),
                'metrics': {}
            }

        data = domain_data['data']
        score = 0
        metrics = {}

        yearly_revenue = data.get('estimated_sales_yearly', 0) or 0
        metrics['yearly_revenue'] = yearly_revenue
        revenue_score = self._calculate_revenue_score(yearly_revenue)
        score += revenue_score * 0.4

        employee_count = data.get('employee_count', 0) or 0
        metrics['employee_count'] = employee_count
        size_score = self._calculate_size_score(employee_count)
        score += size_score * 0.3

        monthly_visits = data.get('estimated_visits', 0) or 0
        metrics['monthly_visits'] = monthly_visits
        traffic_score = self._calculate_traffic_score(monthly_visits)
        score += traffic_score * 0.15

        platform_rank = data.get('platform_rank', 0) or 0
        rank_percentile = data.get('rank_percentile', 0) or 0
        page_rank = data.get('page_rank', 0) or 0
        metrics['platform_rank'] = platform_rank
        metrics['rank_percentile'] = rank_percentile
        rank_score = self._calculate_rank_score(platform_rank, rank_percentile, page_rank)
        score += rank_score * 0.15

        # Add bonus for funding (for B2B companies)
        total_funding = data.get('total_funding', 0) or 0
        if total_funding > 0:
            funding_bonus = self._calculate_funding_bonus(total_funding)
            score += funding_bonus * 0.05  # 5% bonus weight for funding

        final_score = min(100, max(0, score))

        grade = self._get_grade(final_score)
        priority = self._get_priority(final_score)

        # Pass through all available metrics
        metrics['product_count'] = data.get('f_product_count', 0) or data.get('product_count', 0) or 0
        metrics['monthly_app_spend'] = data.get('monthly_app_spend', 0) or 0
        metrics['platform'] = data.get('platform', 'Unknown')
        metrics['data_source'] = data.get('data_source', 'StoreLeads')

        # Company information
        metrics['name'] = data.get('name', '')
        metrics['website'] = data.get('website', '')
        metrics['type'] = data.get('type', '')
        metrics['industry'] = data.get('industry', '')
        metrics['industries'] = data.get('industries', '')
        metrics['categories'] = data.get('categories', '')
        metrics['keywords'] = data.get('keywords', '')
        metrics['technologies'] = data.get('technologies', '')

        # Revenue display values
        metrics['revenue_range'] = data.get('revenue_range', '')
        metrics['employee_range'] = data.get('employee_range', '')

        # Location
        metrics['country'] = data.get('country_code', 'Unknown')
        metrics['country_name'] = data.get('country_name', '')
        metrics['state'] = data.get('state', '')
        metrics['state_code'] = data.get('state_code', '')
        metrics['city'] = data.get('city', '')
        metrics['address'] = data.get('address', '')
        metrics['postal_code'] = data.get('postal_code', '')
        metrics['phone'] = data.get('phone', '')

        # Financial
        metrics['total_funding'] = data.get('total_funding', 0)
        metrics['stock_symbol'] = data.get('stock_symbol', '')
        metrics['stock_exchange'] = data.get('stock_exchange', '')
        metrics['funding_stage'] = data.get('funding_stage', '')
        metrics['funding_rounds'] = data.get('funding_rounds', 0)
        metrics['last_funding_amount'] = data.get('last_funding_amount', 0)
        metrics['last_funding_type'] = data.get('last_funding_type', '')

        # Additional metrics
        metrics['page_rank'] = data.get('page_rank', 0)
        metrics['founded_year'] = data.get('founded_year', 0)

        # Social URLs
        metrics['linkedin_url'] = data.get('linkedin_url', '')
        metrics['twitter_url'] = data.get('twitter_url', '')
        metrics['facebook_url'] = data.get('facebook_url', '')
        metrics['crunchbase_url'] = data.get('crunchbase_url', '')

        return {
            'domain': domain_data['domain'],
            'score': round(final_score, 2),
            'grade': grade,
            'priority': priority,
            'metrics': metrics,
            'breakdown': {
                'revenue_contribution': round(revenue_score * 0.4, 2),
                'size_contribution': round(size_score * 0.3, 2),
                'traffic_contribution': round(traffic_score * 0.15, 2),
                'rank_contribution': round(rank_score * 0.15, 2)
            }
        }

    def _calculate_revenue_score(self, yearly_revenue: float) -> float:
        if yearly_revenue >= self.revenue_brackets['very_high']:
            return 100
        elif yearly_revenue >= self.revenue_brackets['high']:
            return 80 + (yearly_revenue - self.revenue_brackets['high']) / (self.revenue_brackets['very_high'] - self.revenue_brackets['high']) * 20
        elif yearly_revenue >= self.revenue_brackets['medium']:
            return 60 + (yearly_revenue - self.revenue_brackets['medium']) / (self.revenue_brackets['high'] - self.revenue_brackets['medium']) * 20
        elif yearly_revenue >= self.revenue_brackets['low']:
            return 40 + (yearly_revenue - self.revenue_brackets['low']) / (self.revenue_brackets['medium'] - self.revenue_brackets['low']) * 20
        elif yearly_revenue > 0:
            return (yearly_revenue / self.revenue_brackets['low']) * 40
        else:
            return 0

    def _calculate_size_score(self, employee_count: int) -> float:
        if employee_count >= self.employee_brackets['enterprise']:
            return 100
        elif employee_count >= self.employee_brackets['mid_market']:
            return 75 + (employee_count - self.employee_brackets['mid_market']) / (self.employee_brackets['enterprise'] - self.employee_brackets['mid_market']) * 25
        elif employee_count >= self.employee_brackets['small']:
            return 50 + (employee_count - self.employee_brackets['small']) / (self.employee_brackets['mid_market'] - self.employee_brackets['small']) * 25
        elif employee_count >= self.employee_brackets['micro']:
            return 25 + (employee_count - self.employee_brackets['micro']) / (self.employee_brackets['small'] - self.employee_brackets['micro']) * 25
        else:
            return 0

    def _calculate_traffic_score(self, monthly_visits: float) -> float:
        if monthly_visits >= 1000000:
            return 100
        elif monthly_visits >= 100000:
            return 70 + (monthly_visits - 100000) / 900000 * 30
        elif monthly_visits >= 10000:
            return 40 + (monthly_visits - 10000) / 90000 * 30
        elif monthly_visits >= 1000:
            return 20 + (monthly_visits - 1000) / 9000 * 20
        elif monthly_visits > 0:
            return (monthly_visits / 1000) * 20
        else:
            return 0

    def _calculate_rank_score(self, platform_rank: int, rank_percentile: float, page_rank: float = 0) -> float:
        # If we have rank percentile, use it
        if rank_percentile > 0:
            return rank_percentile

        # If we have platform rank (e-commerce)
        elif platform_rank > 0:
            if platform_rank <= 100:
                return 95
            elif platform_rank <= 500:
                return 85
            elif platform_rank <= 1000:
                return 75
            elif platform_rank <= 5000:
                return 60
            elif platform_rank <= 10000:
                return 40
            else:
                return max(0, 40 - math.log10(platform_rank) * 10)

        # If we have page rank (B2B/general websites)
        elif page_rank > 0:
            # Page rank is typically 0-10, with 10 being the best
            return min(100, page_rank * 10)

        else:
            return 0

    def _calculate_funding_bonus(self, total_funding: float) -> float:
        """Calculate bonus score based on total funding"""
        if total_funding >= 1000000000:  # $1B+
            return 100
        elif total_funding >= 100000000:  # $100M+
            return 80
        elif total_funding >= 10000000:  # $10M+
            return 60
        elif total_funding >= 1000000:  # $1M+
            return 40
        elif total_funding > 0:
            return 20
        else:
            return 0

    def _get_grade(self, score: float) -> str:
        if score >= 90:
            return 'A+'
        elif score >= 80:
            return 'A'
        elif score >= 70:
            return 'B+'
        elif score >= 60:
            return 'B'
        elif score >= 50:
            return 'C+'
        elif score >= 40:
            return 'C'
        elif score >= 30:
            return 'D'
        else:
            return 'F'

    def _get_priority(self, score: float) -> str:
        if score >= 80:
            return 'Very High'
        elif score >= 60:
            return 'High'
        elif score >= 40:
            return 'Medium'
        elif score >= 20:
            return 'Low'
        else:
            return 'Very Low'