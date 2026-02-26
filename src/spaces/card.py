from random import Random

from ..player import Player

from .space import Space


class Card(Space):
    def __init__(self, name: str, rand: Random):
        super().__init__(name)
        self.random = rand

    def land(self, player: Player):
        coin = self.random.randint(0, 1)
        money = 50
        if coin == 1:
            money *= -1
        if not player.transact(money):
            self.board.insufficient_funds_flow(player, -money)

        player.io.provide_info(f"You landed on {self.name}. You {'gained' if coin == 0 else 'lost'} ${money}.")