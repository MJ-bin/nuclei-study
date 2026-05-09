from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse
import base64
import json
import time


HOST = "127.0.0.1"
PORT = 8010
CSRF_TOKEN = "lab-csrf-2026"
API_TOKEN = "public-demo-api-token"
BASIC_USER = "lab"
BASIC_PASS = "public-demo-basic-password"


class NucleiLabHandler(BaseHTTPRequestHandler):
    server_version = "NucleiLab/0.2"
    sys_version = ""

    def log_message(self, fmt, *args):
        return

    def do_GET(self):
        parsed = urlparse(self.path)
        routes = {
            "/": self.handle_index,
            "/debug": self.handle_debug,
            "/admin": self.handle_admin,
            "/login": self.handle_login,
            "/api/private": self.handle_private,
            "/basic-only": self.handle_basic_only,
            "/headers": self.handle_headers,
            "/search": self.handle_search,
            "/redirect": self.handle_redirect,
            "/slow": self.handle_slow,
            "/robots.txt": self.handle_robots,
            "/wp-login.php": self.handle_wordpress_login,
        }
        handler = routes.get(parsed.path, self.handle_not_found)
        handler(parsed)

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/login":
            self.handle_api_login()
            return
        self.handle_not_found(parsed)

    def send_common_headers(self, status_code, content_type):
        self.send_response(status_code)
        self.send_header("Content-Type", content_type)
        self.send_header("X-Powered-By", "Express")
        self.send_header("X-Lab-Target", "nuclei-local-training")
        self.send_header("Set-Cookie", "lab_session=guest; HttpOnly; Path=/")

    def finish_response(self, body):
        if isinstance(body, str):
            body = body.encode("utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def handle_index(self, _parsed):
        body = """<html>
<head>
  <title>Nuclei Local Lab</title>
  <meta name="generator" content="WordPress 6.4.1" />
</head>
<body>
  <h1>Nuclei Local Lab</h1>
  <p>Local-only target for curl and nuclei template practice.</p>
  <ul>
    <li><a href="/debug">Debug endpoint</a></li>
    <li><a href="/admin">Redirecting admin panel</a></li>
    <li><a href="/login">Login form with CSRF token</a></li>
    <li><a href="/api/private">Header-protected API</a></li>
    <li><a href="/basic-only">Basic-auth protected API</a></li>
    <li><a href="/search?q=hello">Search endpoint for DAST fuzzing</a></li>
    <li><a href="/wp-login.php">WordPress-looking fingerprint page</a></li>
  </ul>
</body>
</html>
"""
        self.send_common_headers(200, "text/html; charset=utf-8")
        self.finish_response(body)

    def handle_debug(self, _parsed):
        payload = {
            "app": "AcmeNotes",
            "version": "1.4.2-dev",
            "debug": True,
            "build": "2026.05.09-lab",
            "debug_marker": "debug-panel-enabled",
        }
        self.send_common_headers(200, "application/json")
        self.send_header("X-Debug-Mode", "enabled")
        self.finish_response(json.dumps(payload, indent=2))

    def handle_admin(self, _parsed):
        self.send_response(302)
        self.send_header("Location", "/login")
        self.send_header("X-Redirect-Reason", "auth-required")
        self.end_headers()

    def handle_login(self, _parsed):
        body = f"""<html>
<head><title>Acme Control Panel</title></head>
<body>
  <h1>Login</h1>
  <form action="/api/login" method="post">
    <input type="hidden" name="csrf" value="{CSRF_TOKEN}" />
    <input name="username" />
    <input name="password" type="password" />
    <button type="submit">Sign in</button>
  </form>
</body>
</html>
"""
        self.send_common_headers(200, "text/html; charset=utf-8")
        self.finish_response(body)

    def handle_api_login(self):
        length = int(self.headers.get("Content-Length", "0"))
        raw_body = self.rfile.read(length).decode("utf-8", errors="replace")
        form = parse_qs(raw_body)
        username = form.get("username", [""])[0]
        password = form.get("password", [""])[0]
        csrf = form.get("csrf", [""])[0]

        ok = username == "admin" and password == "public-demo-login-password" and csrf == CSRF_TOKEN
        status = 200 if ok else 403
        payload = {
            "authenticated": ok,
            "user": username if ok else "",
            "session_token": "public-demo-session-token" if ok else "",
        }
        self.send_common_headers(status, "application/json")
        self.send_header("X-Auth-Result", "ok" if ok else "denied")
        self.finish_response(json.dumps(payload, indent=2))

    def handle_private(self, _parsed):
        if self.headers.get("X-Lab-Auth") != API_TOKEN:
            self.send_common_headers(401, "application/json")
            self.send_header("WWW-Authenticate", 'Bearer realm="nuclei-lab"')
            self.finish_response(json.dumps({"error": "missing X-Lab-Auth"}))
            return

        payload = {
            "feature": "custom-header-auth",
            "status": "private config visible",
        }
        self.send_common_headers(200, "application/json")
        self.finish_response(json.dumps(payload, indent=2))

    def handle_basic_only(self, _parsed):
        expected = "Basic " + base64.b64encode(f"{BASIC_USER}:{BASIC_PASS}".encode()).decode()
        if self.headers.get("Authorization") != expected:
            self.send_common_headers(401, "application/json")
            self.send_header("WWW-Authenticate", 'Basic realm="nuclei-lab"')
            self.finish_response(json.dumps({"error": "basic auth required"}))
            return

        payload = {
            "feature": "basic-auth",
            "status": "basic-only area visible",
        }
        self.send_common_headers(200, "application/json")
        self.finish_response(json.dumps(payload, indent=2))

    def handle_headers(self, _parsed):
        selected = {
            key: value
            for key, value in self.headers.items()
            if key.lower() in {"user-agent", "x-lab-auth", "authorization", "cookie"}
        }
        self.send_common_headers(200, "application/json")
        self.finish_response(json.dumps(selected, indent=2))

    def handle_search(self, parsed):
        params = parse_qs(parsed.query)
        query = params.get("q", [""])[0]
        marker = query
        sql_error = ""
        if "'" in query or '"' in query:
            sql_error = "<pre>SQL syntax error near user supplied query</pre>"
        body = f"""<html>
<head><title>Search</title></head>
<body>
  <h1>Search</h1>
  <p>query: {marker}</p>
  {sql_error}
</body>
</html>
"""
        self.send_common_headers(200, "text/html; charset=utf-8")
        self.finish_response(body)

    def handle_redirect(self, parsed):
        params = parse_qs(parsed.query)
        destination = params.get("next", ["/debug"])[0]
        self.send_response(302)
        self.send_header("Location", destination)
        self.end_headers()

    def handle_slow(self, _parsed):
        time.sleep(0.4)
        self.send_common_headers(200, "text/plain; charset=utf-8")
        self.finish_response("slow endpoint reached\n")

    def handle_robots(self, _parsed):
        body = "User-agent: *\nDisallow: /debug\nDisallow: /api/private\n"
        self.send_common_headers(200, "text/plain; charset=utf-8")
        self.finish_response(body)

    def handle_wordpress_login(self, _parsed):
        body = """<html>
<head><title>WordPress Login</title></head>
<body class="login wp-core-ui">
  <form id="loginform" action="/wp-login.php" method="post">
    <input name="log" />
    <input name="pwd" type="password" />
    <input type="submit" name="wp-submit" value="Log In" />
  </form>
</body>
</html>
"""
        self.send_common_headers(200, "text/html; charset=utf-8")
        self.finish_response(body)

    def handle_not_found(self, _parsed):
        self.send_common_headers(404, "text/plain; charset=utf-8")
        self.finish_response("404 not found\n")


def main():
    server = ThreadingHTTPServer((HOST, PORT), NucleiLabHandler)
    print(f"[*] Nuclei lab listening on http://{HOST}:{PORT}")
    server.serve_forever()


if __name__ == "__main__":
    main()
