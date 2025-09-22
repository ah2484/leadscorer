"""
Vercel-compatible API endpoint for the Lead Scorer application.
Note: WebSocket functionality is not supported on Vercel.
This version uses polling instead of WebSockets for progress updates.
"""

import os
import sys
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import tempfile
import uuid
import asyncio
from typing import Optional

from app.csv_processor import CSVProcessor
from app.progress_tracker import progress_tracker

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store results temporarily (in production, use a database or Redis)
results_store = {}

@app.get("/", response_class=HTMLResponse)
async def index():
    """Serve the main HTML page"""
    html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Lead Scorer - Vercel Version</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }

        .container {
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            padding: 40px;
            max-width: 800px;
            width: 100%;
        }

        h1 {
            color: #333;
            margin-bottom: 10px;
            font-size: 2.5em;
            text-align: center;
        }

        .subtitle {
            color: #666;
            text-align: center;
            margin-bottom: 30px;
        }

        .warning {
            background: #fff3cd;
            border: 1px solid #ffc107;
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 30px;
            color: #856404;
        }

        .tabs {
            display: flex;
            gap: 10px;
            margin-bottom: 30px;
            border-bottom: 2px solid #e0e0e0;
        }

        .tab {
            padding: 12px 24px;
            background: none;
            border: none;
            color: #666;
            cursor: pointer;
            font-size: 16px;
            font-weight: 500;
            position: relative;
            transition: all 0.3s;
        }

        .tab:hover {
            color: #667eea;
        }

        .tab.active {
            color: #667eea;
        }

        .tab.active::after {
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
        }

        .tab-content.active {
            display: block;
        }

        textarea {
            width: 100%;
            min-height: 200px;
            padding: 15px;
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            font-size: 14px;
            font-family: 'Monaco', 'Courier New', monospace;
            resize: vertical;
            transition: border-color 0.3s;
        }

        textarea:focus {
            outline: none;
            border-color: #667eea;
        }

        .file-upload {
            border: 2px dashed #e0e0e0;
            border-radius: 10px;
            padding: 40px;
            text-align: center;
            transition: all 0.3s;
            cursor: pointer;
            position: relative;
        }

        .file-upload:hover {
            border-color: #667eea;
            background: #f8f9ff;
        }

        .file-upload.active {
            border-color: #667eea;
            background: #f8f9ff;
        }

        .file-upload input[type="file"] {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            opacity: 0;
            cursor: pointer;
        }

        .button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 15px 40px;
            border-radius: 10px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
            display: block;
            width: 100%;
            margin-top: 20px;
        }

        .button:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(102, 126, 234, 0.4);
        }

        .button:disabled {
            opacity: 0.5;
            cursor: not-allowed;
            transform: none;
        }

        .progress-container {
            margin-top: 30px;
            padding: 20px;
            background: #f8f9ff;
            border-radius: 10px;
            display: none;
        }

        .progress-container.active {
            display: block;
        }

        .progress-bar {
            width: 100%;
            height: 30px;
            background: #e0e0e0;
            border-radius: 15px;
            overflow: hidden;
            margin-bottom: 15px;
        }

        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            transition: width 0.3s;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: 600;
        }

        .status {
            margin-top: 20px;
            padding: 15px;
            border-radius: 10px;
            display: none;
        }

        .status.success {
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
            display: block;
        }

        .status.error {
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
            display: block;
        }

        .counter {
            text-align: center;
            color: #666;
            margin-top: 10px;
            font-size: 14px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 Lead Scorer</h1>
        <p class="subtitle">Score and prioritize your leads efficiently</p>

        <div class="warning">
            <strong>⚠️ Vercel Deployment Notice:</strong><br>
            This is a simplified version for Vercel. Progress updates use polling instead of WebSockets.
            For full functionality with real-time updates, consider deploying to Railway, Render, or AWS.
        </div>

        <div class="tabs">
            <button class="tab active" onclick="switchTab('paste')">📝 Paste Domains</button>
            <button class="tab" onclick="switchTab('upload')">📁 Upload CSV</button>
        </div>

        <div id="paste-tab" class="tab-content active">
            <textarea
                id="domain-input"
                placeholder="Paste your domains here, one per line...&#10;&#10;Example:&#10;example.com&#10;store.example.com&#10;https://another-example.com"
            ></textarea>
            <div class="counter">
                <span id="domain-count">0</span> / 2000 domains
            </div>
        </div>

        <div id="upload-tab" class="tab-content">
            <div class="file-upload" id="file-upload">
                <input type="file" id="file-input" accept=".csv">
                <div>
                    <p style="font-size: 48px; margin-bottom: 10px;">📤</p>
                    <p style="color: #666; font-weight: 500;">Drop your CSV file here or click to browse</p>
                    <p style="color: #999; font-size: 14px; margin-top: 10px;">Maximum 2000 domains</p>
                </div>
            </div>
        </div>

        <button class="button" onclick="processInput()" id="process-btn">
            🎯 Score Leads
        </button>

        <div class="progress-container" id="progress-container">
            <div class="progress-bar">
                <div class="progress-fill" id="progress-fill" style="width: 0%">0%</div>
            </div>
            <div id="progress-message">Initializing...</div>
        </div>

        <div class="status" id="status"></div>
    </div>

    <script>
        let activeTab = 'paste';
        let selectedFile = null;
        let currentSessionId = null;
        let pollInterval = null;

        // Tab switching
        function switchTab(tab) {
            activeTab = tab;

            // Update tab buttons
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            event.target.classList.add('active');

            // Update tab content
            document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
            document.getElementById(tab + '-tab').classList.add('active');
        }

        // Domain counter
        document.getElementById('domain-input').addEventListener('input', (e) => {
            const domains = e.target.value.split('\\n').filter(line => line.trim().length > 0);
            document.getElementById('domain-count').textContent = domains.length;

            if (domains.length > 2000) {
                e.target.style.borderColor = '#dc3545';
                document.getElementById('domain-count').style.color = '#dc3545';
            } else {
                e.target.style.borderColor = '#e0e0e0';
                document.getElementById('domain-count').style.color = '#666';
            }
        });

        // File upload
        document.getElementById('file-input').addEventListener('change', (e) => {
            selectedFile = e.target.files[0];
            if (selectedFile) {
                document.getElementById('file-upload').classList.add('active');
                document.querySelector('#file-upload p:nth-child(2)').textContent =
                    '✅ ' + selectedFile.name + ' selected';
            }
        });

        // Drag and drop
        const fileUpload = document.getElementById('file-upload');

        fileUpload.addEventListener('dragover', (e) => {
            e.preventDefault();
            fileUpload.classList.add('active');
        });

        fileUpload.addEventListener('dragleave', () => {
            fileUpload.classList.remove('active');
        });

        fileUpload.addEventListener('drop', (e) => {
            e.preventDefault();
            selectedFile = e.dataTransfer.files[0];
            document.getElementById('file-input').files = e.dataTransfer.files;
            if (selectedFile) {
                document.querySelector('#file-upload p:nth-child(2)').textContent =
                    '✅ ' + selectedFile.name + ' selected';
            }
        });

        async function processInput() {
            const formData = new FormData();

            if (activeTab === 'paste') {
                // Create CSV from pasted domains
                const textarea = document.getElementById('domain-input');
                const domains = textarea.value.split('\\n')
                    .filter(line => line.trim().length > 0)
                    .map(line => {
                        let cleaned = line.trim();
                        cleaned = cleaned.replace(/["'`]/g, '');
                        if (cleaned.includes(',')) {
                            cleaned = cleaned.split(',')[0].trim();
                        }
                        cleaned = cleaned.replace(/^https?:\\/\\//i, '');
                        cleaned = cleaned.replace(/^www\\./i, '');
                        if (cleaned.includes('/')) {
                            cleaned = cleaned.split('/')[0];
                        }
                        return cleaned.trim();
                    })
                    .filter(domain => domain.length > 0);

                if (domains.length === 0) {
                    showStatus('Please enter at least one domain', 'error');
                    return;
                }

                if (domains.length > 2000) {
                    showStatus('Maximum 2000 domains allowed', 'error');
                    return;
                }

                const csvContent = 'website\\n' + domains.join('\\n');
                const blob = new Blob([csvContent], { type: 'text/csv' });
                const file = new File([blob], 'domains.csv', { type: 'text/csv' });
                formData.append('file', file);
            } else {
                if (!selectedFile) {
                    showStatus('Please select a CSV file', 'error');
                    return;
                }
                formData.append('file', selectedFile);
            }

            // Show progress
            document.getElementById('progress-container').classList.add('active');
            document.getElementById('process-btn').disabled = true;
            document.getElementById('status').className = 'status';

            try {
                // Start processing
                const response = await fetch('/api/process', {
                    method: 'POST',
                    body: formData
                });

                const result = await response.json();

                if (result.session_id) {
                    currentSessionId = result.session_id;
                    // Start polling for progress
                    startPolling();
                } else if (result.error) {
                    showStatus(result.error, 'error');
                    document.getElementById('progress-container').classList.remove('active');
                    document.getElementById('process-btn').disabled = false;
                }
            } catch (error) {
                showStatus('Error: ' + error.message, 'error');
                document.getElementById('progress-container').classList.remove('active');
                document.getElementById('process-btn').disabled = false;
            }
        }

        function startPolling() {
            pollInterval = setInterval(async () => {
                try {
                    const response = await fetch(`/api/progress/${currentSessionId}`);
                    const data = await response.json();

                    updateProgress(data);

                    if (data.completed) {
                        stopPolling();

                        if (data.success) {
                            // Download results
                            const downloadResponse = await fetch(`/api/download/${currentSessionId}`);
                            if (downloadResponse.ok) {
                                const blob = await downloadResponse.blob();
                                const url = window.URL.createObjectURL(blob);
                                const a = document.createElement('a');
                                a.style.display = 'none';
                                a.href = url;
                                a.download = `lead_scores_${currentSessionId}.csv`;
                                document.body.appendChild(a);
                                a.click();
                                window.URL.revokeObjectURL(url);

                                showStatus('✅ Processing complete! Your file is downloading.', 'success');
                            }
                        } else {
                            showStatus('❌ Processing failed. Please try again.', 'error');
                        }

                        document.getElementById('process-btn').disabled = false;
                    }
                } catch (error) {
                    console.error('Polling error:', error);
                }
            }, 1000);
        }

        function stopPolling() {
            if (pollInterval) {
                clearInterval(pollInterval);
                pollInterval = null;
            }
        }

        function updateProgress(data) {
            const progressFill = document.getElementById('progress-fill');
            const progressMessage = document.getElementById('progress-message');

            const percentage = data.percentage || 0;
            progressFill.style.width = percentage + '%';
            progressFill.textContent = percentage + '%';

            progressMessage.textContent = data.message || 'Processing...';
        }

        function showStatus(message, type) {
            const status = document.getElementById('status');
            status.textContent = message;
            status.className = 'status ' + type;
        }
    </script>
</body>
</html>
    """
    return HTMLResponse(content=html_content)

@app.post("/api/process")
async def process_file(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    """Process uploaded CSV file"""
    session_id = str(uuid.uuid4())

    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as tmp_file:
        content = await file.read()
        tmp_file.write(content)
        tmp_path = tmp_file.name

    # Start background processing
    background_tasks.add_task(process_csv_background, session_id, tmp_path)

    return JSONResponse({"session_id": session_id, "message": "Processing started"})

async def process_csv_background(session_id: str, file_path: str):
    """Background task to process CSV"""
    processor = CSVProcessor()

    try:
        # Read domains from CSV
        websites = processor.read_input_csv(file_path)

        # Create progress tracking
        progress_tracker.create_session(session_id, len(websites))

        # Process websites with progress callback
        def progress_callback(api_progress, stage=None, message=None, error=None):
            progress_tracker.update_progress(
                session_id,
                stage=stage,
                message=message,
                error=error,
                api_progress=api_progress
            )

        # Process the websites
        df = await processor.process_websites(websites, session_id, progress_callback)

        # Save results
        output_path = processor.save_results(df)

        # Store results for download
        results_store[session_id] = output_path

        # Mark as complete
        progress_tracker.complete_session(session_id, success=True)

    except Exception as e:
        progress_tracker.complete_session(session_id, success=False, message=str(e))

    finally:
        # Clean up temp file
        try:
            os.unlink(file_path)
        except:
            pass

@app.get("/api/progress/{session_id}")
async def get_progress(session_id: str):
    """Get processing progress"""
    progress = progress_tracker.get_progress(session_id)

    if not progress:
        raise HTTPException(status_code=404, detail="Session not found")

    return JSONResponse(progress)

@app.get("/api/download/{session_id}")
async def download_results(session_id: str):
    """Download processed results"""
    if session_id not in results_store:
        raise HTTPException(status_code=404, detail="Results not found")

    file_path = results_store[session_id]

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(
        path=file_path,
        media_type='text/csv',
        filename=f'lead_scores_{session_id}.csv'
    )

# Handler for Vercel - needs to be wrapped for ASGI
from mangum import Mangum
handler = Mangum(app)