# Railway + Vercel Deployment Guide

This guide will help you deploy your Lead Scorer application with:
- **Python Backend** on Railway (free tier available)
- **Next.js Frontend** on Vercel

## Part 1: Deploy Python Backend to Railway

### Prerequisites
- Railway account (sign up at https://railway.app)
- GitHub repository (already set up: https://github.com/ah2484/leadscorer)

### Steps to Deploy on Railway

1. **Login to Railway**
   - Go to https://railway.app
   - Sign in with GitHub

2. **Create New Project**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your repository: `ah2484/leadscorer`

3. **Configure Environment Variables**
   In Railway dashboard, add these variables:
   ```
   STORELEADS_API_KEY=your_storeleads_api_key
   COMPANYENRICH_API_KEY=your_companyenrich_api_key
   PORT=8000
   ```

4. **Deploy**
   - Railway will automatically detect the Procfile and start deployment
   - Once deployed, click on the deployment
   - Go to Settings → Domains
   - Click "Generate Domain" to get your API URL
   - Your backend will be available at something like: `https://lead-scorer-production.up.railway.app`

## Part 2: Create Next.js Frontend

Since the create-next-app command requires interactive input, please run this manually:

```bash
cd "/Users/adityaharipurkar/Documents/lead scorer"

# Create Next.js app
npx create-next-app@latest lead-scorer-frontend \
  --typescript \
  --tailwind \
  --app \
  --no-src-dir \
  --import-alias "@/*"

# When prompted:
# - ESLint: Yes
# - Turbopack: No (or Yes if you prefer)

cd lead-scorer-frontend
```

## Part 3: Setup Next.js Frontend Code

Once you've created the Next.js app, I'll provide you with:
1. The frontend components
2. API integration code
3. Environment configuration
4. Deployment instructions for Vercel

## Part 4: Important Files Already Created

Your Python backend is ready with:
- ✅ CORS configuration added to `app/main.py`
- ✅ Procfile for Railway deployment
- ✅ All Python dependencies in `requirements.txt`

## Quick Start Commands

### For Python Backend (Railway):
```bash
# Push to GitHub (already done)
git add .
git commit -m "Add Railway deployment configuration"
git push

# Then deploy via Railway dashboard
```

### For Next.js Frontend (after creation):
```bash
# Install dependencies
npm install axios

# Create .env.local
echo "NEXT_PUBLIC_API_URL=https://your-railway-url.railway.app" > .env.local

# Run locally
npm run dev

# Deploy to Vercel
npx vercel
```

## Architecture Overview

```
┌─────────────────┐         ┌─────────────────┐
│                 │         │                 │
│  Next.js App    │  ──────▶│  Python API     │
│  (Vercel)       │   HTTP  │  (Railway)      │
│                 │         │                 │
└─────────────────┘         └─────────────────┘
                                    │
                                    ▼
                            ┌───────────────┐
                            │               │
                            │  External APIs │
                            │  - StoreLeads │
                            │  - CompanyEnrich│
                            │               │
                            └───────────────┘
```

## Next Steps

1. **Deploy Python to Railway** (follow Part 1)
2. **Create Next.js app** (run the command in Part 2)
3. **Let me know when ready** and I'll provide the frontend code
4. **Deploy frontend to Vercel**

## Benefits of This Approach

- ✅ Full WebSocket support on Railway
- ✅ No timeout limitations
- ✅ Scalable architecture
- ✅ Free tiers available on both platforms
- ✅ Easy to maintain and update
- ✅ Production-ready setup

## Need Help?

Once you've:
1. Deployed the Python backend to Railway and have the URL
2. Created the Next.js app

Let me know and I'll provide the complete frontend code to connect everything together!