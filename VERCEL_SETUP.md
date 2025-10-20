# Vercel Deployment - Final Setup

## Your API has been deployed! ✅

**Latest Production URL**: https://leadscorer-h7cbp8s18-sieve-fresh.vercel.app

**Production Domain** (once protection is disabled): https://leadscorer.vercel.app

---

## ⚠️ Important: Disable Deployment Protection

Your API is currently protected by Vercel authentication, which prevents public access. You need to disable this for your API to work.

### Steps to Disable Protection:

1. **Go to Vercel Dashboard**
   - Visit: https://vercel.com/sieve-fresh/leadscorer

2. **Navigate to Settings**
   - Click on "Settings" tab at the top

3. **Find Deployment Protection**
   - Look for "Deployment Protection" in the left sidebar
   - Or go directly to: https://vercel.com/sieve-fresh/leadscorer/settings/deployment-protection

4. **Disable Protection**
   - Click on "Deployment Protection"
   - Change setting to "Disabled" or "Standard Protection Only"
   - Click "Save"

5. **Redeploy (Optional)**
   ```bash
   cd ~/Documents/leadscorer
   vercel --prod
   ```

---

## Testing Your API

Once protection is disabled, test with:

```bash
# Health check
curl https://leadscorer.vercel.app/health

# Score a domain
curl "https://leadscorer.vercel.app/score?domain=shopify.com"
```

---

## Your API Endpoints

### Base URL
```
https://leadscorer.vercel.app
```

### Available Endpoints

#### 1. GET /
API information and available endpoints

#### 2. GET /health
```bash
curl https://leadscorer.vercel.app/health
```

**Response:**
```json
{
  "status": "healthy",
  "storeleads_api": "configured",
  "companyenrich_api": "configured"
}
```

#### 3. GET /score?domain={domain}
```bash
curl "https://leadscorer.vercel.app/score?domain=shopify.com"
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

#### 4. GET /score/detailed?domain={domain}
Complete metrics and scoring breakdown

---

## Environment Variables Configured ✅

The following environment variables are already set in your Vercel project:

- ✅ `STORELEADS_API_KEY` - Configured
- ✅ `COMPANYENRICH_API_KEY` - Configured

---

## Using Your API in Internal Tools

### Python Example
```python
import requests

API_URL = "https://leadscorer.vercel.app"

def score_lead(domain):
    response = requests.get(f"{API_URL}/score?domain={domain}")
    if response.status_code == 200:
        return response.json()
    return None

# Usage
result = score_lead("shopify.com")
print(f"Score: {result['score']}, Grade: {result['grade']}, Priority: {result['priority']}")
```

### JavaScript Example
```javascript
const API_URL = "https://leadscorer.vercel.app";

async function scoreLead(domain) {
  const response = await fetch(`${API_URL}/score?domain=${domain}`);
  return await response.json();
}

// Usage
scoreLead("shopify.com").then(result => {
  console.log(`Score: ${result.score}, Grade: ${result.grade}`);
});
```

### cURL Example
```bash
curl "https://leadscorer.vercel.app/score?domain=shopify.com" | jq
```

---

## API Documentation

Once deployed and protection is disabled, you can access:

- **Swagger UI**: https://leadscorer.vercel.app/docs
- **ReDoc**: https://leadscorer.vercel.app/redoc

---

## Monitoring & Logs

View real-time logs and analytics:
- **Vercel Dashboard**: https://vercel.com/sieve-fresh/leadscorer
- **Deployments**: https://vercel.com/sieve-fresh/leadscorer/deployments
- **Logs**: Click on any deployment to see logs

---

## Next Steps

1. ✅ API Deployed to Vercel
2. ✅ Environment Variables Configured
3. ⚠️ **Disable Deployment Protection** (see instructions above)
4. 🔄 Test the API endpoints
5. 🚀 Integrate into your internal tools

---

## Custom Domain (Optional)

To use your own domain:

1. Go to https://vercel.com/sieve-fresh/leadscorer/settings/domains
2. Click "Add Domain"
3. Enter your domain (e.g., api.yourdomain.com)
4. Follow DNS configuration instructions
5. Your API will be available at your custom domain!

---

## Support

- **API Docs**: See API_README.md
- **Deployment Guide**: See DEPLOYMENT_GUIDE.md
- **Vercel Docs**: https://vercel.com/docs

---

## Current Status

✅ **Deployed Successfully**
✅ **Environment Variables Set**
⚠️ **Deployment Protection Active** - Needs to be disabled
✅ **Ready to Use** - Once protection is removed

**Your API is ready to power your internal tools!** 🚀
