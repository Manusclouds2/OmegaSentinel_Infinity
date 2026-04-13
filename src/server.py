import asyncio
import json
import os
import random
import threading
import time
from http.server import HTTPServer, SimpleHTTPRequestHandler

import websockets

# ---------- Runtime State ----------
state = {
    "activeProtections": 256,
    "threatsNeutralized": 1247,
    "ghostCount": 1_000_000,
    "polymorphicShifts": 894,
    "clients": set(),
    "loputhjosephCommands": [],
    "logs": [],
}


# ---------- Utility Helpers ----------

def make_metrics():
    state["activeProtections"] = max(128, min(1024, state["activeProtections"] + random.randint(-5, 5)))
    state["threatsNeutralized"] += random.randint(0, 3)
    state["ghostCount"] = max(900_000, min(2_000_000, state["ghostCount"] + random.randint(-1000, 1000)))
    state["polymorphicShifts"] = max(100, min(5000, state["polymorphicShifts"] + random.randint(-20, 20)))

    return {
        "type": "metrics",
        "activeProtections": state["activeProtections"],
        "threatsNeutralized": state["threatsNeutralized"],
        "ghostCount": state["ghostCount"],
        "polymorphicShifts": state["polymorphicShifts"],
    }


def make_threat():
    priority = "critical" if random.random() < 0.08 else "normal"
    message = random.choice([
        "Quantum anomaly detected in dimensional fold #{}".format(random.randint(1, 512)),
        "Unauthorized entanglement attempt detected from node {}".format(random.randint(100, 999)),
        "Intrusion signature matched: Specter-{}".format(random.randint(1000, 9999)),
    ])

    return {
        "type": "threat",
        "message": message,
        "source": "Source IP: {}.{}.{}.{}".format(
            random.randint(1, 254), random.randint(1, 254), random.randint(1, 254), random.randint(1, 254)
        ),
        "action": random.choice(["Neutralized via chronos-shift", "quarantined", "rerouted to ghost network"]),
        "priority": priority,
    }


async def broadcast(message: dict):
    if not state["clients"]:
        return

    payload = json.dumps(message)
    dead = []
    for ws in list(state["clients"]):
        try:
            await ws.send(payload)
        except Exception:
            dead.append(ws)

    for ws in dead:
        state["clients"].discard(ws)


async def periodic_broadcast():
    while True:
        await asyncio.sleep(2)
        await broadcast(make_metrics())

        if random.random() < 0.3:
            await broadcast(make_threat())


# ---------- WebSocket Server ----------

async def ws_handler(websocket, path):
    state["clients"].add(websocket)
    await websocket.send(json.dumps({"type": "connected", "message": "LOPUTHJOSEPH WS connected"}))

    try:
        async for message in websocket:
            # Echo back any received message for debugging
            await websocket.send(json.dumps({"type": "echo", "message": message}))
    finally:
        state["clients"].discard(websocket)


# ---------- HTTP API Server ----------

class APIServerHandler(SimpleHTTPRequestHandler):
    def _send_json(self, data, status=200):
        payload = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def do_GET(self):
        if self.path in ["/", "/dashboard.html"]:
            self.path = "/dashboard.html"
        return super().do_GET()

    def do_POST(self):
        length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(length).decode("utf-8")
        try:
            data = json.loads(body) if body else {}
        except Exception:
            data = {}

        if self.path == "/api/omega/execute":
            cmd = data.get("command")
            state["omegaCommands"].append({"command": cmd, "timestamp": time.time()})
            return self._send_json({"status": "success", "command": cmd, "executedAt": time.time()})

        if self.path == "/api/omega/protocol/activate":
            level = data.get("level", "maximum")
            return self._send_json({"status": "activated", "level": level, "timestamp": time.time()})

        if self.path == "/api/omega/scan/global":
            return self._send_json({"status": "scan_initiated", "estimatedSeconds": 3.2})

        if self.path == "/api/chronos/shift":
            return self._send_json({"status": "shifted", "mode": data.get("mode"), "speed": data.get("speed")})

        if self.path == "/api/omega/self-destruct":
            code = data.get("code")
            if code == "478236915032":
                return self._send_json({"status": "self_destruct_initiated"})
            return self._send_json({"status": "invalid_code"}, status=400)

        if self.path == "/api/security/log":
            state["logs"].append({"event": data.get("event"), "timestamp": time.time(), "details": data})
            return self._send_json({"status": "ok"})

        self.send_response(404)
        self.end_headers()


def run_http_server(port=80):
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    httpd = HTTPServer(("0.0.0.0", port), APIServerHandler)
    print(f"HTTP server listening on http://0.0.0.0:{port}")
    httpd.serve_forever()


async def main():
    ws_server = await websockets.serve(ws_handler, "0.0.0.0", 8001)
    print("WebSocket server listening on ws://0.0.0.0:8001")

    broadcast_task = asyncio.create_task(periodic_broadcast())

    await ws_server.wait_closed()
    await broadcast_task


if __name__ == "__main__":
    threading.Thread(target=run_http_server, daemon=True).start()
    asyncio.run(main())
