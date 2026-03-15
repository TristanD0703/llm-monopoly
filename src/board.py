from random import Random
from time import sleep
from typing import Optional

from .move_broadcaster import Move, MoveBroadcaster

from .spaces.normal_property import NormalProperty

from .trade import Trade
from .spaces.property import BaseProperty
from .auction import Auction
from .io.io_data_models import (
    ActionItem,
    ActionRequest,
    GameStateModel,
    PropertyStateModel,
)
from .player import Player
from .spaces.space import Space

MAX_PLAYER_REPITITIONS = 3 

class BoardState:
    PASS_GO_BONUS = 200

    def __init__(self, 
                 broadcaster: MoveBroadcaster,
                 property_groups: dict[str, list[int]] = {}, 
                 random_seed: Optional[int] = None,
                 time_between: float = 5,
                 force_trades_if_no_monopoly: tuple[bool, int] = (False, 0)
                 ):
        self.broadcaster = broadcaster
        self.players: list[Player] = [] 
        self.curr_turn = 0
        self.property_groups = property_groups
        self.spaces: list[Space] = [] 
        self.random = Random(random_seed)
        self.turn_count = 0
        self.last_roll = -1
        self.doubles = 0 
        self.running = True
        self.repeat = False
        self.time_between = time_between
        self.forcing_trades, self.force_trade_turn = force_trades_if_no_monopoly


    def build_action_request(self) -> ActionRequest:
        action_items: list[ActionItem]= []
        curr_player = self.get_curr_player()

        if self.forcing_trades and not (self.turn_count > self.force_trade_turn and self.count_player_monopolies() == 0):
            action_items.append(ActionItem(action_name='Roll', description= "Move forward based on dice roll"))
        elif self.forcing_trades:
            curr_player.io.provide_info("The game has gone too long without a monopoly. Please make a trade with a player that will earn you a monopoly.") 
            self.broadcaster.add_move(Move(curr_player.name, 'forcing_trade', 'Too many turns without monopoly', {}))
        
        action_items.append(ActionItem(action_name='Trade', description= "Enter a trade discussion with another player. You can exchange properties and/or money."))
        if len(curr_player.property_indexes_owned) > 0:
            action_items.append(ActionItem(action_name='Mortgage', description= 'Manage your properties\' mortgage states'))
            if self.player_monopolies(self.get_curr_player()):
                action_items.append(ActionItem(action_name="Manage houses", description="Buy or sell houses on properties within a monopoly"))

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
            for index in player.property_indexes_owned:
                prop = self.spaces[index]
                res = prop.name
                if hasattr(prop, "property_group"):
                    res += f" - {getattr(prop, 'property_group')}"
                owned_list.append(res)
            ret[player.name] = owned_list

        return ret

    def property_state(self) -> dict[str, PropertyStateModel]:
        ret: dict[str, PropertyStateModel] = {}
        for space in self.spaces:
            if not hasattr(space, "owned_by"):
                continue

            houses = getattr(space, "house_count", 0)
            mortgaged = getattr(space, "is_mortgaged", False)
            ret[space.name] = PropertyStateModel(
                houses=houses,
                mortgaged=mortgaged,
            )
        return ret

    def build_game_state(self) -> GameStateModel:
        player_locations = self.player_locations()
        banks = self.player_banks()
        owned = self.player_properties_owned()
        property_state = self.property_state()
        return GameStateModel(player_locations=player_locations, properties_owned=owned, property_state=property_state, player_banks=banks, turn_count=self.turn_count, last_roll=self.last_roll, doubles_count=self.doubles, previous_player_name=self.get_prev_player().name)

    def next_turn(self):
        names: list[str] = []
        for p in self.players:
            names.append(p.name)
        move_data = Move('system', 'begin_game', '', {'players': list(names)})
        self.broadcaster.add_move(move_data)

        repititions = 0
        while self.running:
            sleep(self.time_between)

            continuing_turn = self.repeat
            self.repeat = False
            if self.get_curr_player().bankrupt:
                self.advance_turn()
                continue

            if not continuing_turn:
                self.turn_count += 1

            state = self.build_game_state()
            req = self.build_action_request()
            curr_player = self.get_curr_player()

            if repititions > MAX_PLAYER_REPITITIONS:
                curr_player.io.provide_info("Too many repeated turns, rolling and advancing.")
                self.move_curr_player_by_dice()
                self.advance_turn()
                repititions = 0
                continue

            res = curr_player.io.request_action(req, self.broadcaster, state)

            if res.action_name == 'Roll':
                self.move_curr_player_by_dice()
            elif res.action_name == 'Mortgage':
                self.mortgage_properties()
            elif res.action_name == 'Trade':
                self.trade()
            elif res.action_name == "Manage houses":
                self.manage_houses()

            winner = self.check_winner()
            if winner:
                print(f"The winner is {winner.name}!")
                move_data = Move("system", "game_over", "", {'winner': winner.name}, self.build_game_state())
                self.broadcaster.add_move(move_data)
                return

            if self.doubles >= 3:
                curr_player.incarcerate(self.broadcaster)
                self.doubles = 0

            repititions += 1
            if not self.repeat and self.doubles == 0:
                repititions = 0
                self.advance_turn()
            
        move_data = Move("system", "game_over", "", data={}, game_state=self.build_game_state())
        self.broadcaster.add_move(move_data)
        
    def advance_turn(self):
        self.curr_turn = (self.curr_turn + 1) % len(self.players)

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
            self.get_curr_player().is_in_jail = False
        else:
            self.doubles = 0

        self.last_roll = combined 
        return combined 
    
    def move_curr_player_by_dice(self):
        player: Player = self.get_curr_player()
        moving_spaces = self.roll_dice()

        passed_go = player.curr_index + moving_spaces >= len(self.spaces) 
        next_space = (player.curr_index + moving_spaces) % len(self.spaces)

        if passed_go:
            player.transact(self.PASS_GO_BONUS)
        
        player.set_position(next_space)
        move_data = Move(
            player_name=player.name, 
            action_name='dice_roll', 
            game_state=self.build_game_state(), 
            data={'roll_number': moving_spaces, 'is_doubles': self.doubles > 0},
            reason=""
            )

        self.broadcaster.add_move(move_data)
        self.spaces[player.curr_index].land(player, self.broadcaster)

    def award_curr_property(self, target_player: Player, cost: int):
        curr_player = self.get_curr_player()
        if cost:
            target_player.transact(-cost)
        target_player.property_indexes_owned.add(curr_player.curr_index)

        curr_space = self.get_curr_space()
        move_data = Move(target_player.name, 'purchase_property', '', {'name': curr_space.name}, self.build_game_state())
        self.broadcaster.add_move(move_data)

    def player_monopolies(self, player: Player) -> set[str]:
        monopoly_names: set[str]= set() 
        for name, props in self.property_groups.items():
            if self.count_owned_properties_within_group(player, name) == len(props):
                monopoly_names.add(name)
        return monopoly_names

    def count_player_monopolies(self) -> int:
        count = 0
        for player in self.players:
            if self.player_monopolies(player):
                count += 1
        return count
    
    def count_owned_properties_within_group(self, player: Player, group: str):
        owned_properties = player.property_indexes_owned
        properties_in_group = self.property_groups[group]
        return len(owned_properties.intersection(properties_in_group))
    
    def get_curr_player(self) -> Player:
        return self.players[self.curr_turn]
    
    def add_space(self, space: Space):
        space.board = self
        if space.name == 'Jail':
            self.jail_index = len(self.spaces)

        if hasattr(space, 'property_group'):
            prop_grp = getattr(space, 'property_group') 
            if prop_grp not in self.property_groups:
                self.property_groups[prop_grp] = []
            self.property_groups[prop_grp].append(len(self.spaces))
        self.spaces.append(space)

    def add_player(self, player: Player):
        player.game = self
        self.players.append(player)

    def get_prev_player(self):
        return self.players[(self.curr_turn - 1) % len(self.players)] if self.doubles == 0 else self.get_curr_player()
    
    def start_auction(self, property: BaseProperty | None):
        curr_property = self.get_curr_space()
        if issubclass(type(curr_property), BaseProperty):
            property = property if property else curr_property # type: ignore
            auc = Auction(self.curr_turn, self.broadcaster)
            auc.property = curr_property
            auc.board = self
            winner, price = auc.run()
            self.award_curr_property(winner, price)
        else: 
            raise ValueError("Cannot auction on non property space")

    def insufficient_funds_flow(self, player: Player, required_amount: int):
        move_data = Move(player.name, "insufficient_funds", '', {'required_amount': required_amount}, self.build_game_state())
        self.broadcaster.add_move(move_data)

        while not player.can_afford(required_amount):
            actions: list[ActionItem] = []
            if len(player.property_indexes_owned) > 0:
                actions.append(ActionItem(action_name="Mortgage properties", description="Mortgage properties to pay what's due"))
            actions.append(ActionItem(action_name="Trade", description="Trade with another player."))
            actions.append(ActionItem(action_name="Declare bankruptcy", description="If you cannot gather enough money to pay, exit the game."))

            req = ActionRequest(request=f"You don't have enough money! You currently have ${player.money}, but you owe ${required_amount}. What will you do to resolve this?", 
                                available_actions=actions)
            res = player.io.request_action(req, self.broadcaster, game_state=self.build_game_state()) 

            if res.action_name == "Mortgage properties":
                self.mortgage_properties(player)
            elif res.action_name == "Trade":
                self.trade()
            elif res.action_name == "Declare bankruptcy":
                player.bankrupt = True

                move_data = Move(player.name, 'declare_bankruptcy', res.explanation, data={}, game_state=self.build_game_state())
                self.broadcaster.add_move(move_data)

                if hasattr(self.get_curr_space(), "owned_by"):
                    owned_by = getattr(self.get_curr_space(), "owned_by")
                    owned_by.add_properties(player.property_indexes_owned)
                    owned_by.transact(player.money)
                    player.property_indexes_owned = set()
                    player.money = 0
                return
            else:
                raise ValueError("Action input not recognized")

        move_data = Move(player.name, "insufficient_funds_resolved", '', data={}, game_state=self.build_game_state())
        self.broadcaster.add_move(move_data)
        player.transact(-required_amount)
        self.repeat = False

    def prompt_mortgage_list(self, player: Player) -> tuple[BaseProperty, str]:
        prop_descs: list[ActionItem] = []
        name_to_prop: dict[str, BaseProperty] = {}
        for prop_i in player.property_indexes_owned:
            prop = self.spaces[prop_i]
            if issubclass(type(prop), BaseProperty):
                name = f"{prop.name} - {prop.property_group} - ${prop.mortgage_value}{': MORTGAGED' if prop.is_mortgaged else ''}" # type: ignore
                name_to_prop[name] = prop # type: ignore
                prop_descs.append(ActionItem(action_name=name, description=f"Mortgaging this property will earn you {prop.mortgage_value}")) # type: ignore

        req = ActionRequest(request="Please choose which of your properties to mortgage or unmortgage", available_actions=prop_descs)
        res = player.io.request_action(req, self.broadcaster)
        return name_to_prop[res.action_name], res.explanation

    def mortgage_properties(self, player: Player | None=None):
        self.repeat = True
        player = self.get_curr_player() if not player else player
        res, exp = self.prompt_mortgage_list(player)
        if res.toggle_mortgage():
            player.io.provide_info(f"You just {'un' if not res.is_mortgaged else ''}mortgaged {res.name} for ${res.mortgage_value}. You now have ${player.money}.")
            move_data = Move(player.name, "toggle_mortgage", exp, {'name': res.name}, self.build_game_state())
            self.broadcaster.add_move(move_data)
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
        res = self.get_curr_player().io.request_action(req, self.broadcaster)

        return name_player[res.action_name]

    def trade(self):
        self.repeat = True
        target = self.prompt_target_player_trade()
        t = Trade(self.get_curr_player(), target, self.build_game_state(), self.broadcaster)
        t.begin_trade()
        pass

    def get_curr_space(self) -> Space:
        return self.spaces[self.get_curr_player().curr_index]

    def prompt_property_houses(self, props: list[Space], is_purchasing: bool) -> tuple[NormalProperty, str]:
        actions: list[ActionItem] = []
        for p in props:
            if is_purchasing and hasattr(p, 'can_purchase_house'):
                if not p.can_purchase_house(): # type: ignore
                    continue

            if hasattr(p, 'house_count'):
                count = getattr(p, 'house_count') 
                actions.append(ActionItem(action_name=p.name, description=f"Currently has {count} houses")) 

        req = ActionRequest(request="Choose a property to buy houses for:", available_actions=actions)
        res = self.get_curr_player().io.request_action(req, self.broadcaster)
        
        for p in props:
            if p.name == res.action_name:
                return p, res.explanation # type: ignore
        raise ValueError("request_action returned an invalid option")

    def manage_houses(self):
        self.repeat = True
        curr_player = self.get_curr_player()
        groups = self.player_monopolies(curr_player)

        monopoly_properties: list[Space]= []
        for g in groups:
            monopoly_properties.extend(list(map(lambda x: self.spaces[x], self.property_groups[g])))

        method = curr_player.io.request_action(ActionRequest(
            available_actions=[ActionItem(action_name="Buy", description=""), ActionItem(action_name="Sell", description="")],
            request="Buy or sell?"
        ), self.broadcaster)

        chosen, reason = self.prompt_property_houses(monopoly_properties, method.action_name=="Buy")
        count = curr_player.io.request_action_int(broadcaster=self.broadcaster, options=ActionRequest(request="How many houses do you wish to purchase/sell?", available_actions=[]))

        if count.number < 0:
            return

        event_name = f"{method.action_name.lower()}_houses"
        actual_count = 0
        for _ in range(count.number):
            if method.action_name == "Buy" and not chosen.add_house():
                curr_player.io.provide_info("Could not buy house. Could not afford.")
            elif not chosen.sell_house():
                curr_player.io.provide_info("Could not sell house. No houses to sell!")
            actual_count += 1

        move_data = Move(curr_player.name, event_name, reason, {'property_name': chosen.name, 'count': count.number}, self.build_game_state())
        self.broadcaster.add_move(move_data)
