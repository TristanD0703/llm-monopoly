from dataclasses import dataclass
from typing import Any 


from .io.io_data_models import GameStateModel


@dataclass
class Move:
    player_name: str
    action_name: str
    reason: str
    data: dict[str, Any]
    game_state: GameStateModel | None = None

    def to_dict(self) -> dict[str, Any]:
        res: dict[str, Any] = ({
            "player_name": self.player_name,
            "action_name": self.action_name,
            "data": self.data,
            "game_state": None,
        })
        if self.game_state:
            res["game_state"] = self.game_state.model_dump()
        return res

class Receiver:
    def on_move(self, event: dict[str, Any]):
        pass


class MoveBroadcaster:
    # Want to use websockets eventually when move is made
    def __init__(self, listeners: list[Receiver] = []):
        self.history: list[dict[str, Any]] = []
        self.listeners = listeners

    def emit(self, move: dict[str, Any]):
        for l in self.listeners:
            l.on_move(move)

    def add_move(self, move: Move):
        move_data = move.to_dict()
        self.history.append(move_data)
        self.emit(move_data) 

    def get_history(self):
        return self.history
    
    def add_listener(self, listener: Receiver):
        self.listeners.append(listener)
    
    def clear_history(self):
        self.history = []
    
