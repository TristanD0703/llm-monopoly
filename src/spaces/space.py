from typing import Any

from ..player import Player

class Space:
    board: Any

    def __init__(self, name: str):
        self.name = name

    def land(self, player: Player):
        pass

    def who_owns(self) -> Player | None:
        return None
    