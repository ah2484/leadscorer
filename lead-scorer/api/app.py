"""
Simple HTTP handler for Vercel
"""
from http.server import BaseHTTPRequestHandler
import json

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

        response = {
            "message": "Lead Scorer API",
            "status": "running",
            "note": "This is a simplified version. For full functionality, please use Railway or other platforms that support FastAPI/WebSockets."
        }

        self.wfile.write(json.dumps(response).encode())
        return

    def do_POST(self):
        """Handle POST requests"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

        response = {
            "message": "POST endpoint",
            "note": "Full API functionality requires FastAPI support. Consider deploying to Railway."
        }

        self.wfile.write(json.dumps(response).encode())
        return