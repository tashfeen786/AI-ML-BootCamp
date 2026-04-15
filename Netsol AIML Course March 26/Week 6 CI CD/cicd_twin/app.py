"""
CI/CD Pipeline Digital Twin — Main Application
================================================
Dependencies: Flask only (stdlib for everything else)
Run:  python3 app.py   then open http://localhost:5050
"""

import json
import time
import queue
import threading
import webbrowser
from pathlib import Path
from flask import Flask, render_template, jsonify, request, Response, stream_with_context

app = Flask(__name__)
BASE_DIR = Path(__file__).parent


class PipelineEngine:
    def __init__(self):
        self.running = False
        self.paused  = False
        self.thread  = None
        self._queues = []
        self._lock   = threading.Lock()

    def subscribe(self):
        q = queue.Queue(maxsize=200)
        with self._lock:
            self._queues.append(q)
        return q

    def unsubscribe(self, q):
        with self._lock:
            if q in self._queues:
                self._queues.remove(q)

    def _emit(self, event, data):
        msg = f"event: {event}\ndata: {json.dumps(data)}\n\n"
        with self._lock:
            dead = []
            for q in self._queues:
                try:
                    q.put_nowait(msg)
                except queue.Full:
                    dead.append(q)
            for q in dead:
                self._queues.remove(q)

    def run(self, scenario, speed=1.0):
        if self.running:
            self.stop()
            time.sleep(0.15)
        self.running = True
        self.paused  = False
        self.thread  = threading.Thread(
            target=self._execute, args=(scenario, speed), daemon=True)
        self.thread.start()

    def _sleep(self, seconds, speed):
        steps    = max(1, int(seconds * 20))
        per_step = seconds / steps / max(0.1, speed)
        for _ in range(steps):
            if not self.running:
                return False
            while self.paused and self.running:
                time.sleep(0.05)
            time.sleep(per_step)
        return True

    def _execute(self, scenario, speed):
        stages     = scenario["stages"]
        start_time = time.time()

        self._emit("pipeline_start", {
            "scenario": scenario["id"],
            "title":    scenario["title"],
            "total":    len(stages)
        })

        for idx, stage in enumerate(stages):
            if not self.running:
                break

            self._emit("stage_start", {
                "index":          idx,
                "id":             stage["id"],
                "name":           stage["name"],
                "icon":           stage["icon"],
                "learn":          stage.get("learn", ""),
                "file":           stage.get("file", ""),
                "file_highlight": stage.get("file_highlight", -1)
            })

            for line in stage.get("terminal_lines", []):
                if not self.running:
                    break
                while self.paused and self.running:
                    time.sleep(0.05)
                self._emit("terminal_line", {"line": line, "stage_index": idx})
                self._sleep(line.get("delay", 0.25), speed)

            if not self.running:
                break

            outcome = stage.get("outcome", "pass")
            elapsed = round(time.time() - start_time, 1)

            self._emit("stage_end", {
                "index":        idx,
                "id":           stage["id"],
                "outcome":      outcome,
                "elapsed":      elapsed,
                "fail_message": stage.get("fail_message", ""),
                "fail_learn":   stage.get("fail_learn", "")
            })

            if outcome == "fail":
                self.running = False
                self._emit("pipeline_end", {
                    "outcome": "failed", "stage": stage["name"],
                    "elapsed": elapsed, "stages_done": idx + 1
                })
                return

            self._sleep(0.2, speed)

        if self.running:
            elapsed = round(time.time() - start_time, 1)
            self.running = False
            self._emit("pipeline_end", {
                "outcome": "success", "elapsed": elapsed,
                "stages_done": len(stages)
            })

    def pause(self):
        self.paused = not self.paused
        self._emit("paused", {"paused": self.paused})
        return self.paused

    def stop(self):
        self.running = False
        self.paused  = False
        self._emit("stopped", {})


engine = PipelineEngine()


def load_scenarios():
    path = BASE_DIR / "scenarios" / "scenarios.json"
    with open(path, encoding="utf-8") as f:
        return json.load(f)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/scenarios")
def api_scenarios():
    return jsonify(load_scenarios())


@app.route("/api/scenario/<sid>")
def api_scenario(sid):
    for s in load_scenarios():
        if s["id"] == sid:
            return jsonify(s)
    return jsonify({"error": "not found"}), 404


@app.route("/api/events")
def sse_events():
    q = engine.subscribe()

    def generate():
        yield "data: {\"type\": \"connected\"}\n\n"
        try:
            while True:
                try:
                    msg = q.get(timeout=25)
                    yield msg
                except queue.Empty:
                    yield ": heartbeat\n\n"
        except GeneratorExit:
            pass
        finally:
            engine.unsubscribe(q)

    return Response(
        stream_with_context(generate()),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        }
    )


@app.route("/api/run", methods=["POST"])
def api_run():
    data  = request.get_json()
    sid   = data.get("scenario_id")
    speed = float(data.get("speed", 1.0))
    for s in load_scenarios():
        if s["id"] == sid:
            engine.run(s, speed)
            return jsonify({"ok": True})
    return jsonify({"error": "scenario not found"}), 404


@app.route("/api/pause", methods=["POST"])
def api_pause():
    paused = engine.pause()
    return jsonify({"paused": paused})


@app.route("/api/stop", methods=["POST"])
def api_stop():
    engine.stop()
    return jsonify({"ok": True})


def open_browser():
    time.sleep(1.5)
    webbrowser.open("http://localhost:5050")


if __name__ == "__main__":
    print("=" * 55)
    print("  CI/CD Pipeline Digital Twin")
    print("  http://localhost:5050")
    print("  Press Ctrl+C to stop")
    print("=" * 55)
    threading.Thread(target=open_browser, daemon=True).start()
    app.run(host="0.0.0.0", port=5050, debug=False, threaded=True)
