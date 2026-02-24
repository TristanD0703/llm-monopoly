from random import Random
from typing import Optional

from .trade import Trade
from .spaces.property import BaseProperty
from .auction import Auction
from .io.io_data_models import ActionItem, ActionRequest, GameStateModel
from .player import Player
from .spaces.space import Space


class BoardState:
    PASS_GO_BONUS = 200

    def __init__(self, 
                 property_groups: dict[str, list[int]], 
                 random_seed: Optional[int] = None
                 ):

        self.players: list[Player] = [] 
        self.curr_turn = 0
        self.property_groups = property_groups
        self.spaces: list[Space] = [] 
        self.random = Random(random_seed)
        self.last_roll = -1
        self.doubles = 0 
        self.running = True
        self.repeat = False

    def build_action_request(self) -> ActionRequest:
        action_items: list[ActionItem]= []
        curr_player = self.get_curr_player()

        action_items.append(ActionItem(action_name='Roll', description= "Move forward based on dice roll"))
        action_items.append(ActionItem(action_name='Trade', description= "Enter a trade discussion with another player. You can exchange properties and/or money."))
        if len(curr_player.property_idexes_owned) > 0:
            action_items.append(ActionItem(action_name='Mortgage', description= 'Manage your properties\' mortgage states'))

        req = ActionRequest(request=f"It's your turn, {self.get_curr_player().name}! What would you like to do?\n", available_actions=action_items)

        return req

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
        return GameStateModel(player_locations=player_locations, properties_owned=owned, player_banks=banks, last_roll=self.last_roll, doubles_count=self.doubles, previous_player_name=self.get_prev_player().name)

    def next_turn(self):
        while self.running:
            if self.get_curr_player().bankrupt:
                continue

            state = self.build_game_state()
            req = self.build_action_request()
            curr_player = self.get_curr_player()
            res = curr_player.io.request_action(req, state)

            if res.action_name == 'Roll':
                self.move_curr_player_by_dice()
            elif res.action_name == 'Mortgage':
                self.mortgage_properties()
            elif res.action_name == 'Trade':
                self.trade()

            winner = self.check_winner()
            if winner:
                print(f"The winner is {winner.name}!")
                return

            if self.doubles == 0 and not self.repeat: 
                self.curr_turn = (self.curr_turn + 1) % len(self.players)
            elif self.doubles >= 3:
                self.get_curr_player().incarcerate()
                self.doubles = 0

    def check_winner(self) -> Player | None:
        non_bankrupt = None 
        count_bankrupt = 0
        for p in self.players:
            if p.bankrupt:
                count_bankrupt += 1
            else:
                non_bankrupt = p
        
        if count_bankrupt == len(self.players) - 1:
            return non_bankrupt
        return None

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
        player: Player = self.get_curr_player()
        moving_spaces = self.roll_dice()

        passed_go = moving_spaces >= len(self.spaces) 
        next_space = (player.curr_index + moving_spaces) % len(self.spaces)

        if passed_go:
            player.transact(self.PASS_GO_BONUS)
        
        player.set_position(next_space)
        self.spaces[player.curr_index].land(player)

    def award_curr_property(self, target_player: Player, cost: int):
        curr_player = self.get_curr_player()
        if cost:
            target_player.transact(-cost)
        target_player.property_idexes_owned.add(curr_player.curr_index)

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
        if space.name == 'Jail':
            self.jail_index = len(self.spaces)
        self.spaces.append(space)

    def add_player(self, player: Player):
        player.game = self
        self.players.append(player)

    def get_prev_player(self):
        return self.players[(self.curr_turn - 1) % len(self.players)] if self.doubles == 0 else self.get_curr_player()
    
    def start_auction(self, property: BaseProperty | None):
        curr_property = self.get_curr_space()
        if type(curr_property) == BaseProperty:
            property = property if property else curr_property 
            auc = Auction(self.curr_turn)
            auc.property = curr_property
            auc.board = self
            winner, price = auc.run()
            self.award_curr_property(winner, price)
        else: 
            raise ValueError("Cannot auction on non property space")

    def insufficient_funds_flow(self, player: Player, required_amount: int):
        while not player.can_afford(required_amount):
            actions: list[ActionItem] = []
            if len(player.property_idexes_owned) > 0:
                actions.append(ActionItem(action_name="Mortgage properties", description="Mortgage properties to pay what's due"))
            actions.append(ActionItem(action_name="Trade", description="Trade with another player."))
            actions.append(ActionItem(action_name="Declare bankruptcy", description="If you cannot gather enough money to pay, exit the game."))

            req = ActionRequest(request=f"You don't have enough money! You currently have ${player.money}, but you owe ${required_amount}. What will you do to resolve this?", 
                                available_actions=actions)
            res = player.io.request_action(req, game_state=self.build_game_state()) 

            if res.action_name == "Mortgage properties":
                self.mortgage_properties(player)
            elif res.action_name == "Trade":
                self.trade()
            elif res.action_name == "Declare Bankruptcy":
                player.bankrupt = True
                return
            else:
                raise ValueError("Action input not recognized")

        player.transact(-required_amount)

    def prompt_mortgage_list(self, player: Player) -> BaseProperty:
        prop_descs: list[ActionItem] = []
        name_to_prop: dict[str, BaseProperty] = {}
        for prop_i in player.property_idexes_owned:
            prop = self.spaces[prop_i]
            if issubclass(type(prop), BaseProperty):
                name = f"{prop.name} - {prop.property_group}{': MORTGAGED' if prop.is_mortgaged else ''}" # type: ignore
                name_to_prop[name] = prop # type: ignore
                prop_descs.append(ActionItem(action_name=name, description=f"Mortgaging this property will earn you {prop.mortgage_value}")) # type: ignore

        req = ActionRequest(request="Please choose which of your properties to mortgage or unmortgage", available_actions=prop_descs)
        res = player.io.request_action(req)
        return name_to_prop[res.action_name]

    def mortgage_properties(self, player: Player | None=None):
        self.repeat = True
        player = self.get_curr_player() if not player else player
        res = self.prompt_mortgage_list(player)
        if res.toggle_mortage():
            player.io.provide_info(f"You just {'un' if not res.is_mortgaged else ''}mortgaged {res.name} for ${res.mortgage_value}. You now have ${player.money}.")
        else:
            player.io.provide_info(f"Cannot afford to unmortgage {res.name}.")
        pass

    def prompt_target_player_trade(self) -> Player:
        name_actions: list[ActionItem] = []
        name_player: dict[str, Player] = {}
        for p in self.players:
            if p.name == self.get_curr_player().name:
                continue

            name_actions.append(ActionItem(action_name=p.name, description=""))
            name_player[p.name] = p
        req = ActionRequest(request="Who would you like to trade with?", available_actions=name_actions)
        res = self.get_curr_player().io.request_action(req)

        return name_player[res.action_name]

    def trade(self):
        self.repeat = True
        target = self.prompt_target_player_trade()
        t = Trade(self.get_curr_player(), target, self.build_game_state())
        t.begin_trade()
        pass

    def get_curr_space(self) -> Space:
        return self.spaces[self.get_curr_player().curr_index]