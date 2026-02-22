from random import Random
from typing import Optional

from player import Player
from spaces.space import Space


class BoardState:
    PASS_GO_BONUS = 200

    def __init__(self, 
                 spaces: list[Space], 
                 property_groups: dict[str, list[int]], 
                 players: list[Player], 
                 random_seed: Optional[int]
                 ):
        self.players = players
        self.curr_turn = 0
        self.property_groups = property_groups
        self.spaces = spaces
        self.random = Random(random_seed)
        self.last_roll = -1

    def next_turn(self):
        curr_player = self.get_curr_player()
        print(f"It is currently {curr_player.name}'s turn. What shall you do?")

        pass

    def roll_dice(self) -> int:
        roll = self.random.randrange(1, 12)
        self.last_roll = roll
        return roll
    
    def move_player_by_dice(self, player_index: int):
        player = self.players[player_index]
        moving_spaces = self.roll_dice()

        passed_go = moving_spaces >= len(self.spaces) 
        next_space = (player.curr_index + moving_spaces) % len(self.spaces)

        if passed_go:
            player.transact(self.PASS_GO_BONUS)
        
        player.set_position(next_space)

    def award_curr_property(self):
        curr_player = self.players[self.curr_turn]
        curr_player.property_idexes_owned.add(curr_player.curr_index)

    def player_has_monopoly(self, player: Player, group: str) -> bool:
        properties_in_group = self.property_groups[group]
        return  self.count_owned_properties_within_group(player, group) == len(properties_in_group)
    
    def count_owned_properties_within_group(self, player: Player, group: str):
        owned_properties = player.property_idexes_owned
        properties_in_group = self.property_groups[group]
        return len(owned_properties.intersection(properties_in_group))
    
    def get_curr_player(self):
        return self.players[self.curr_turn]