# Lead Scorer API

A simple REST API wrapper for the Lead Scorer application. Input a domain URL and get back the lead score, grade, and priority.

## API Endpoints

### `GET /`
Root endpoint with API information.

**Response:**
```json
{
  "message": "Lead Scorer API",
  "version": "1.0.0",
  "endpoints": {
    "/score": "GET - Score a single domain",
    "/health": "GET - Health check"
  }
}
```

### `GET /health`
Health check endpoint to verify API and data source configuration.

**Response:**
```json
{
  "status": "healthy",
  "storeleads_api": "configured",
  "companyenrich_api": "configured"
}
```

### `GET /score?domain={domain}`
Score a single domain and return basic metrics.

**Parameters:**
- `domain` (required): Domain URL to score (e.g., `example.com` or `https://example.com`)

**Response:**
```json
{
  "domain": "example.com",
  "score": 85.5,
  "grade": "A",
  "priority": "Very High",
  "company_name": "Example Company",
  "industry": "Technology",
  "revenue": "10m-50m",
  "employees": "100-250",
  "country": "United States",
  "data_source": "CompanyEnrich"
}
```

### `GET /score/detailed?domain={domain}`
Score a domain and return detailed scoring breakdown with all available metrics.

**Parameters:**
- `domain` (required): Domain URL to score

**Response:**
```json
{
  "domain": "example.com",
  "score": 85.5,
  "grade": "A",
  "priority": "Very High",
  "metrics": {
    "name": "Example Company",
    "yearly_revenue": 30000000,
    "employee_count": 175,
    "industry": "Technology",
    "country": "United States",
    ...
  },
  "breakdown": {
    "revenue_contribution": 34.2,
    "size_contribution": 25.5,
    "traffic_contribution": 12.8,
    "rank_contribution": 13.0
  }
}
```

## Running Locally

### 1. Install Dependencies
```bash
cd leadscorer
pip install -r api_requirements.txt
```

### 2. Configure Environment Variables
Create a `.env` file with your API keys:
```bash
STORELEADS_API_KEY=your_storeleads_key
COMPANYENRICH_API_KEY=your_companyenrich_key
API_RATE_LIMIT=5
```

### 3. Start the API
```bash
# Option 1: Using the start script
./start_api.sh

# Option 2: Using uvicorn directly
uvicorn api_wrapper:app --reload --port 8001
```

The API will be available at `http://localhost:8001`

### 4. Test the API
```bash
# Basic health check
curl http://localhost:8001/health

# Score a domain
curl "http://localhost:8001/score?domain=shopify.com"

# Get detailed score
curl "http://localhost:8001/score/detailed?domain=shopify.com"
```

## Deployment Options

### Option 1: Vercel (Recommended for Serverless)

1. Install Vercel CLI:
```bash
npm install -g vercel
```

2. Deploy:
```bash
vercel --prod
```

3. Add environment variables in Vercel dashboard:
   - `STORELEADS_API_KEY`
   - `COMPANYENRICH_API_KEY`
   - `API_RATE_LIMIT`

**Configuration file:** `vercel_api.json`

### Option 2: Railway

1. Connect your GitHub repository to Railway
2. Set environment variables in Railway dashboard:
   - `STORELEADS_API_KEY`
   - `COMPANYENRICH_API_KEY`
   - `API_RATE_LIMIT`
3. Railway will auto-deploy using `railway.json` configuration

**Configuration file:** `railway.json`

### Option 3: Render

1. Create a new Web Service on Render
2. Connect your repository
3. Set build command: `pip install -r api_requirements.txt`
4. Set start command: `uvicorn api_wrapper:app --host 0.0.0.0 --port $PORT`
5. Add environment variables

## How It Works

The API uses two data sources:

1. **StoreLeads API** - Primary source for e-commerce companies
2. **CompanyEnrich API** - Fallback for B2B/enterprise companies

When you request a score:
1. API tries StoreLeads first
2. If not found, falls back to CompanyEnrich
3. Scores the lead using a weighted algorithm:
   - Revenue (40%)
   - Company size (30%)
   - Website traffic (15%)
   - Platform ranking (15%)
   - Funding bonus (5% for B2B)

## Scoring System

**Grades:**
- A+ (90-100): Exceptional lead
- A (80-89): High-value lead
- B+ (70-79): Good lead
- B (60-69): Above average lead
- C+ (50-59): Average lead
- C (40-49): Below average lead
- D (30-39): Low-value lead
- F (0-29): Very low value lead

**Priority Levels:**
- Very High (80-100)
- High (60-79)
- Medium (40-59)
- Low (20-39)
- Very Low (0-19)

## Example Usage

### Python
```python
import requests

response = requests.get("http://localhost:8001/score?domain=shopify.com")
data = response.json()
print(f"Score: {data['score']}, Grade: {data['grade']}, Priority: {data['priority']}")
```

### JavaScript
```javascript
fetch('http://localhost:8001/score?domain=shopify.com')
  .then(response => response.json())
  .then(data => {
    console.log(`Score: ${data.score}, Grade: ${data.grade}, Priority: ${data.priority}`);
  });
```

### cURL
```bash
curl "http://localhost:8001/score?domain=shopify.com" | jq
```

## API Documentation

Once the API is running, visit:
- Swagger UI: `http://localhost:8001/docs`
- ReDoc: `http://localhost:8001/redoc`

## Rate Limits

The API respects rate limits from the underlying data sources:
- Default: 5 requests per second
- Configurable via `API_RATE_LIMIT` environment variable

## Error Handling

The API returns standard HTTP status codes:
- `200` - Success
- `400` - Bad request (missing domain parameter)
- `404` - Domain not found in any database
- `500` - Server error

Error response format:
```json
{
  "detail": "Error message here"
}
```

## Support

For issues or questions, check the main README.md or create an issue in the repository.
