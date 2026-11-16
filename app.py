import json, os, pathlib
from http.server import BaseHTTPRequestHandler, HTTPServer

DATA = pathlib.Path(os.environ.get("DATA_DIR", "/data")) / "notes.json"
PORT = int(os.environ.get("PORT", "8202"))

def load():
    return json.loads(DATA.read_text()) if DATA.exists() else []

def save(notes):
    DATA.parent.mkdir(parents=True, exist_ok=True)
    DATA.write_text(json.dumps(notes, ensure_ascii=False, indent=2))

class Handler(BaseHTTPRequestHandler):
    def _send(self, code, body, ctype="application/json"):
        data = body.encode() if isinstance(body, str) else body
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if self.path == "/health":
            return self._send(200, '{"status":"ok"}')
        if self.path == "/notes":
            return self._send(200, json.dumps(load(), ensure_ascii=False))
        if self.path == "/":
            items = "".join(f"<li>{n['text']}</li>" for n in load())
            return self._send(200, f"<h1>Заметки</h1><ul>{items}</ul>", "text/html; charset=utf-8")
        self._send(404, '{"error":"not found"}')

    def do_POST(self):
        if self.path != "/notes":
            return self._send(404, '{"error":"not found"}')
        length = int(self.headers.get("Content-Length", 0))
        try:
            payload = json.loads(self.rfile.read(length) or b"{}")
            text = payload["text"].strip()
            assert text
        except Exception:
            return self._send(400, '{"error":"bad request"}')
        notes = load(); notes.append({"text": text}); save(notes)
        self._send(201, json.dumps({"saved": text}, ensure_ascii=False))

    def log_message(self, fmt, *args):
        print("%s - %s" % (self.address_string(), fmt % args), flush=True)

if __name__ == "__main__":
    print(f"listening on :{PORT}, data={DATA}", flush=True)
    HTTPServer(("0.0.0.0", PORT), Handler).serve_forever()