import http.client
import http.server
import os
import socketserver

PORT = 3000
API_TARGET = "localhost"
API_PORT = 5000
DIRECTORY = "wwwroot"


class SPAServer(http.server.SimpleHTTPRequestHandler):
    extensions_map = http.server.SimpleHTTPRequestHandler.extensions_map.copy()
    extensions_map.update(
        {
            ".js": "application/javascript",
            ".mjs": "application/javascript",
            ".css": "text/css",
            ".json": "application/json",
            ".png": "image/png",
            ".jpg": "image/jpeg",
            ".svg": "image/svg+xml",
            ".wasm": "application/wasm",
        }
    )

    # --- Disable Caching ---
    def end_headers(self):
        """Send custom headers to disable browser caching before closing headers."""
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        super().end_headers()

    # --- Routing Logic ---

    def do_GET(self):
        if self.path.startswith("/api"):
            self.proxy_request()
        else:
            # SPA Fallback logic
            path = self.translate_path(self.path)
            if not os.path.exists(path):
                self.path = "index.html"
            return super().do_GET()

    def do_POST(self):
        self.proxy_request()

    def do_PUT(self):
        self.proxy_request()

    def do_PATCH(self):
        self.proxy_request()

    def do_DELETE(self):
        self.proxy_request()

    # --- Proxy Engine ---

    def proxy_request(self):
        """Forwards request, headers, and body to the backend API."""
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length) if content_length > 0 else None

        conn = http.client.HTTPConnection(API_TARGET, API_PORT)

        # Forward headers from original request
        headers = {key: value for key, value in self.headers.items()}

        try:
            # Send the request with the specific method (GET, POST, PUT, etc.)
            conn.request(self.command, self.path, body=body, headers=headers)
            res = conn.getresponse()

            # Pass the backend response back to the browser
            self.send_response(res.status)
            for key, value in res.getheaders():
                # Avoid duplicate hop-by-hop headers if necessary
                self.send_header(key, value)
            self.end_headers()
            self.wfile.write(res.read())

        except ConnectionRefusedError:
            self.send_error(502, f"Backend at {API_TARGET}:{API_PORT} is unreachable.")
        finally:
            conn.close()


os.chdir(DIRECTORY)
socketserver.TCPServer.allow_reuse_address = True

with socketserver.TCPServer(("", PORT), SPAServer) as httpd:
    print(f"SPA Frontend: http://localhost:{PORT}")
    print(f"API Proxy: Forwarding /api -> http://{API_TARGET}:{API_PORT}")
    httpd.serve_forever()
