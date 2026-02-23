from __future__ import annotations
from typing import Any, Optional

from .io.base_io import BaseIO

class Player:
    def __init__(self, name: str, id: int, io: BaseIO, initial_money: int=1500):
        self.money = initial_money
        self.property_idexes_owned: set[int] = set()
        self.curr_index = 0
        self.is_in_jail = False
        self.name = name
        self.id = id
        self.bankrupt = False
        self.game: Any = None 
        self.io = io

    def set_position(self, pos: int) -> bool:
        if not self.is_in_jail:
            self.curr_index = pos
            return True
        return False

    def trade(self, other: Player, money: Optional[int], properties: Optional[set[int]]):
        """Transfer assets from this player to the other player"""
        if properties:
            self.property_idexes_owned ^= properties
            other.property_idexes_owned ^= properties
        
        if money:
            self.transact(money)
            other.transact(money)

    def transact(self, money: int) -> bool:
        if self.money + money < 0:
            return False

        self.money += money
        return True
    
    def incarcerate(self):
        if not self.game:
            raise ValueError("Board not defined")

        self.is_in_jail = True
        self.curr_index: int = self.game.jail_index

    def release(self):
        self.is_in_jail = False

    def can_afford(self, amount: int):
        return self.money - amount >= 0
