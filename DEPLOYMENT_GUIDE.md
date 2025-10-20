# Lead Scorer API - Deployment Guide

## Quick Start

Your API is ready to deploy! Choose one of the free serverless platforms below.

## Option 1: Vercel (Recommended - Easiest)

Vercel offers free serverless hosting with excellent performance.

### Step 1: Install Vercel CLI
```bash
npm install -g vercel
```

### Step 2: Login to Vercel
```bash
vercel login
```

### Step 3: Deploy from the project directory
```bash
cd ~/Documents/leadscorer
vercel --prod
```

### Step 4: Set Environment Variables
After deployment, add your API keys in the Vercel dashboard:

1. Go to your project on vercel.com
2. Navigate to Settings > Environment Variables
3. Add the following variables:
   - `STORELEADS_API_KEY` = your_key_here
   - `COMPANYENRICH_API_KEY` = your_key_here
   - `API_RATE_LIMIT` = 5

### Step 5: Redeploy
```bash
vercel --prod
```

Your API will be live at: `https://your-project.vercel.app`

**Example Usage:**
```bash
curl "https://your-project.vercel.app/score?domain=shopify.com"
```

---

## Option 2: Railway

Railway offers $5/month free credit and auto-deploys from GitHub.

### Step 1: Create GitHub Repository
```bash
cd ~/Documents/leadscorer
git init
git add .
git commit -m "Initial commit - Lead Scorer API"
git remote add origin https://github.com/yourusername/leadscorer-api.git
git push -u origin main
```

### Step 2: Deploy on Railway

1. Go to https://railway.app/
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Choose your leadscorer-api repository
5. Railway will auto-detect the configuration from `railway.json`

### Step 3: Set Environment Variables

In the Railway dashboard:
1. Go to your project
2. Click "Variables"
3. Add:
   - `STORELEADS_API_KEY` = your_key_here
   - `COMPANYENRICH_API_KEY` = your_key_here
   - `API_RATE_LIMIT` = 5
   - `PORT` = 8001

Your API will be live at: `https://your-project.railway.app`

---

## Option 3: Render

Render offers a free tier with 750 hours/month.

### Step 1: Create GitHub Repository (if not done already)
```bash
cd ~/Documents/leadscorer
git init
git add .
git commit -m "Initial commit - Lead Scorer API"
git remote add origin https://github.com/yourusername/leadscorer-api.git
git push -u origin main
```

### Step 2: Deploy on Render

1. Go to https://render.com/
2. Click "New +" > "Web Service"
3. Connect your GitHub repository
4. Configure:
   - **Name**: leadscorer-api
   - **Environment**: Python 3
   - **Build Command**: `pip install -r api_requirements.txt`
   - **Start Command**: `uvicorn api_wrapper:app --host 0.0.0.0 --port $PORT`
   - **Plan**: Free

### Step 3: Set Environment Variables

In the Render dashboard:
1. Go to Environment
2. Add:
   - `STORELEADS_API_KEY` = your_key_here
   - `COMPANYENRICH_API_KEY` = your_key_here
   - `API_RATE_LIMIT` = 5

Your API will be live at: `https://leadscorer-api.onrender.com`

**Note:** Free tier spins down after 15 minutes of inactivity. First request after inactivity may be slow.

---

## Testing Your Deployed API

Once deployed, test with:

```bash
# Health check
curl https://your-api-url.com/health

# Score a domain
curl "https://your-api-url.com/score?domain=shopify.com"

# Get detailed score
curl "https://your-api-url.com/score/detailed?domain=shopify.com"
```

---

## Integration Examples

### Python Integration
```python
import requests

API_URL = "https://your-api-url.com"

def score_lead(domain):
    response = requests.get(f"{API_URL}/score?domain={domain}")
    if response.status_code == 200:
        data = response.json()
        return {
            'domain': data['domain'],
            'score': data['score'],
            'grade': data['grade'],
            'priority': data['priority']
        }
    return None

# Usage
result = score_lead("shopify.com")
print(f"Score: {result['score']}, Grade: {result['grade']}")
```

### JavaScript/Node.js Integration
```javascript
const API_URL = "https://your-api-url.com";

async function scoreLead(domain) {
  const response = await fetch(`${API_URL}/score?domain=${domain}`);
  if (response.ok) {
    const data = await response.json();
    return {
      domain: data.domain,
      score: data.score,
      grade: data.grade,
      priority: data.priority
    };
  }
  return null;
}

// Usage
scoreLead("shopify.com").then(result => {
  console.log(`Score: ${result.score}, Grade: ${result.grade}`);
});
```

### Google Sheets Integration (Apps Script)
```javascript
function SCORE_LEAD(domain) {
  const API_URL = "https://your-api-url.com";
  const url = `${API_URL}/score?domain=${domain}`;

  const response = UrlFetchApp.fetch(url);
  const data = JSON.parse(response.getContentText());

  return data.score;
}

// Usage in Google Sheets:
// =SCORE_LEAD(A2)  // where A2 contains the domain
```

---

## API Endpoints Reference

### GET /
Returns API information and available endpoints

### GET /health
Health check - verifies API and data sources are configured

### GET /score?domain={domain}
Returns basic scoring information:
- domain
- score (0-100)
- grade (A+ to F)
- priority (Very High, High, Medium, Low, Very Low)
- company_name
- industry
- revenue
- employees
- country
- data_source

### GET /score/detailed?domain={domain}
Returns complete scoring breakdown with all metrics and scoring contributions

---

## Monitoring & Logs

### Vercel
- View logs at: https://vercel.com/your-username/your-project/deployments
- Click on any deployment to see real-time logs

### Railway
- View logs in the Railway dashboard under "Deployments"
- Real-time logs available in the "Logs" tab

### Render
- View logs in the Render dashboard under "Logs"
- Real-time streaming available

---

## Cost Considerations

All platforms offer generous free tiers:

**Vercel:**
- Free: 100GB bandwidth/month
- Serverless execution time included
- Perfect for API use cases

**Railway:**
- $5/month free credit
- ~500 hours of usage
- Good for moderate traffic

**Render:**
- 750 hours/month free
- Spins down after 15min inactivity
- Good for occasional use

---

## Troubleshooting

### API returns 404 for all domains
- Check that environment variables are set correctly
- Verify API keys are valid
- Check logs for errors

### API is slow
- First request may be slow on free tiers (cold start)
- Consider upgrading to paid tier for production use
- Implement caching in your application

### Rate limit errors
- Adjust API_RATE_LIMIT environment variable
- Consider implementing request queuing in your application

---

## Security Best Practices

1. **Never commit API keys to Git**
   - Use `.env` file locally
   - Use platform environment variables in production

2. **Add API authentication** (optional)
   - Consider adding API key authentication for production use
   - Implement rate limiting per client

3. **Monitor usage**
   - Set up alerts for unusual traffic
   - Monitor API costs on your chosen platform

---

## Next Steps

1. Deploy to your chosen platform
2. Test the API endpoints
3. Integrate into your internal tools
4. Monitor usage and performance
5. Consider adding caching for frequently requested domains

For questions or issues, refer to the API_README.md file.
