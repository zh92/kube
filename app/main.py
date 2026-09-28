import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

DATA_FILE = Path(__file__).parent / "tasks.json"

def load_tasks():
    try:
        return json.loads(DATA_FILE.read_text())
    except FileNotFoundError:
        return []

def save_tasks():
    tmp = DATA_FILE.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(tasks))
    tmp.replace(DATA_FILE)

tasks: list[dict] = load_tasks()

class Handler(BaseHTTPRequestHandler):
    def _send(self, status, payload):
        body = json.dumps(payload).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/healthz":
            self._send(200, {"status": "ok"})
        elif self.path == "/tasks":
            self._send(200, tasks)
        elif self.path == "/readyz":
            self._send(200, {"status": "ready"})
        else:
            self._send(404, {"detail": "not found"})

    def do_POST(self):
        if self.path != "/tasks":
            self._send(404, {"detail": "not found"})
            return
        length = int(self.headers.get("Content-Length", 0))
        try:
            data = json.loads(self.rfile.read(length) or b"{}")
        except json.JSONDecodeError:
            self._send(400, {"detail": "invalid json"})
            return
        if "title" not in data:
            self._send(422, {"detail": "title is required"})
            return
        task = {"id": len(tasks) + 1, "title": data["title"], "status": "todo"}
        tasks.append(task)
        save_tasks()
        self._send(201, task)

    def do_PATCH(self):
        parts = self.path.strip("/").split("/")
        if len(parts) != 2 or parts[0] != "tasks":
            self._send(404, {"detail": "not found"})
            return
        try:
            task_id = int(parts[1])
        except ValueError:
            self._send(404, {"detail": "not found"})
            return
        task = next((t for t in tasks if t["id"] == task_id), None)
        if task is None:
            self._send(404, {"detail": "task not found"})
            return
        length = int(self.headers.get("Content-Length", 0))
        try:
            data = json.loads(self.rfile.read(length) or b"{}")
        except json.JSONDecodeError:
            self._send(400, {"detail": "invalid json"})
            return
        if data.get("status") not in ("todo", "doing", "done"):
            self._send(422, {"detail": "status must be todo, doing or done"})
            return
        task["status"] = data["status"]
        save_tasks()
        self._send(200, task)

    def log_message(self, *args):
        pass  # quiet for now; structured logs get their own step later

if __name__ == "__main__":
    server = ThreadingHTTPServer(("127.0.0.1", 8000), Handler)
    print("serving on http://127.0.0.1:8000")
    server.serve_forever()
