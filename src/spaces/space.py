from typing import Any

from ..move_broadcaster import MoveBroadcaster

from ..player import Player

class Space:
    board: Any

    def __init__(self, name: str):
        self.name = name

    def land(self, player: Player, broadcaster: MoveBroadcaster):
        pass

    def who_owns(self) -> Player | None:
        return None
    