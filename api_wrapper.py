from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import os
from dotenv import load_dotenv

from app.storeleads_client import StoreLeadsClient
from app.companyenrich_client import CompanyEnrichClient
from app.lead_scorer import LeadScorer

load_dotenv()

app = FastAPI(
    title="Lead Scorer API",
    description="API to score leads based on domain URL",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize clients
try:
    storeleads_client = StoreLeadsClient()
    companyenrich_client = CompanyEnrichClient()
    scorer = LeadScorer()
except Exception as e:
    print(f"Warning: Could not initialize all clients: {e}")
    storeleads_client = None
    companyenrich_client = None
    scorer = LeadScorer()


class ScoreResponse(BaseModel):
    domain: str
    score: float
    grade: str
    priority: str
    company_name: Optional[str] = None
    industry: Optional[str] = None
    revenue: Optional[str] = None
    employees: Optional[str] = None
    country: Optional[str] = None
    data_source: Optional[str] = None


@app.get("/")
async def root():
    return {
        "message": "Lead Scorer API",
        "version": "1.0.0",
        "endpoints": {
            "/score": "GET - Score a single domain",
            "/health": "GET - Health check"
        }
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "storeleads_api": "configured" if storeleads_client else "not configured",
        "companyenrich_api": "configured" if companyenrich_client else "not configured"
    }


@app.get("/score", response_model=ScoreResponse)
async def score_domain(
    domain: str = Query(..., description="Domain URL to score (e.g., example.com or https://example.com)")
):
    """
    Score a domain and return the lead score, grade, and priority.

    The API will try StoreLeads first (for e-commerce data), and fallback to CompanyEnrich for B2B companies.
    """
    if not domain:
        raise HTTPException(status_code=400, detail="Domain parameter is required")

    # Try StoreLeads API first
    domain_data = None
    if storeleads_client:
        try:
            domain_data = storeleads_client.fetch_domain_data(domain)
        except Exception as e:
            print(f"StoreLeads API error: {e}")

    # If StoreLeads didn't find data, try CompanyEnrich
    if not domain_data or not domain_data.get('success'):
        if companyenrich_client:
            try:
                domain_data = companyenrich_client.fetch_company_data(domain)
            except Exception as e:
                print(f"CompanyEnrich API error: {e}")

    # If we still don't have data, return error
    if not domain_data or not domain_data.get('success'):
        raise HTTPException(
            status_code=404,
            detail=f"Domain not found in any database: {domain_data.get('error', 'Unknown error') if domain_data else 'No data available'}"
        )

    # Calculate score
    result = scorer.calculate_score(domain_data)

    # Extract metrics for response
    metrics = result.get('metrics', {})

    return ScoreResponse(
        domain=result['domain'],
        score=result['score'],
        grade=result['grade'],
        priority=result['priority'],
        company_name=metrics.get('name', None),
        industry=metrics.get('industry', None),
        revenue=metrics.get('revenue_range', None),
        employees=metrics.get('employee_range', None),
        country=metrics.get('country_name', None) or metrics.get('country', None),
        data_source=metrics.get('data_source', None)
    )


@app.get("/score/detailed")
async def score_domain_detailed(
    domain: str = Query(..., description="Domain URL to score")
):
    """
    Score a domain and return detailed scoring breakdown and all available metrics.
    """
    if not domain:
        raise HTTPException(status_code=400, detail="Domain parameter is required")

    # Try StoreLeads API first
    domain_data = None
    if storeleads_client:
        try:
            domain_data = storeleads_client.fetch_domain_data(domain)
        except Exception as e:
            print(f"StoreLeads API error: {e}")

    # If StoreLeads didn't find data, try CompanyEnrich
    if not domain_data or not domain_data.get('success'):
        if companyenrich_client:
            try:
                domain_data = companyenrich_client.fetch_company_data(domain)
            except Exception as e:
                print(f"CompanyEnrich API error: {e}")

    # If we still don't have data, return error
    if not domain_data or not domain_data.get('success'):
        raise HTTPException(
            status_code=404,
            detail=f"Domain not found in any database: {domain_data.get('error', 'Unknown error') if domain_data else 'No data available'}"
        )

    # Calculate score
    result = scorer.calculate_score(domain_data)

    return result


# For serverless deployment (Vercel)
# This is used by Vercel's Python runtime
if __name__ != "__main__":
    # This allows Vercel to import the app
    handler = app
