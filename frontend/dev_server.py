import http.client
import http.server
import os
import shutil
import socket
import socketserver
import time

PORT = 3000
API_TARGET = "127.0.0.1"
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
            physical_path = self.translate_path(self.path)
            if not os.path.exists(physical_path):
                filename = os.path.basename(self.path)
                if "." in filename:
                    self.send_error(404, f"File not found: {self.path}")
                    return
                else:
                    self.path = "/index.html"

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
        """Forwards request using streaming to reduce latency and RAM usage."""
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length) if content_length > 0 else None

        # 1. Use a context manager to ensure the connection is handled cleanly
        conn = http.client.HTTPConnection(API_TARGET, API_PORT)
        conn.connect()  # Manually connect so we can access the socket
        conn.sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

        try:
            # 2. Forward headers (Filter out 'Host' to avoid logic errors at target)
            headers = {k: v for k, v in self.headers.items() if k.lower() != "host"}

            t = time.perf_counter()
            conn.request(self.command, self.path, body=body, headers=headers)
            print(time.perf_counter() - t)
            res = conn.getresponse()

            # 3. Send Response Status and Headers immediately
            self.send_response(res.status)
            for key, value in res.getheaders():
                # Important: Don't forward 'Transfer-Encoding' if we aren't handling chunks manually
                if key.lower() not in ["transfer-encoding", "content-length"]:
                    self.send_header(key, value)

            # Explicitly set content length if provided by backend
            length = res.getheader("Content-Length")
            if length:
                self.send_header("Content-Length", length)

            self.end_headers()

            # 4. STREAMING: Instead of res.read(), pipe the source to the destination
            # shutil.copyfileobj is highly optimized for internal buffering
            shutil.copyfileobj(res, self.wfile)

        except (ConnectionRefusedError, http.client.HTTPException) as e:
            self.send_error(502, f"Gateway Error: {e}")
        finally:
            conn.close()


class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass


os.chdir(DIRECTORY)
socketserver.TCPServer.allow_reuse_address = True

with ThreadedTCPServer(("", PORT), SPAServer) as httpd:
    print(f"SPA Frontend: http://localhost:{PORT}")
    print(f"API Proxy: Forwarding /api -> http://{API_TARGET}:{API_PORT}")
    httpd.serve_forever()
