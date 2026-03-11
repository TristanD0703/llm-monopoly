from dataclasses import dataclass
from flask_socketio import SocketIO
from typing import Any, Optional


from .io.io_data_models import GameStateModel


@dataclass
class Move:
    player_name: str
    action_name: str
    data: dict[str, Any]
    game_state: GameStateModel

    def to_dict(self) -> dict[str, Any]:
        return ({
            "player_name": self.player_name,
            "action_name": self.action_name,
            "data": self.data,
            "game_state": None,
            "game_state": self.game_state.model_dump()
        })


class MoveBroadcaster:
    # Want to use websockets eventually when move is made
    def __init__(self, socket: Optional[SocketIO]):
        self.history: list[dict[str, Any]] = []
        self.socket = socket

    def add_move(self, move: Move):
        move_data = move.to_dict()
        self.history.append(move_data)
        if self.socket is not None:
            self.socket.emit("move", move_data) # type: ignore

    def get_last_ten(self) -> list[dict[str, Any]]:
        return self.history[-10:]
    
    def clear_history(self):
        self.history = []
    
