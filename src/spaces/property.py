from board import BoardState
from player import Player
from space import Space


class BaseProperty(Space):
    def __init__(self, 
                 name: str, 
                 price: int, 
                 property_group: str, 
                 mortgage_value: int, 
                 rent_costs: list[int], 
                 board: BoardState
                 ):
        if price <= 0:
            raise ValueError(f"Property must be worth something silly! You put {price}")        

        if mortgage_value <= 0:
            raise ValueError(f"Mortgage value must be worth something silly! You put {price}")        
        
        min_cost = min(rent_costs) 
        if min_cost <= 0:
            raise ValueError(f"Property must have rent prices! You put {min_cost}")        

        self.owned_by: Player | None = None
        self.name = name
        self.price = price
        self.mortgage_value = mortgage_value
        self.rent_costs = rent_costs
        self.board = board
        self.is_mortgaged = False
        self.property_group = property_group

    def land(self, player: Player):
        if not self.owned_by:
            if self.offer_to_buy(player) and player.transact(self.price):
                self.board.award_curr_property()
                self.owned_by = player
            else:
                # TODO: add auctions for denied properties
                raise ValueError("Auctions not ready yet")
        else:
            curr_rent = self.get_curr_rent()
            if not player.transact(-curr_rent):
                # TODO: add actions to reconcile not enough funds
                raise ValueError("User cannot pay rent. Die.")

    def offer_to_buy(self, player: Player) -> bool:
        """Ask player if they want to buy. If they cannot afford or they deny, return false"""
        # TODO: add user prompt for buying properties
        return True
    
    def who_owns(self) -> Player | None:
        return self.owned_by
    
    def mortage(self) -> bool:
        if self.is_mortgaged or not self.owned_by:
            return False
        
        self.is_mortgaged = True
        return self.owned_by.transact(self.mortgage_value)
    

    def get_curr_rent(self) -> int:
        raise NotImplementedError("get_curr_rent not implemented.")