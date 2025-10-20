# Deploy to Railway - Step by Step

Railway CLI is already installed! Follow these simple steps to deploy your API:

## Step 1: Login to Railway

Run this command in your terminal:

```bash
cd ~/Documents/leadscorer
railway login
```

This will open your browser to authenticate. Once done, come back to the terminal.

## Step 2: Initialize Railway Project

```bash
railway init
```

This will ask you to:
- Create a new project or link to existing one
- Give your project a name (e.g., "leadscorer-api")

## Step 3: Add Environment Variables

Add your API keys to Railway:

```bash
railway variables set STORELEADS_API_KEY=cd1dea52-b90e-43f9-57ca-124ee96c
railway variables set COMPANYENRICH_API_KEY=EcNCU9WhvsiqGOdsdwoFEG
railway variables set API_RATE_LIMIT=5
```

## Step 4: Deploy!

```bash
railway up
```

That's it! Railway will:
1. Detect it's a Python project
2. Install dependencies from `api_requirements.txt`
3. Start your API with uvicorn
4. Give you a public URL

## Step 5: Get Your URL

After deployment completes, get your public URL:

```bash
railway domain
```

This will show your API URL (e.g., `https://leadscorer-api-production.up.railway.app`)

## Testing Your Deployed API

Once deployed, test with:

```bash
# Replace with your Railway URL
API_URL="https://your-project.up.railway.app"

# Health check
curl "$API_URL/health"

# Score a domain
curl "$API_URL/score?domain=shopify.com"
```

## Quick Reference Commands

```bash
# View logs
railway logs

# Open dashboard
railway open

# Add more environment variables
railway variables set KEY=value

# Redeploy
railway up

# Check status
railway status
```

## What Railway Will Deploy

Railway will use these files:
- **api_wrapper.py** - Your FastAPI application
- **api_requirements.txt** - Python dependencies
- **app/** directory - Your scoring logic and API clients

Railway automatically detects:
- Python version
- Start command: `uvicorn api_wrapper:app --host 0.0.0.0 --port $PORT`
- Required packages from requirements.txt

## Costs

Railway offers:
- **$5/month free credit** for new accounts
- Enough for moderate API usage
- ~500 hours of usage per month

---

**Ready to deploy?** Just run:
```bash
cd ~/Documents/leadscorer
railway login
railway init
railway variables set STORELEADS_API_KEY=cd1dea52-b90e-43f9-57ca-124ee96c
railway variables set COMPANYENRICH_API_KEY=EcNCU9WhvsiqGOdsdwoFEG
railway up
```

Your API will be live in ~2 minutes! 🚀
