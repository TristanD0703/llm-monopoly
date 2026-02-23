from random import Random
from typing import Any, Callable, Optional

from .io.base_io import BaseIO
from .io.io_data_models import ActionItem, ActionRequest, GameStateModel
from .player import Player
from .spaces.space import Space


class BoardState:
    PASS_GO_BONUS = 200

    def __init__(self, 
                 property_groups: dict[str, list[int]], 
                 io: BaseIO,
                 random_seed: Optional[int]
                 ):

        self.players: list[Player] = [] 
        self.curr_turn = 0
        self.property_groups = property_groups
        self.spaces: list[Space] = [] 
        self.random = Random(random_seed)
        self.last_roll = -1
        self.doubles = 0 
        self.running = True
        self.io = io

    def build_action_request(self) -> ActionRequest:
        actions = self.get_actions_dict()
        action_items: list[ActionItem]= []
        for name, meta in actions.items():
            action_items.append(ActionItem(action_name=name, description=meta['desc'])) # type: ignore
        req = ActionRequest(request=f"It's your turn, {self.get_curr_player().name}! What would you like to do?\n", available_actions=action_items)
        return req

    def get_actions_dict(self) -> dict[str, dict[str, str | Callable[..., Any]]]:
        return  ({
            'roll': {
                'method': self.move_curr_player_by_dice,
                'desc': "Move forward based on dice roll"
            }
        })

    def run_action(self, name: str):
        self.get_actions_dict()[name]['method']() # type: ignore

    def player_locations(self) -> dict[str, str]:
        ret: dict[str, str] = {}
        for player in self.players:
            player_space = self.spaces[player.curr_index]
            ret[player.name] = player_space.name

            try:
                property_group = getattr(player_space, "property_group")
                ret[player.name] += " - " + property_group
            except:
                pass
        return ret
    
    def player_banks(self) -> dict[str, int]:
        ret: dict[str, int] = {}
        for player in self.players:
            ret[player.name] = player.money
        return ret

    def player_properties_owned(self) -> dict[str, list[str]]:
        ret: dict[str, list[str]] = {}

        for player in self.players:
            owned_list: list[str] = []
            for index in player.property_idexes_owned:
                prop = self.spaces[index].name
                owned_list.append(prop)
            ret[player.name] = owned_list

        return ret

    def build_game_state(self) -> GameStateModel:
        player_locations = self.player_locations()
        banks = self.player_banks()
        owned = self.player_properties_owned()
        return GameStateModel(player_locations=player_locations, properties_owned=owned, player_banks=banks, last_roll=self.last_roll, doubles_count=self.doubles)


    def next_turn(self):
        while self.running:
            state = self.build_game_state()
            req = self.build_action_request()
            res = self.io.request_action(req, state)
            self.run_action(res.action_name)
        pass

    def roll_dice(self) -> int:
        roll = self.random.randint(1, 6)
        roll2 = self.random.randint(1, 6)
        combined = roll + roll2

        if roll == roll2:
            self.doubles += 1  
        else:
            self.doubles = 0

        self.last_roll = combined 
        return combined 
    
    def move_curr_player_by_dice(self):
        player = self.get_curr_player()
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
    
    def add_space(self, space: Space):
        space.board = self
        if space.name == 'jail':
            self.jail_index = len(self.spaces)
        self.spaces.append(space)

    def add_player(self, player: Player):
        player.game = self
        self.players.append(player)
