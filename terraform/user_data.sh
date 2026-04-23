#!/bin/bash
exec > >(tee /var/log/user-data.log|logger -t user-data -s 2>/dev/console) 2>&1
set -e

echo "Starting CPU bootstrap"

# Basic runtime for a lightweight local API
dnf update -y
dnf install -y python3

mkdir -p /opt/cpu-api

cat > /opt/cpu-api/server.py << 'PYEOF'
#!/usr/bin/env python3
import json
from http.server import BaseHTTPRequestHandler, HTTPServer


class Handler(BaseHTTPRequestHandler):
    def _send_json(self, status_code, payload):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        return

    def do_GET(self):
        if self.path == "/health":
            self._send_json(200, {"status": "ok", "mode": "cpu"})
            return
        self._send_json(404, {"error": "not_found"})

    def do_POST(self):
        if self.path in ("/v1/chat/completions", "/v1/completions"):
            self._send_json(
                200,
                {
                    "id": "cpu-fallback-demo",
                    "object": "chat.completion",
                    "choices": [
                        {
                            "index": 0,
                            "finish_reason": "stop",
                            "message": {
                                "role": "assistant",
                                "content": "CPU fallback endpoint is running. SSH to instance for LightGBM benchmark."
                            },
                        }
                    ],
                },
            )
            return
        self._send_json(404, {"error": "not_found"})


if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", 8000), Handler)
    server.serve_forever()
PYEOF

cat > /etc/systemd/system/cpu-api.service << 'SVCEOF'
[Unit]
Description=CPU Fallback API Service
After=network.target

[Service]
Type=simple
ExecStart=/usr/bin/python3 /opt/cpu-api/server.py
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
SVCEOF

systemctl daemon-reload
systemctl enable cpu-api
systemctl start cpu-api

echo "CPU bootstrap complete"
er started with model $MODEL"