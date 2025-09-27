from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
import asyncio
import os
import json
from datetime import datetime
import shutil
import uuid
import traceback

from .csv_processor import CSVProcessor
from .progress_tracker import progress_tracker
from .api_routes import router as api_router

app = FastAPI(title="Lead Scorer", version="1.0.1")

# Add CORS middleware for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Local Next.js development
        "https://*.vercel.app",   # Vercel deployments
        "*"  # Allow all origins (configure more strictly in production)
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the API routes
app.include_router(api_router)

processor = CSVProcessor()

class ProcessingStatus(BaseModel):
    status: str
    message: str
    result_file: Optional[str] = None
    summary: Optional[Dict] = None

processing_status = {}
active_websockets: Dict[str, WebSocket] = {}

@app.get("/", response_class=HTMLResponse)
async def root():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Lead Scorer</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                max-width: 1200px;
                margin: 0 auto;
                padding: 40px 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
            }
            .container {
                background: white;
                border-radius: 20px;
                padding: 40px;
                box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            }
            h1 {
                color: #333;
                margin-bottom: 10px;
            }
            .subtitle {
                color: #666;
                margin-bottom: 30px;
            }
            .input-tabs {
                display: flex;
                gap: 10px;
                margin: 20px 0;
                border-bottom: 2px solid #e2e8f0;
            }
            .tab-button {
                padding: 10px 20px;
                background: none;
                border: none;
                color: #718096;
                cursor: pointer;
                font-size: 16px;
                font-weight: 500;
                position: relative;
                transition: all 0.3s;
            }
            .tab-button.active {
                color: #667eea;
            }
            .tab-button.active::after {
                content: '';
                position: absolute;
                bottom: -2px;
                left: 0;
                right: 0;
                height: 2px;
                background: #667eea;
            }
            .tab-content {
                display: none;
                margin: 20px 0;
            }
            .tab-content.active {
                display: block;
            }
            .upload-area {
                border: 2px dashed #ddd;
                border-radius: 10px;
                padding: 40px;
                text-align: center;
                margin-bottom: 30px;
                transition: all 0.3s;
                background: #fafafa;
            }
            .upload-area:hover {
                border-color: #667eea;
                background: #f5f5ff;
            }
            .text-input-area {
                background: white;
                border: 2px solid #cbd5e0;
                border-radius: 10px;
                padding: 20px;
            }
            .domain-textarea {
                width: 100%;
                min-height: 200px;
                padding: 15px;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                font-size: 14px;
                resize: vertical;
            }
            .domain-textarea:focus {
                outline: none;
                border-color: #667eea;
                box-shadow: 0 0 0 3px rgba(102,126,234,0.1);
            }
            .input-info {
                margin-top: 10px;
                font-size: 14px;
                color: #718096;
            }
            .domain-count {
                margin-top: 10px;
                font-size: 14px;
                color: #667eea;
                font-weight: 500;
            }
            input[type="file"] {
                display: none;
            }
            .upload-label {
                display: inline-block;
                padding: 12px 30px;
                background: #667eea;
                color: white;
                border-radius: 8px;
                cursor: pointer;
                transition: all 0.3s;
                font-weight: 500;
            }
            .upload-label:hover {
                background: #764ba2;
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(118,75,162,0.3);
            }
            .button {
                padding: 12px 30px;
                background: #48bb78;
                color: white;
                border: none;
                border-radius: 8px;
                cursor: pointer;
                font-size: 16px;
                font-weight: 500;
                transition: all 0.3s;
                margin-right: 10px;
            }
            .button:hover {
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(72,187,120,0.3);
            }
            .button:disabled {
                background: #cbd5e0;
                cursor: not-allowed;
                transform: none;
            }
            #status {
                margin-top: 30px;
                padding: 20px;
                border-radius: 10px;
                background: #f7fafc;
                min-height: 100px;
            }
            .success {
                background: #c6f6d5 !important;
                color: #22543d;
            }
            .error {
                background: #fed7d7 !important;
                color: #742a2a;
            }
            .processing {
                background: #feebc8 !important;
                color: #744210;
            }
            .summary-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                margin: 20px 0;
            }
            .summary-card {
                background: white;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            }
            .summary-card h3 {
                margin: 0 0 10px 0;
                color: #667eea;
                font-size: 14px;
                text-transform: uppercase;
                letter-spacing: 1px;
            }
            .summary-card .value {
                font-size: 28px;
                font-weight: bold;
                color: #333;
            }
            table {
                width: 100%;
                border-collapse: collapse;
                margin-top: 20px;
            }
            th {
                background: #667eea;
                color: white;
                padding: 12px;
                text-align: left;
            }
            td {
                padding: 10px;
                border-bottom: 1px solid #e2e8f0;
            }
            tr:hover {
                background: #f7fafc;
            }
            .grade {
                display: inline-block;
                padding: 4px 8px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 12px;
            }
            .grade-A { background: #c6f6d5; color: #22543d; }
            .grade-B { background: #bee3f8; color: #2c5282; }
            .grade-C { background: #feebc8; color: #744210; }
            .grade-D { background: #fed7d7; color: #742a2a; }
            .grade-F { background: #e2e8f0; color: #4a5568; }
            .priority-very-high { color: #d53f8c; font-weight: bold; }
            .priority-high { color: #dd6b20; font-weight: bold; }
            .priority-medium { color: #d69e2e; }
            .priority-low { color: #38a169; }
            .priority-very-low { color: #718096; }

            /* Progress bar styles */
            .progress-container {
                display: none;
                margin: 30px 0;
                padding: 20px;
                background: #f7fafc;
                border-radius: 10px;
                border: 1px solid #e2e8f0;
            }
            .progress-container.active {
                display: block;
            }
            .progress-bar-wrapper {
                background: #e2e8f0;
                border-radius: 10px;
                overflow: hidden;
                height: 30px;
                position: relative;
                margin: 15px 0;
            }
            .progress-bar {
                height: 100%;
                background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
                transition: width 0.3s ease;
                display: flex;
                align-items: center;
                justify-content: center;
                color: white;
                font-weight: bold;
                font-size: 14px;
            }
            .progress-info {
                display: flex;
                justify-content: space-between;
                margin: 10px 0;
                color: #4a5568;
                font-size: 14px;
            }
            .progress-message {
                color: #667eea;
                font-weight: 500;
                margin-top: 10px;
            }
            .error-container {
                display: none;
                margin: 20px 0;
                padding: 15px;
                background: #fed7d7;
                border: 1px solid #fc8181;
                border-radius: 8px;
                color: #742a2a;
            }
            .error-container.active {
                display: block;
            }
            .error-title {
                font-weight: bold;
                margin-bottom: 10px;
            }
            .error-details {
                font-family: monospace;
                font-size: 12px;
                background: white;
                padding: 10px;
                border-radius: 4px;
                margin-top: 10px;
                max-height: 200px;
                overflow-y: auto;
            }
            .spinner {
                display: inline-block;
                width: 20px;
                height: 20px;
                border: 3px solid #f3f3f3;
                border-top: 3px solid #667eea;
                border-radius: 50%;
                animation: spin 1s linear infinite;
                margin-left: 10px;
            }
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Lead Scorer</h1>
            <p class="subtitle">Add website URLs to get lead scores (Max 500 domains)</p>

            <!-- Input Method Tabs -->
            <div class="input-tabs">
                <button class="tab-button active" onclick="switchTab('paste')">Paste Domains</button>
                <button class="tab-button" onclick="switchTab('upload')">Upload CSV</button>
            </div>

            <!-- Paste Domains Tab -->
            <div id="paste-tab" class="tab-content active">
                <div class="text-input-area">
                    <textarea id="domain-input" class="domain-textarea"
                        placeholder="Paste your domains here (one per line)&#10;&#10;Examples:&#10;example.com&#10;https://www.example.com&#10;www.example.com"
                        oninput="updateDomainCount()" onpaste="setTimeout(updateDomainCount, 100)"></textarea>
                    <div class="input-info">
                        Enter one domain per line. Supports formats: domain.com, www.domain.com, https://domain.com
                    </div>
                    <div id="domain-count" class="domain-count">0 domains</div>
                </div>
            </div>

            <!-- Upload CSV Tab -->
            <div id="upload-tab" class="tab-content">
                <div class="upload-area">
                    <label for="file-upload" class="upload-label">
                        Choose CSV File
                    </label>
                    <input id="file-upload" type="file" accept=".csv" onchange="handleFileSelect(event)">
                    <p id="file-name" style="margin-top: 20px; color: #666;">No file selected</p>
                </div>
            </div>

            <button class="button" onclick="processInput()" id="process-btn" disabled>Process Leads</button>
            <button class="button" onclick="downloadResults()" id="download-btn" style="display:none; background: #667eea;">Download Results</button>

            <!-- Progress Bar -->
            <div id="progress-container" class="progress-container">
                <h3>Processing Progress<span class="spinner"></span></h3>
                <div class="progress-bar-wrapper">
                    <div id="progress-bar" class="progress-bar" style="width: 0%">0%</div>
                </div>
                <div class="progress-info">
                    <span id="progress-current">0 / 0 items</span>
                    <span id="progress-time">Elapsed: 0s | Remaining: calculating...</span>
                </div>
                <div id="api-progress" style="margin-top: 15px; font-size: 14px;">
                    <div id="storeleads-progress" style="margin: 5px 0;">🔍 Store Leads API: <span id="storeleads-status">Pending</span></div>
                    <div id="companyenrich-progress" style="margin: 5px 0;">🏢 Company Enrich API: <span id="companyenrich-status">Pending</span></div>
                    <div id="scoring-progress" style="margin: 5px 0;">📊 Lead Scoring: <span id="scoring-status">Pending</span></div>
                </div>
                <div id="progress-message" class="progress-message">Initializing...</div>
            </div>

            <!-- Error Container -->
            <div id="error-container" class="error-container">
                <div class="error-title">Processing Errors Detected</div>
                <div id="error-list"></div>
                <details>
                    <summary style="cursor: pointer; margin-top: 10px;">Show Technical Details</summary>
                    <div id="error-details" class="error-details"></div>
                </details>
            </div>

            <div id="status"></div>
        </div>

        <script>
            let selectedFile = null;
            let resultFile = null;
            let websocket = null;
            let sessionId = null;
            let activeTab = 'paste';

            function switchTab(tab) {
                activeTab = tab;

                // Update tab buttons
                document.querySelectorAll('.tab-button').forEach(btn => btn.classList.remove('active'));
                event.target.classList.add('active');

                // Update tab content
                document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
                document.getElementById(tab + '-tab').classList.add('active');

                // Update process button state
                updateProcessButton();
            }

            function updateDomainCount() {
                const textarea = document.getElementById('domain-input');
                const domains = textarea.value.split('\\n').filter(line => line.trim().length > 0);
                const count = domains.length;

                document.getElementById('domain-count').textContent = count + ' domain' + (count !== 1 ? 's' : '');

                if (count > 4000) {
                    document.getElementById('domain-count').textContent += ' (Only first 4000 will be processed)';
                    document.getElementById('domain-count').style.color = '#fc8181';
                } else {
                    document.getElementById('domain-count').style.color = '#667eea';
                }

                updateProcessButton();
            }

            function updateProcessButton() {
                const processBtn = document.getElementById('process-btn');

                if (activeTab === 'paste') {
                    const textarea = document.getElementById('domain-input');
                    const domains = textarea.value.split('\\n').filter(line => line.trim().length > 0);
                    processBtn.disabled = domains.length === 0;
                } else {
                    processBtn.disabled = !selectedFile;
                }
            }

            function handleFileSelect(event) {
                selectedFile = event.target.files[0];
                if (selectedFile) {
                    document.getElementById('file-name').textContent = 'Selected: ' + selectedFile.name;
                    updateProcessButton();
                }
            }

            function updateProgress(data) {
                const progressContainer = document.getElementById('progress-container');
                const progressBar = document.getElementById('progress-bar');
                const progressCurrent = document.getElementById('progress-current');
                const progressTime = document.getElementById('progress-time');
                const progressMessage = document.getElementById('progress-message');
                const errorContainer = document.getElementById('error-container');
                const errorList = document.getElementById('error-list');

                progressContainer.classList.add('active');

                // Update progress bar
                const percentage = data.percentage || 0;
                progressBar.style.width = percentage + '%';
                progressBar.textContent = percentage.toFixed(1) + '%';

                // Update overall count
                const totalItems = data.api_progress?.storeleads?.total || data.total || 0;
                progressCurrent.textContent = 'Processing ' + totalItems + ' domains';

                // Update API-specific progress
                if (data.api_progress) {
                    const storeleads = data.api_progress.storeleads;
                    const companyenrich = data.api_progress.companyenrich;
                    const scoring = data.api_progress.scoring;

                    document.getElementById('storeleads-status').textContent =
                        storeleads.current + '/' + storeleads.total + ' (' + ((storeleads.current/Math.max(storeleads.total,1))*100).toFixed(0) + '%)';

                    // Handle Company Enrich display - always show progress if available
                    if (companyenrich && (companyenrich.total > 0 || companyenrich.current > 0)) {
                        // Company Enrich has data - show actual progress
                        const ceTotal = companyenrich.total || 0;
                        const ceCurrent = companyenrich.current || 0;
                        const cePercent = ceTotal > 0 ? ((ceCurrent/ceTotal)*100).toFixed(0) : '0';
                        document.getElementById('companyenrich-status').textContent =
                            ceCurrent + '/' + ceTotal + ' (' + cePercent + '%)';
                    } else if (data.stage === 'companyenrich') {
                        // We're in Company Enrich stage but no data yet
                        document.getElementById('companyenrich-status').textContent = 'Initializing...';
                    } else if (storeleads.current === storeleads.total && storeleads.total > 0 && scoring.current === 0) {
                        // Store Leads completed, scoring hasn't started - likely checking for Company Enrich
                        document.getElementById('companyenrich-status').textContent = 'Checking for domains needing enrichment...';
                    } else if (scoring.current > 0 || data.stage === 'scoring') {
                        // Scoring has started, Company Enrich is done
                        document.getElementById('companyenrich-status').textContent =
                            companyenrich && companyenrich.current > 0 ?
                            companyenrich.current + '/' + (companyenrich.total || companyenrich.current) + ' (completed)' :
                            'Not needed';
                    } else {
                        document.getElementById('companyenrich-status').textContent = 'Pending';
                    }

                    document.getElementById('scoring-status').textContent =
                        scoring.current + '/' + scoring.total + ' (' + ((scoring.current/Math.max(scoring.total,1))*100).toFixed(0) + '%)';
                }

                // Update time
                const elapsed = data.elapsed_time || 0;
                const remaining = data.estimated_remaining || 0;
                progressTime.textContent = 'Elapsed: ' + elapsed.toFixed(0) + 's | Remaining: ' + (remaining > 0 ? remaining.toFixed(0) + 's' : 'calculating...');

                // Update message
                progressMessage.textContent = data.message || 'Processing...';

                // Show errors if any
                if (data.errors && data.errors.length > 0) {
                    errorContainer.classList.add('active');
                    const errorHtml = data.errors.map(err =>
                        '<div style="margin: 5px 0;">• ' + err.error + '</div>'
                    ).join('');
                    errorList.innerHTML = errorHtml;
                }

                // Handle completion
                if (data.completed) {
                    progressBar.style.background = data.success ?
                        'linear-gradient(90deg, #48bb78 0%, #38a169 100%)' :
                        'linear-gradient(90deg, #fc8181 0%, #f56565 100%)';

                    // Hide progress bar after a short delay
                    setTimeout(() => {
                        progressContainer.classList.remove('active');
                    }, 2000);

                    if (websocket) {
                        websocket.close();
                        websocket = null;
                    }
                }
            }

            async function processInput() {
                const formData = new FormData();

                if (activeTab === 'paste') {
                    // Create CSV from pasted domains
                    const textarea = document.getElementById('domain-input');
                    const domains = textarea.value.split('\\n')
                        .filter(line => line.trim().length > 0)
                        .map(line => {
                            // Clean up the domain: remove quotes, extra spaces, special characters
                            let cleaned = line.trim();

                            // Remove all types of quotes and backticks
                            cleaned = cleaned.replace(/["'`]/g, '');

                            // If line contains delimiters, take first part
                            if (cleaned.includes(',')) {
                                cleaned = cleaned.split(',')[0].trim();
                            } else if (cleaned.includes('\\t')) {
                                cleaned = cleaned.split('\\t')[0].trim();
                            } else if (cleaned.includes('|')) {
                                cleaned = cleaned.split('|')[0].trim();
                            } else if (cleaned.includes(' ')) {
                                // Take first word if there are spaces
                                cleaned = cleaned.split(' ')[0].trim();
                            }

                            // Remove protocol if present (http://, https://, etc.)
                            cleaned = cleaned.replace(/^https?:\\/\\//i, '');
                            cleaned = cleaned.replace(/^www\\./i, '');

                            // Remove trailing slashes and paths
                            if (cleaned.includes('/')) {
                                cleaned = cleaned.split('/')[0];
                            }

                            // Remove any control characters
                            cleaned = cleaned.replace(/[\\x00-\\x1F\\x7F]/g, '');

                            return cleaned.trim();
                        })
                        .filter(domain => domain.length > 0);

                    if (domains.length === 0) return;

                    // Create CSV content with just the domains, one per line
                    const csvContent = 'website\\n' + domains.join('\\n');
                    const blob = new Blob([csvContent], { type: 'text/csv' });
                    const file = new File([blob], 'domains.csv', { type: 'text/csv' });
                    formData.append('file', file);
                } else {
                    if (!selectedFile) return;
                    formData.append('file', selectedFile);
                }

                const statusDiv = document.getElementById('status');
                const processBtn = document.getElementById('process-btn');
                const downloadBtn = document.getElementById('download-btn');
                const progressContainer = document.getElementById('progress-container');
                const errorContainer = document.getElementById('error-container');
                const errorDetails = document.getElementById('error-details');

                processBtn.disabled = true;
                downloadBtn.style.display = 'none';
                statusDiv.innerHTML = '';
                progressContainer.classList.add('active');
                errorContainer.classList.remove('active');

                try {
                    const response = await fetch('/process', {
                        method: 'POST',
                        body: formData
                    });

                    const data = await response.json();

                    if (response.ok && data.status === 'processing') {
                        sessionId = data.session_id;

                        // Connect WebSocket immediately for real-time updates
                        if (sessionId) {
                            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
                            const wsUrl = protocol + '//' + window.location.host + '/ws/' + sessionId;
                            websocket = new WebSocket(wsUrl);

                            websocket.onmessage = (event) => {
                                const progressData = JSON.parse(event.data);
                                updateProgress(progressData);

                                // Handle completion with results
                                if (progressData.completed && progressData.success) {
                                    resultFile = progressData.result_file;
                                    if (resultFile) {
                                        downloadBtn.style.display = 'inline-block';
                                    }

                                    statusDiv.className = 'success';
                                    let html = '<h3>Processing Complete!</h3>';

                                    if (progressData.summary) {
                                        const summary = progressData.summary;
                                        html += '<div class="summary-grid">';
                                        html += '<div class="summary-card">' +
                                            '<h3>Total Leads</h3>' +
                                            '<div class="value">' + summary.total_leads + '</div>' +
                            '</div>';
                                        html += '<div class="summary-card">' +
                                            '<h3>Average Score</h3>' +
                                            '<div class="value">' + summary.average_score.toFixed(1) + '</div>' +
                            '</div>';

                                        const veryHighAndHigh = (summary.priority_distribution['Very High'] || 0) +
                                                                (summary.priority_distribution['High'] || 0);
                                        html += '<div class="summary-card">' +
                                            '<h3>High Priority</h3>' +
                                            '<div class="value">' + veryHighAndHigh + '</div>' +
                            '</div>';

                                        const aPlus = (summary.score_distribution['A+'] || 0) +
                                                      (summary.score_distribution['A'] || 0);
                                        html += '<div class="summary-card">' +
                                            '<h3>A-Grade Leads</h3>' +
                                            '<div class="value">' + aPlus + '</div>' +
                            '</div>';
                                        html += '</div>';

                                        if (summary.top_10_leads && summary.top_10_leads.length > 0) {
                                            html += '<h3>Top 10 Leads</h3>';
                                            html += '<table>';
                                            html += '<thead><tr><th>Domain</th><th>Score</th><th>Grade</th><th>Priority</th><th>Yearly Revenue</th><th>Employees</th></tr></thead>';
                                            html += '<tbody>';
                                            for (const lead of summary.top_10_leads) {
                                    const gradeClass = 'grade-' + lead.grade.replace('+', '');
                                    const priorityClass = 'priority-' + lead.priority.toLowerCase().replace(' ', '-');
                                                html += '<tr>' +
                                        '<td><strong>' + lead.domain + '</strong></td>' +
                                        '<td>' + lead.score.toFixed(1) + '</td>' +
                                        '<td><span class="grade ' + gradeClass + '">' + lead.grade + '</span></td>' +
                                        '<td><span class="' + priorityClass + '">' + lead.priority + '</span></td>' +
                                        '<td>$' + lead.yearly_revenue.toLocaleString() + '</td>' +
                                        '<td>' + lead.employee_count + '</td>' +
                                    '</tr>';
                                            }
                                            html += '</tbody></table>';
                                        }
                                    }

                                    statusDiv.innerHTML = html;
                                }
                            };

                            websocket.onerror = (error) => {
                                console.error('WebSocket error:', error);
                            };

                            websocket.onclose = () => {
                                console.log('WebSocket connection closed');
                            };
                        }
                    } else if (!response.ok) {
                        // Handle error response
                        const errorData = data.detail || data;
                        const errorMessage = typeof errorData === 'object' ? errorData.error : errorData;
                        const traceback = typeof errorData === 'object' ? errorData.traceback : '';

                        const errorContainer = document.getElementById('error-container');
                        const errorList = document.getElementById('error-list');
                        const errorDetails = document.getElementById('error-details');

                        errorContainer.classList.add('active');
                        errorList.innerHTML = '<div>• ' + errorMessage + '</div>';

                        if (traceback) {
                            errorDetails.textContent = traceback;
                        }

                        // Try to connect WebSocket even on error for partial results
                        if (typeof errorData === 'object' && errorData.session_id) {
                            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
                            const wsUrl = protocol + '//' + window.location.host + '/ws/' + errorData.session_id;
                            websocket = new WebSocket(wsUrl);

                            websocket.onmessage = (event) => {
                                const progressData = JSON.parse(event.data);
                                updateProgress(progressData);
                            };
                        }

                        throw new Error(errorMessage);
                    }
                } catch (error) {
                    statusDiv.className = 'error';
                    statusDiv.innerHTML = '<h3>Error</h3><p>' + error.message + '</p>';
                    progressContainer.classList.remove('active');
                } finally {
                    processBtn.disabled = false;
                }
            }

            function downloadResults() {
                if (resultFile) {
                    window.open('/download/' + resultFile, '_blank');
                }
            }

            // Initialize on load
            window.addEventListener('DOMContentLoaded', function() {
                updateDomainCount();
                // Also check on focus/click to catch any missed updates
                document.getElementById('domain-input').addEventListener('focus', updateDomainCount);
                document.getElementById('domain-input').addEventListener('click', updateDomainCount);
            });
        </script>
    </body>
    </html>
    """

@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    await websocket.accept()
    active_websockets[session_id] = websocket

    try:
        while True:
            # Keep connection alive and send progress updates
            await asyncio.sleep(0.5)
            progress = progress_tracker.get_progress(session_id)
            if progress:
                await websocket.send_json(progress)
                if progress.get('completed'):
                    break
    except WebSocketDisconnect:
        pass
    finally:
        if session_id in active_websockets:
            del active_websockets[session_id]

@app.post("/process")
async def process_csv(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="File must be a CSV")

    session_id = str(uuid.uuid4())
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    temp_input_path = f"data/temp_input_{timestamp}.csv"

    os.makedirs("data", exist_ok=True)
    os.makedirs("output", exist_ok=True)

    try:
        with open(temp_input_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        websites = processor.read_input_csv(temp_input_path)

        if len(websites) == 0:
            raise HTTPException(status_code=400, detail="No valid websites found in CSV")

        # Already handled by csv_processor (capped at 500)

        # Create progress tracking session
        progress_tracker.create_session(session_id, len(websites))

        # Start processing in background
        async def process_in_background():
            try:
                # Progress callback with API-specific progress
                def update_progress(progress_data: dict, stage: str = None, message: str = None, error: str = None):
                    # Calculate total progress
                    total_progress = 0
                    if progress_data:
                        sl = progress_data['storeleads']
                        ce = progress_data['companyenrich']
                        sc = progress_data['scoring']

                        # Calculate weighted total
                        if ce['total'] > 0:
                            total_progress = sl['current'] + ce['current'] + sc['current']
                        else:
                            total_progress = sl['current'] + sc['current']

                    progress_tracker.update_progress(
                        session_id,
                        current=total_progress,
                        stage=stage,
                        message=message,
                        error=error,
                        api_progress=progress_data
                    )
                    # Send WebSocket update if connected
                    if session_id in active_websockets:
                        try:
                            asyncio.create_task(active_websockets[session_id].send_json(
                                progress_tracker.get_progress(session_id)
                            ))
                        except:
                            pass

                # Process with progress tracking
                df = await processor.process_websites(websites, session_id, update_progress)

                output_filename = f"lead_scores_{timestamp}.csv"
                output_path = f"output/{output_filename}"
                processor.save_results(df, output_path)

                summary = processor.generate_summary(df)

                # Store results in progress tracker
                progress_data = progress_tracker.get_progress(session_id)
                if progress_data:
                    progress_data['result_file'] = output_filename
                    progress_data['summary'] = summary

                # Mark session as complete
                progress_tracker.complete_session(session_id, success=True)

                # Send final update
                if session_id in active_websockets:
                    try:
                        await active_websockets[session_id].send_json(
                            progress_tracker.get_progress(session_id)
                        )
                    except:
                        pass

            except Exception as e:
                error_detail = f"{str(e)}\n{traceback.format_exc()}"
                progress_tracker.update_progress(session_id, error=error_detail)
                progress_tracker.complete_session(session_id, success=False, message=str(e))

        # Add to background tasks
        background_tasks.add_task(process_in_background)

        # Return immediately with session ID
        return {
            "status": "processing",
            "session_id": session_id,
            "message": f"Processing {len(websites)} websites in background"
        }

    except Exception as e:
        # Log detailed error
        error_detail = f"{str(e)}\n{traceback.format_exc()}"
        progress_tracker.update_progress(session_id, error=error_detail)
        progress_tracker.complete_session(session_id, success=False, message=str(e))

        raise HTTPException(status_code=500, detail={
            "error": str(e),
            "session_id": session_id,
            "traceback": traceback.format_exc()
        })

    finally:
        if os.path.exists(temp_input_path):
            os.remove(temp_input_path)

@app.get("/download/{filename}")
async def download_file(filename: str):
    file_path = f"output/{filename}"

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(
        path=file_path,
        filename=filename,
        media_type='text/csv'
    )

@app.get("/health")
async def health_check():
    return {"status": "healthy"}