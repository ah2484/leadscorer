# Deployment Instructions

## Vercel Deployment (Simplified Version)

### Prerequisites
- Vercel account (sign up at https://vercel.com)
- Git repository (GitHub, GitLab, or Bitbucket)
- API keys for StoreLeads and CompanyEnrich

### Important Note
⚠️ **Vercel Limitations**: Vercel's serverless functions don't support WebSockets, so the deployed version uses polling for progress updates instead of real-time WebSocket connections. For full functionality with real-time updates, consider using Railway or Render (instructions below).

### Step 1: Prepare Environment Variables

Create a `.env` file in your project root (don't commit this to git):

```env
STORELEADS_API_KEY=your_storeleads_api_key_here
COMPANYENRICH_API_KEY=your_companyenrich_api_key_here
```

### Step 2: Deploy to Vercel

#### Option A: Deploy via GitHub (Recommended)

1. Push your code to GitHub:
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin YOUR_GITHUB_REPO_URL
git push -u origin main
```

2. Go to [Vercel Dashboard](https://vercel.com/dashboard)
3. Click "Add New Project"
4. Import your GitHub repository
5. Configure build settings:
   - Framework Preset: Other
   - Build Command: (leave empty)
   - Output Directory: (leave empty)
6. Add environment variables:
   - Click "Environment Variables"
   - Add `STORELEADS_API_KEY` and `COMPANYENRICH_API_KEY`
7. Click "Deploy"

#### Option B: Deploy via CLI

1. Login to Vercel:
```bash
npx vercel login
```

2. Deploy:
```bash
npx vercel
```

3. Follow the prompts:
   - Link to existing project? No
   - What's your project's name? lead-scorer
   - In which directory is your code located? ./
   - Want to override the settings? No

4. Add environment variables:
```bash
npx vercel env add STORELEADS_API_KEY
npx vercel env add COMPANYENRICH_API_KEY
```

5. Deploy to production:
```bash
npx vercel --prod
```

### Step 3: Access Your Application

Your application will be available at:
- Development: `https://your-project.vercel.app`
- Production: `https://your-custom-domain.com` (if configured)

## Alternative Deployment Options (Full WebSocket Support)

### Railway Deployment (Recommended for Full Features)

Railway supports WebSockets and is ideal for this application.

1. Install Railway CLI:
```bash
npm install -g @railway/cli
```

2. Login and initialize:
```bash
railway login
railway init
```

3. Add environment variables:
```bash
railway variables set STORELEADS_API_KEY=your_key
railway variables set COMPANYENRICH_API_KEY=your_key
```

4. Deploy:
```bash
railway up
```

5. Generate domain:
```bash
railway domain
```

### Render Deployment

1. Create a `render.yaml` file:
```yaml
services:
  - type: web
    name: lead-scorer
    runtime: python
    buildCommand: pip install -r requirements.txt
    startCommand: python run.py
    envVars:
      - key: STORELEADS_API_KEY
        sync: false
      - key: COMPANYENRICH_API_KEY
        sync: false
```

2. Connect to GitHub and deploy via Render Dashboard

### AWS EC2/ECS Deployment

For production workloads with high traffic:

1. Create a `Dockerfile`:
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "run.py"]
```

2. Build and push to ECR:
```bash
docker build -t lead-scorer .
docker tag lead-scorer:latest YOUR_ECR_URI/lead-scorer:latest
docker push YOUR_ECR_URI/lead-scorer:latest
```

3. Deploy using ECS or EC2 with proper load balancing

## Local Development

To run locally with full features:

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export STORELEADS_API_KEY=your_key
export COMPANYENRICH_API_KEY=your_key

# Run the application
python run.py
```

Access at: http://localhost:8000

## Environment Variables

Required environment variables for all deployments:

| Variable | Description | Required |
|----------|-------------|----------|
| `STORELEADS_API_KEY` | StoreLeads API key for fetching e-commerce data | Yes |
| `COMPANYENRICH_API_KEY` | CompanyEnrich API key for B2B company data | Yes |
| `MAX_DOMAINS` | Maximum domains to process (default: 2000) | No |
| `PORT` | Port to run the server (default: 8000) | No |

## Monitoring and Logs

### Vercel
- View logs: `npx vercel logs`
- Monitor function usage in Vercel Dashboard

### Railway
- View logs: `railway logs`
- Monitor in Railway Dashboard

### Render
- View logs in Render Dashboard
- Set up health checks for monitoring

## Troubleshooting

### Common Issues

1. **"Module not found" errors**
   - Ensure all dependencies are in `requirements.txt`
   - Check Python version compatibility (3.9+)

2. **API rate limits**
   - CompanyEnrich API has rate limits
   - Consider implementing caching or queuing

3. **Large file processing timeouts**
   - Vercel has 60-second function timeout
   - For large batches, use Railway or Render

4. **WebSocket connection fails**
   - Expected on Vercel (uses polling instead)
   - Deploy to Railway/Render for WebSocket support

## Support

For issues or questions:
1. Check the application logs
2. Verify API keys are correct
3. Ensure domain limits are not exceeded
4. Check API service status

## Security Notes

- Never commit `.env` files to version control
- Rotate API keys regularly
- Use environment-specific keys (dev/staging/prod)
- Enable CORS only for your domain in production