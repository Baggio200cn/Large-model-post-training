from http.server import BaseHTTPRequestHandler
import json

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

        response = {
            'status': 'success',
            'message': 'Test API works!',
            'timestamp': '2026-01-25'
        }

        self.wfile.write(json.dumps(response).encode('utf-8'))
        return
