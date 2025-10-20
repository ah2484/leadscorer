# Railway Deployment - Configuration Guide

Your project is deployed! 🎉

**Project URL**: https://railway.com/project/ea7863ae-522d-45bd-a5d4-9f138aa6c140

## Step 1: Add Environment Variables

Go to your Railway project settings and add these environment variables:

1. Click on your project: https://railway.com/project/ea7863ae-522d-45bd-a5d4-9f138aa6c140
2. Click on the "Variables" tab
3. Add the following variables:

```
STORELEADS_API_KEY=cd1dea52-b90e-43f9-57ca-124ee96c
COMPANYENRICH_API_KEY=EcNCU9WhvsiqGOdsdwoFEG
API_RATE_LIMIT=5
```

## Step 2: Set Start Command

1. Go to "Settings" tab in your Railway project
2. Scroll to "Deploy" section
3. Set the **Start Command** to:
   ```
   uvicorn api_wrapper:app --host 0.0.0.0 --port $PORT
   ```

## Step 3: Generate a Domain

1. Go to "Settings" tab
2. Scroll to "Networking" section
3. Click "Generate Domain"
4. Railway will give you a public URL like: `https://your-project.up.railway.app`

## Step 4: Redeploy

After adding environment variables and setting the start command:

1. Go to "Deployments" tab
2. Click "Deploy" or wait for auto-deploy
3. Watch the build logs

## Step 5: Test Your API

Once deployed, test your API:

```bash
# Replace with your Railway domain
API_URL="https://your-project.up.railway.app"

# Health check
curl "$API_URL/health"

# Score a domain
curl "$API_URL/score?domain=shopify.com"
```

## Quick Links

- **Project Dashboard**: https://railway.com/project/ea7863ae-522d-45bd-a5d4-9f138aa6c140
- **Settings**: https://railway.com/project/ea7863ae-522d-45bd-a5d4-9f138aa6c140/settings
- **Deployments**: https://railway.com/project/ea7863ae-522d-45bd-a5d4-9f138aa6c140/deployments
- **Logs**: Click on any deployment to see logs

## What Files Railway Uses

Railway will automatically detect and use:
- `api_wrapper.py` - Your FastAPI app
- `api_requirements.txt` - Python dependencies
- `app/` directory - All your scoring logic

## Troubleshooting

### Build Fails
- Check that `api_requirements.txt` exists
- View build logs in deployments tab

### API Not Responding
- Verify environment variables are set
- Check start command is correct
- View runtime logs

### Import Errors
- Make sure all files from `app/` directory are included
- Check deployment logs for missing dependencies

## Monitor Your Deployment

1. **View Logs**: Click on deployment → View logs
2. **Check Metrics**: See CPU, memory, network usage
3. **Monitor Costs**: Railway shows usage in dashboard

## Your API Endpoints

Once deployed, your API will have:

- `GET /` - API information
- `GET /health` - Health check
- `GET /score?domain={domain}` - Score a domain
- `GET /score/detailed?domain={domain}` - Detailed scoring

## Next Steps

1. ✅ Add environment variables
2. ✅ Set start command
3. ✅ Generate domain
4. ✅ Test API endpoints
5. ✅ Update your internal tools with new URL

---

**Need help?** Check the Railway logs or the project dashboard.
