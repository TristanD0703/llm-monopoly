from __future__ import annotations
from typing import Any

from .io.base_io import BaseIO

class Player:
    def __init__(self, name: str, io: BaseIO, initial_money: int=1500, max_jail_rolls: int=3, jail_release_cost: int=50):
        self.money = initial_money
        self.jail_release_cost = jail_release_cost
        self.max_jail_rolls = max_jail_rolls
        self.property_idexes_owned: set[int] = set()
        self.curr_index = 0
        self.is_in_jail = False
        self.name = name
        self.id = id
        self.bankrupt = False
        self.game: Any = None 
        self.io = io
        self.jail_rolls = 0

    def set_position(self, pos: int) -> bool:
        if not self.is_in_jail:
            self.curr_index = pos
            return True

        self.jail_rolls += 1
        if self.jail_rolls == self.max_jail_rolls:
            self.io.provide_info(f"You failed to roll doubles {self.jail_rolls} times. You had to pay ${self.jail_release_cost} to escape.")
            self.curr_index = pos
            if not self.transact(-self.jail_release_cost):
                self.money = 0
            self.is_in_jail = False
            return True

        return False

    def remove_properties(self, props: list[int]):
        self.property_idexes_owned -= set(props)
        pass

    def add_properties(self, props: list[int]):
        self.property_idexes_owned = self.property_idexes_owned.union(set(props))
        pass

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

    def name_to_property_index(self, name: str) -> int:
        for i in self.property_idexes_owned:
            rel_prop = self.game.spaces[i]
            if rel_prop.name == name:
                return i
        return -1