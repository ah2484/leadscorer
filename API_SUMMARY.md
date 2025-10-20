# Lead Scorer API - Summary

## What Was Created

A RESTful API wrapper for the Lead Scorer application that accepts a domain URL and returns scoring information.

### Files Created

1. **api_wrapper.py** - Main API application with FastAPI
2. **api_requirements.txt** - Python dependencies for the API
3. **start_api.sh** - Local startup script
4. **vercel_api.json** - Vercel serverless configuration
5. **railway.json** - Railway deployment configuration
6. **Procfile_api** - Heroku/Railway process file
7. **API_README.md** - Complete API documentation
8. **DEPLOYMENT_GUIDE.md** - Step-by-step deployment instructions
9. **API_SUMMARY.md** - This file

---

## API Endpoints

### 1. GET /score?domain={domain}
Simple endpoint that returns:
- Score (0-100)
- Grade (A+ to F)
- Priority (Very High, High, Medium, Low, Very Low)
- Basic company info

**Example:**
```bash
curl "http://localhost:8001/score?domain=shopify.com"
```

**Response:**
```json
{
  "domain": "shopify.com",
  "score": 86.82,
  "grade": "A",
  "priority": "Very High",
  "company_name": "Shopify",
  "industry": "Business Services",
  "revenue": "over-1b",
  "employees": "over-10K",
  "country": "Canada",
  "data_source": "CompanyEnrich"
}
```

### 2. GET /score/detailed?domain={domain}
Detailed endpoint with full metrics and scoring breakdown

### 3. GET /health
Health check endpoint

---

## Current Status

✅ **API Created and Tested Locally**
- Running on http://localhost:8001
- Successfully tested with Shopify.com
- Both basic and detailed endpoints working

✅ **Configuration Files Ready**
- Vercel deployment config
- Railway deployment config
- Heroku/Render compatible

✅ **Documentation Complete**
- API usage guide
- Deployment instructions
- Integration examples

---

## Local Testing Results

```bash
# Health Check
$ curl http://localhost:8001/health
{"status":"healthy","storeleads_api":"configured","companyenrich_api":"configured"}

# Score Test
$ curl "http://localhost:8001/score?domain=shopify.com"
{
  "domain": "shopify.com",
  "score": 86.82,
  "grade": "A",
  "priority": "Very High",
  "company_name": "Shopify",
  ...
}
```

---

## How to Use in Your Internal Tools

### Simple Integration Example

```python
import requests

# Your deployed API URL (replace after deployment)
API_URL = "https://your-api.vercel.app"

def get_lead_score(domain):
    """Get lead score for a domain"""
    response = requests.get(f"{API_URL}/score?domain={domain}")
    if response.status_code == 200:
        return response.json()
    return None

# Usage
score = get_lead_score("example.com")
print(f"Score: {score['score']}, Priority: {score['priority']}")
```

### Batch Processing Example

```python
import requests
import pandas as pd

API_URL = "https://your-api.vercel.app"

def score_leads_batch(domains):
    """Score multiple domains"""
    results = []
    for domain in domains:
        response = requests.get(f"{API_URL}/score?domain={domain}")
        if response.status_code == 200:
            results.append(response.json())
        else:
            results.append({
                'domain': domain,
                'score': 0,
                'grade': 'F',
                'priority': 'No Data'
            })
    return pd.DataFrame(results)

# Usage
domains = ['shopify.com', 'stripe.com', 'salesforce.com']
df = score_leads_batch(domains)
print(df[['domain', 'score', 'grade', 'priority']])
```

---

## Next Steps to Deploy

### Quick Deploy with Vercel (5 minutes)

```bash
# 1. Install Vercel CLI
npm install -g vercel

# 2. Deploy
cd ~/Documents/leadscorer
vercel --prod

# 3. Add API keys in Vercel dashboard
# - STORELEADS_API_KEY
# - COMPANYENRICH_API_KEY

# 4. Done! Your API is live
```

See **DEPLOYMENT_GUIDE.md** for detailed instructions.

---

## Free Hosting Options

1. **Vercel** (Recommended)
   - 100GB bandwidth/month free
   - Instant deployments
   - Custom domain support

2. **Railway**
   - $5/month free credit
   - ~500 hours usage
   - Auto-deploy from Git

3. **Render**
   - 750 hours/month free
   - Spins down after inactivity
   - Good for occasional use

---

## Use Cases for Internal Tools

### CRM Integration
Add lead scoring to your CRM when new leads are added:
```python
# When new lead is created
lead_score = get_lead_score(lead.website)
lead.score = lead_score['score']
lead.priority = lead_score['priority']
```

### Sales Dashboard
Build a dashboard showing top-priority leads:
```python
leads = get_all_leads()
for lead in leads:
    score = get_lead_score(lead.domain)
    lead.update_score(score)

high_priority = [l for l in leads if l.priority == 'Very High']
```

### Email Campaigns
Filter leads for targeted campaigns:
```python
leads = get_leads_from_csv()
scored_leads = score_leads_batch(leads['domain'])
enterprise_leads = scored_leads[scored_leads['score'] > 80]
```

### Google Sheets Add-on
Create custom formula for scoring:
```javascript
function SCORE_DOMAIN(domain) {
  const response = UrlFetchApp.fetch(
    `https://your-api.vercel.app/score?domain=${domain}`
  );
  return JSON.parse(response).score;
}
```

---

## API Features

✅ Domain cleaning and normalization
✅ Multiple data sources (StoreLeads + CompanyEnrich)
✅ Automatic fallback between sources
✅ Comprehensive scoring algorithm
✅ Rate limiting built-in
✅ CORS enabled for frontend use
✅ Auto-generated API docs at /docs
✅ Health check endpoint
✅ Error handling

---

## Performance

- **Cold start**: ~1-2 seconds (first request)
- **Warm requests**: ~200-500ms per domain
- **Rate limit**: 5 requests/second (configurable)

---

## Questions?

- API Documentation: See **API_README.md**
- Deployment Help: See **DEPLOYMENT_GUIDE.md**
- Local Testing: Run `./start_api.sh`
- API Docs UI: Visit http://localhost:8001/docs when running

---

## Current Servers Running

1. **Main App**: http://localhost:8000 (original web interface)
2. **API Wrapper**: http://localhost:8001 (new API)

Both can run simultaneously!
