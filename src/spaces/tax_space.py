from ..player import Player
from .space import Space


class TaxSpace(Space):
    def __init__(self, cost: int, name: str):
        super().__init__(name)
        self.cost = cost

    def land(self, player: Player):
        if not player.transact(-self.cost):
            # TODO: Add flow for resolving insufficient funds
            raise ValueError(f"Cannot pay taxes. IRS killed player {player.name}")