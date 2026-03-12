from ..move_broadcaster import MoveBroadcaster

from ..player import Player
from ..spaces.space import Space


class Jail(Space):
    def __init__(self, name: str):
        super().__init__(name)

    def land(self, player: Player, broadcaster: MoveBroadcaster):
        player.incarcerate()