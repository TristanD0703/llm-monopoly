from ..auction import Auction

from ..io.base_io import BaseIO

from ..io.io_data_models import ActionInput, ActionItem, ActionRequest

from ..player import Player
from .space import Space


class BaseProperty(Space):
    def __init__(self, 
                 name: str, 
                 price: int, 
                 property_group: str, 
                 mortgage_value: int, 
                 rent_costs: list[int], 
                 ):
        super().__init__(name)
        if price <= 0:
            raise ValueError(f"Property must be worth something silly! You put {price}")        

        if mortgage_value <= 0:
            raise ValueError(f"Mortgage value must be worth something silly! You put {price}")        


        if len(rent_costs) > 0:
            min_cost = min(rent_costs)
            if min_cost <= 0:
                raise ValueError(f"Property must have rent prices! You put {min_cost}")        

        self.owned_by: Player | None = None
        self.price = price
        self.mortgage_value = mortgage_value
        self.rent_costs = rent_costs
        self.board = None 
        self.is_mortgaged = False
        self.property_group = property_group

    def land(self, player: Player):
        if not self.board:
            raise ValueError("Board not assigned.")

        if not self.owned_by:
            if player.can_afford(self.price) and self.offer_to_buy(player.io):
                self.board.award_curr_property(player, self.price)
                self.owned_by = player
            else:
                auc = Auction(self.board.curr_turn)
                auc.board = self.board
                auc.property = self
                winner, cost = auc.run()
                self.board.award_curr_property(winner, cost)
                self.owned_by = winner
        else:
            curr_rent = self.get_curr_rent()
            if not player.transact(-curr_rent):
                self.board.insufficient_funds_flow(player, curr_rent)
            self.owned_by.transact(curr_rent)
            player.io.provide_info(f"You just landed on {self.owned_by.name}'s space! You had to pay ${curr_rent}.")

    def offer_to_buy(self, io: BaseIO) -> bool:
        """Ask player if they want to buy. If they cannot afford or they deny, return false"""

        req = ActionRequest(available_actions=[
                ActionItem(action_name="Purchase", description="Purchase the property so that you now own it. Subtracts cost from your balance."),
                ActionItem(action_name="Auction", description="Allows yourself and other players to compete for the property. Highest payer wins.")
            ], request=f"You just rolled a {self.board.last_roll} and landed on {self.name} - {self.property_group}, which no one owns yet. It costs ${self.price} What would you like to do?")

        res = io.request_action(req, None)

        if type(res) == ActionInput and res.action_name == "Purchase":
            return True
        return False 
    
    def who_owns(self) -> Player | None:
        return self.owned_by
    
    def toggle_mortage(self) -> bool:
        if not self.owned_by:
            return False

        transaction = self.mortgage_value
        if self.is_mortgaged:
            transaction *= -1

        if self.owned_by.transact(transaction):
            self.is_mortgaged = not self.is_mortgaged
            return True
        return False
    

    def get_curr_rent(self) -> int:
        raise NotImplementedError("get_curr_rent not implemented.")