# Lead Scorer Application

A web-based lead scoring application that analyzes websites using the Store Leads API to prioritize potential customers based on company size and revenue metrics.

## Features

- **CSV Upload**: Process up to 5000 websites at once
- **Automated Scoring**: Uses Store Leads API data to calculate lead scores
- **Intelligent Prioritization**: Scores based on:
  - Yearly revenue (40% weight)
  - Company size/employees (30% weight)
  - Website traffic (15% weight)
  - Platform ranking (15% weight)
- **Grade System**: A+ to F grading for quick assessment
- **Priority Levels**: Very High, High, Medium, Low, Very Low
- **Beautiful Web Interface**: Easy-to-use drag-and-drop file upload
- **CSV Export**: Download results with detailed metrics

## Setup Instructions

1. **Install Dependencies**:
   ```bash
   cd lead-scorer
   pip install -r requirements.txt
   ```

2. **Configure API Key**:
   - The `.env` file has been created with your Store Leads API key
   - If you need to update it, edit the `.env` file

3. **Run the Application**:
   ```bash
   python run.py
   ```

4. **Access the Web Interface**:
   - Open your browser and go to: http://localhost:8000
   - The interface will load automatically

## How to Use

1. **Prepare Your CSV**:
   - Create a CSV file with a column containing website URLs
   - Column can be named: `website`, `domain`, or `url`
   - Example format included in `data/sample_websites.csv`

2. **Upload and Process**:
   - Click "Choose CSV File" to select your file
   - Click "Process Leads" to start scoring
   - Wait for processing (API rate limited to 5 requests/second)

3. **Review Results**:
   - View summary statistics on the web interface
   - See top 10 leads with scores and grades
   - Click "Download Results" to get the full CSV

## Output CSV Columns

- **domain**: The website domain
- **score**: Lead score (0-100)
- **grade**: Letter grade (A+ to F)
- **priority**: Priority level
- **yearly_revenue**: Estimated annual revenue
- **employee_count**: Number of employees
- **monthly_visits**: Estimated monthly website visits
- **platform_rank**: E-commerce platform ranking
- **rank_percentile**: Percentile ranking
- **product_count**: Number of products
- **monthly_app_spend**: Monthly app spending
- **platform**: E-commerce platform used
- **country**: Country code
- **Score breakdown**: Individual contribution of each factor

## API Rate Limits

- Default: 5 requests per second
- Can be adjusted in `.env` file (API_RATE_LIMIT)
- Processing 5000 websites takes approximately 17 minutes

## Project Structure

```
lead-scorer/
├── app/
│   ├── main.py              # FastAPI application
│   ├── storeleads_client.py # Store Leads API client
│   ├── lead_scorer.py       # Scoring algorithm
│   └── csv_processor.py     # CSV processing logic
├── data/                    # Input CSV files
├── output/                  # Generated result files
├── .env                     # API configuration
├── requirements.txt         # Python dependencies
└── run.py                   # Application launcher
```

## Scoring Algorithm

The scoring algorithm evaluates leads on multiple factors:

1. **Revenue Score (40%)**:
   - $10M+: Maximum points
   - $1M-$10M: High points
   - $100K-$1M: Medium points
   - Below $100K: Lower points

2. **Company Size (30%)**:
   - 100+ employees: Enterprise
   - 25-100: Mid-market
   - 10-25: Small business
   - 1-10: Micro business

3. **Traffic Score (15%)**:
   - Based on monthly website visits

4. **Rank Score (15%)**:
   - Platform ranking and percentile

## Troubleshooting

- **API Key Error**: Check that your `.env` file contains the correct API key
- **Rate Limit Issues**: Reduce API_RATE_LIMIT in `.env` if experiencing errors
- **CSV Format Issues**: Ensure your CSV has a header row with website URLs
- **Domain Not Found**: Some domains may not be in the Store Leads database

## Support

For issues with the Store Leads API, refer to: https://storeleads.app/api