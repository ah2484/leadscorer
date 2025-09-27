"""
Utility functions for lead scoring
"""

def has_sufficient_data_for_scoring(storeleads_data: dict) -> bool:
    """
    Check if StoreLeads data has enough information to generate a meaningful score.

    A meaningful score requires at least ONE of:
    - Revenue data (estimated_sales_yearly > 0)
    - Employee count > 0
    - Monthly visits > 0
    - Platform rank > 0
    - Product count > 0 (for e-commerce)

    Returns:
        bool: True if data is sufficient for scoring, False otherwise
    """
    if not storeleads_data.get('success'):
        return False

    data = storeleads_data.get('data', {})

    # Check for key metrics that contribute to scoring
    has_revenue = (data.get('estimated_sales_yearly', 0) or 0) > 0
    has_employees = (data.get('employee_count', 0) or 0) > 0
    has_traffic = (data.get('estimated_visits', 0) or 0) > 0
    has_rank = (data.get('platform_rank', 0) or 0) > 0
    has_products = (data.get('f_product_count', 0) or data.get('product_count', 0) or 0) > 0
    has_funding = (data.get('total_funding', 0) or 0) > 0

    # If we have at least one meaningful metric, we can score
    return any([has_revenue, has_employees, has_traffic, has_rank, has_products, has_funding])

def should_use_companyenrich(storeleads_data: dict) -> bool:
    """
    Determine if we should fallback to CompanyEnrich API.

    Use CompanyEnrich when:
    - StoreLeads request failed
    - StoreLeads has insufficient data for scoring

    Returns:
        bool: True if should use CompanyEnrich, False otherwise
    """
    return not has_sufficient_data_for_scoring(storeleads_data)