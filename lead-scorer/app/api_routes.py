"""
API routes for HubSpot integration and domain scoring
"""
from fastapi import APIRouter, HTTPException, Header, BackgroundTasks, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict
import asyncio
import aiohttp
import uuid
from datetime import datetime
import os
from dotenv import load_dotenv

from .database import Database
from .lead_scorer import LeadScorer
from .storeleads_client import StoreLeadsClient
from .companyenrich_client import CompanyEnrichClient
from .scoring_utils import should_use_companyenrich

load_dotenv()

router = APIRouter(prefix="/api", tags=["Lead Scoring API"])

# Initialize components
db = Database()
lead_scorer = LeadScorer()
storeleads_client = StoreLeadsClient()
companyenrich_client = CompanyEnrichClient()

# API Key configuration
API_KEY = os.getenv("LEADSCORER_API_KEY", "default-api-key-change-this")

class BatchRequest(BaseModel):
    domains: List[str] = Field(..., min_items=1, max_items=4000)
    webhook_url: Optional[str] = None
    use_cache: bool = True

    @validator('domains')
    def validate_domains(cls, v):
        # Clean and validate domains
        cleaned = []
        for domain in v:
            # Remove protocol and www
            domain = domain.strip().lower()
            domain = domain.replace("https://", "").replace("http://", "")
            domain = domain.replace("www.", "")
            # Remove paths
            if "/" in domain:
                domain = domain.split("/")[0]
            if domain:
                cleaned.append(domain)
        return cleaned

class ScoreResponse(BaseModel):
    domain: str
    score: int
    grade: str
    priority: str
    attributes: Optional[Dict] = {}
    last_updated: str
    cached: bool = False

class BatchStatusResponse(BaseModel):
    job_id: str
    status: str
    total_domains: int
    processed_domains: int
    successful_domains: int
    failed_domains: int
    progress_percentage: float
    created_at: str
    completed_at: Optional[str] = None
    results_summary: Optional[Dict] = None

async def verify_api_key(x_api_key: str = Header(None)):
    """Verify API key for authentication"""
    if not x_api_key or x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")
    return True

async def score_domain(domain: str, use_cache: bool = True) -> Dict:
    """Score a single domain"""
    # Check cache first
    if use_cache:
        cached = db.get_scored_domain(domain)
        if cached:
            return {**cached, "cached": True}

    # Score the domain using existing logic
    try:
        # Always try StoreLeads first (it's faster)
        async with aiohttp.ClientSession() as session:
            result = await storeleads_client.fetch_domain_data_async(session, domain)

        # Only use CompanyEnrich if StoreLeads doesn't have sufficient data
        if should_use_companyenrich(result):
            # Fallback to CompanyEnrich for better data
            async with aiohttp.ClientSession() as session:
                result = await companyenrich_client.fetch_company_data_async(session, domain)

        # Calculate score, grade, and priority
        scoring_result = lead_scorer.calculate_score(result)

        # Extract key attributes for storage
        attributes = {
            "company_name": scoring_result.get("metrics", {}).get("name", ""),
            "industry": scoring_result.get("metrics", {}).get("industry", ""),
            "employee_count": scoring_result.get("metrics", {}).get("employee_count", 0),
            "yearly_revenue": scoring_result.get("metrics", {}).get("yearly_revenue", 0),
            "monthly_visits": scoring_result.get("metrics", {}).get("monthly_visits", 0),
            "country": scoring_result.get("metrics", {}).get("country", ""),
            "platform": scoring_result.get("metrics", {}).get("platform", ""),
        }

        # Save to cache
        db.save_scored_domain(
            domain=domain,
            score=int(scoring_result["score"]),
            grade=scoring_result["grade"],
            priority=scoring_result["priority"],
            attributes=attributes
        )

        return {
            "domain": domain,
            "score": int(scoring_result["score"]),
            "grade": scoring_result["grade"],
            "priority": scoring_result["priority"],
            "attributes": attributes,
            "last_updated": datetime.now().isoformat(),
            "cached": False
        }

    except Exception as e:
        # Save failed attempt with score 0
        db.save_scored_domain(
            domain=domain,
            score=0,
            grade="F",
            priority="Very Low",
            attributes={"error": str(e)}
        )

        return {
            "domain": domain,
            "score": 0,
            "grade": "F",
            "priority": "Very Low",
            "attributes": {"error": str(e)},
            "last_updated": datetime.now().isoformat(),
            "cached": False
        }

@router.get("/score/{domain}", response_model=ScoreResponse)
async def get_domain_score(
    domain: str,
    use_cache: bool = True,
    authenticated: bool = Depends(verify_api_key)
):
    """
    Get score, grade, and priority for a single domain.

    - **domain**: The domain to score (e.g., example.com)
    - **use_cache**: Whether to use cached results if available (default: true)
    """
    result = await score_domain(domain, use_cache)
    return ScoreResponse(**result)

@router.post("/score-batch")
async def score_batch(
    request: BatchRequest,
    background_tasks: BackgroundTasks,
    authenticated: bool = Depends(verify_api_key)
):
    """
    Score multiple domains in batch.

    - Accepts up to 4000 domains per batch
    - Returns a job_id immediately
    - Processes domains in the background
    - Sends results to webhook_url when complete (if provided)
    """
    job_id = str(uuid.uuid4())

    # Create batch job in database
    db.create_batch_job(
        job_id=job_id,
        total_domains=len(request.domains),
        webhook_url=request.webhook_url
    )

    # Start background processing
    background_tasks.add_task(
        process_batch,
        job_id,
        request.domains,
        request.webhook_url,
        request.use_cache
    )

    return {
        "job_id": job_id,
        "status": "processing",
        "total_domains": len(request.domains),
        "message": "Batch processing started. Use /api/batch-status/{job_id} to check progress."
    }

async def process_batch(job_id: str, domains: List[str], webhook_url: Optional[str], use_cache: bool):
    """Process domains in batch"""
    processed = 0
    successful = 0
    failed = 0
    results = []

    # Check cache for all domains first if use_cache is True
    cached_results = {}
    domains_to_process = []

    if use_cache:
        cached_results = db.get_batch_domains(domains)
        domains_to_process = [d for d in domains if d.lower() not in cached_results]
    else:
        domains_to_process = domains

    # Add cached results
    for domain, data in cached_results.items():
        results.append({**data, "cached": True})
        processed += 1
        successful += 1

    # Update progress after cached results
    db.update_batch_job(
        job_id=job_id,
        processed=processed,
        successful=successful
    )

    # Process remaining domains
    for domain in domains_to_process:
        try:
            result = await score_domain(domain, use_cache=False)
            results.append(result)
            successful += 1
        except Exception as e:
            results.append({
                "domain": domain,
                "score": 0,
                "grade": "F",
                "priority": "Very Low",
                "error": str(e)
            })
            failed += 1

        processed += 1

        # Update progress
        db.update_batch_job(
            job_id=job_id,
            processed=processed,
            successful=successful,
            failed=failed
        )

        # Rate limiting - wait a bit between requests
        await asyncio.sleep(0.5)

    # Create summary
    summary = {
        "total": len(domains),
        "successful": successful,
        "failed": failed,
        "average_score": sum(r.get("score", 0) for r in results) / len(results) if results else 0,
        "grade_distribution": {},
        "priority_distribution": {}
    }

    # Count grades and priorities
    for result in results:
        grade = result.get("grade", "F")
        priority = result.get("priority", "Very Low")
        summary["grade_distribution"][grade] = summary["grade_distribution"].get(grade, 0) + 1
        summary["priority_distribution"][priority] = summary["priority_distribution"].get(priority, 0) + 1

    # Update job as completed
    db.update_batch_job(
        job_id=job_id,
        status="completed",
        results={"summary": summary, "domains": results}
    )

    # Send webhook if provided
    if webhook_url:
        await send_webhook(webhook_url, {
            "event": "batch_scoring_complete",
            "job_id": job_id,
            "summary": summary,
            "results": results
        })

async def send_webhook(webhook_url: str, data: Dict):
    """Send webhook notification"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                webhook_url,
                json=data,
                headers={"Content-Type": "application/json"}
            ) as response:
                return response.status == 200
    except Exception as e:
        print(f"Webhook failed: {e}")
        return False

@router.get("/batch-status/{job_id}", response_model=BatchStatusResponse)
async def get_batch_status(
    job_id: str,
    authenticated: bool = Depends(verify_api_key)
):
    """
    Get the status of a batch job.

    - **job_id**: The job ID returned from /api/score-batch
    """
    job = db.get_batch_job(job_id)

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    progress_percentage = (job["processed_domains"] / job["total_domains"] * 100) if job["total_domains"] > 0 else 0

    return BatchStatusResponse(
        job_id=job["job_id"],
        status=job["status"],
        total_domains=job["total_domains"],
        processed_domains=job["processed_domains"],
        successful_domains=job["successful_domains"],
        failed_domains=job["failed_domains"],
        progress_percentage=round(progress_percentage, 2),
        created_at=job["created_at"],
        completed_at=job["completed_at"],
        results_summary=job["results"]["summary"] if job["results"] else None
    )

@router.get("/batch-results/{job_id}")
async def get_batch_results(
    job_id: str,
    authenticated: bool = Depends(verify_api_key)
):
    """
    Get the full results of a completed batch job.

    - **job_id**: The job ID returned from /api/score-batch
    """
    job = db.get_batch_job(job_id)

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    if job["status"] != "completed":
        raise HTTPException(status_code=400, detail="Job not completed yet")

    return job["results"]

@router.post("/webhook-test")
async def test_webhook(
    webhook_url: str,
    authenticated: bool = Depends(verify_api_key)
):
    """
    Test a webhook URL by sending a sample payload.

    - **webhook_url**: The URL to test
    """
    test_data = {
        "event": "webhook_test",
        "timestamp": datetime.now().isoformat(),
        "sample_result": {
            "domain": "example.com",
            "score": 75,
            "grade": "B+",
            "priority": "High"
        }
    }

    success = await send_webhook(webhook_url, test_data)

    if success:
        return {"status": "success", "message": "Webhook test successful"}
    else:
        raise HTTPException(status_code=400, detail="Webhook test failed")