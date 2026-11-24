# -*- coding: utf-8 -*-
"""
ai_chart_toolkit.api_server
Zero-dependency HTTP REST API server for web agents, cURL, and cloud integrations.
Listens on port 8000 by default (configurable via PORT env var).
"""

import os
import sys
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from .tool import execute_chart_tool
from .schemas import UNIFIED_TOOL_SCHEMA

class ChartHTTPHandler(BaseHTTPRequestHandler):
    def _send_json(self, status_code: int, data: dict):
        body = json.dumps(data, indent=2).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self._send_json(200, {"status": "ok"})

    def do_GET(self):
        if self.path in ["/", "/health"]:
            self._send_json(200, {
                "service": "ai-chart-toolkit-api",
                "version": "1.0.0",
                "status": "healthy",
                "endpoints": {
                    "POST /render": "Execute chart generation with JSON payload",
                    "GET /schema": "Retrieve tool definition JSON schema",
                    "GET /health": "Health check"
                }
            })
        elif self.path == "/schema":
            self._send_json(200, UNIFIED_TOOL_SCHEMA)
        else:
            self._send_json(404, {"error": "Not Found"})

    def do_POST(self):
        if self.path in ["/render", "/generate"]:
            content_length = int(self.headers.get("Content-Length", 0))
            if content_length == 0:
                self._send_json(400, {"success": False, "error": "Empty request body."})
                return

            body = self.rfile.read(content_length).decode("utf-8")
            try:
                payload = json.loads(body)
            except json.JSONDecodeError as e:
                self._send_json(400, {"success": False, "error": f"Invalid JSON: {e}"})
                return

            chart_type = payload.pop("chart_type", payload.pop("type", "flowchart"))
            result = execute_chart_tool(chart_type, payload)
            status = 200 if result.get("success") else 400
            self._send_json(status, result)
        else:
            self._send_json(404, {"error": f"Path '{self.path}' not found. Use POST /render."})

    def log_message(self, format, *args):
        sys.stderr.write(f"[{self.log_date_time_string()}] {format % args}\n")

def main():
    port = int(os.environ.get("PORT", 8000))
    host = os.environ.get("HOST", "0.0.0.0")
    server = HTTPServer((host, port), ChartHTTPHandler)
    sys.stderr.write(f"ai-chart-toolkit REST API running on http://{host}:{port}\n")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        sys.stderr.write("Server shutting down.\n")
        server.server_close()

if __name__ == "__main__":
    main()
