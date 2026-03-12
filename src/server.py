from __future__ import annotations

import os
import threading
from pathlib import Path
from typing import Any

from flask import Flask, request, send_from_directory
from flask_socketio import SocketIO, emit # type: ignore


PROJECT_ROOT = Path(__file__).resolve().parent.parent
PUBLIC_DIR = PROJECT_ROOT / "public"
INDEX_FILE = "index.html"

app = Flask(__name__, static_folder=None)
socketio = SocketIO(app, cors_allowed_origins="*")
_spectators: set[str] = set()
_spectators_lock = threading.Lock()


def _spectator_count() -> int:
    with _spectators_lock:
        return len(_spectators)


def _broadcast_spectator_count():
    socketio.emit(
        "spectator_count",
        {"count": _spectator_count()},
        namespace="/ws",
    )


@app.route("/", defaults={"requested_path": INDEX_FILE})
@app.route("/<path:requested_path>")
def serve_static(requested_path: str):
    requested_file = PUBLIC_DIR / requested_path
    if requested_file.is_file():
        return send_from_directory(PUBLIC_DIR, requested_path)

    index_file = PUBLIC_DIR / INDEX_FILE
    if index_file.is_file():
        return send_from_directory(PUBLIC_DIR, INDEX_FILE)

    return (
        f"Missing static content. Expected files in: {PUBLIC_DIR}",
        404,
    )


@socketio.on("connect", namespace="/ws")
def on_connect():
    with _spectators_lock:
        _spectators.add(request.sid)
    emit("connected", {"message": "Socket connected"})
    _broadcast_spectator_count()


@socketio.on("disconnect", namespace="/ws")
def on_disconnect():
    with _spectators_lock:
        _spectators.discard(request.sid)
    _broadcast_spectator_count()


@socketio.on("ping", namespace="/ws")
def on_ping(payload: dict[Any, Any] | None):
    emit("pong", payload or {})

def start_socket(socket: SocketIO):
    socket.run( #type: ignore
        app,
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", "8080")),
    )

if __name__ == "__main__":
    start_socket(socketio)
