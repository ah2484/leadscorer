"""
Vercel-compatible handler for Lead Scorer API
"""
from http.server import BaseHTTPRequestHandler
import json

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests"""
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

            html = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>Lead Scorer API</title>
                <style>
                    body { font-family: Arial, sans-serif; padding: 40px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }
                    .container { max-width: 800px; margin: 0 auto; background: white; padding: 40px; border-radius: 10px; color: #333; }
                    h1 { color: #667eea; }
                    .note { background: #fff3cd; padding: 15px; border-radius: 5px; color: #856404; margin-top: 20px; }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>🚀 Lead Scorer API</h1>
                    <p>Welcome to the Lead Scorer API!</p>
                    <div class="note">
                        <strong>⚠️ Note:</strong> This is a basic deployment on Vercel.
                        For full functionality including CSV processing and lead scoring,
                        please deploy to Railway or another platform that supports FastAPI.
                    </div>
                    <h3>Deployment Options:</h3>
                    <ul>
                        <li><strong>Railway</strong> - Full support for FastAPI and WebSockets (Recommended)</li>
                        <li><strong>Render</strong> - Good FastAPI support</li>
                        <li><strong>AWS Lambda</strong> - Serverless with API Gateway</li>
                        <li><strong>Google Cloud Run</strong> - Container-based deployment</li>
                    </ul>
                </div>
            </body>
            </html>
            """
            self.wfile.write(html.encode())
        else:
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()

            response = {
                "status": "running",
                "path": self.path,
                "message": "Lead Scorer API - Basic Vercel Deployment"
            }
            self.wfile.write(json.dumps(response).encode())

        return

    def do_POST(self):
        """Handle POST requests"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

        response = {
            "message": "POST endpoint received",
            "path": self.path,
            "note": "Full API functionality requires FastAPI. Deploy to Railway for complete features."
        }

        self.wfile.write(json.dumps(response).encode())
        return