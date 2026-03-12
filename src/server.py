from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from flask import Flask, send_from_directory
from flask_socketio import SocketIO, emit # type: ignore


PROJECT_ROOT = Path(__file__).resolve().parent.parent
PUBLIC_DIR = PROJECT_ROOT / "public"
INDEX_FILE = "index.html"

app = Flask(__name__, static_folder=None)
socketio = SocketIO(app, cors_allowed_origins="*")


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
    emit("connected", {"message": "Socket connected"})


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