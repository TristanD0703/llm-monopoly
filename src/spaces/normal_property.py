from board import BoardState
from property import BaseProperty

class NormalProperty(BaseProperty):
    def __init__(
                self, 
                 name: str, 
                 price: int, 
                 property_group: str, 
                 mortgage_value: int, 
                 house_cost: int, 
                 rent_costs: list[int], 
                 board: BoardState
                 ):
        if house_cost <= 0:
            raise ValueError(f"Houses must be worth something silly! You put {price}")        

        super().__init__(name, price, property_group, mortgage_value, rent_costs, board)
        self.property_group = property_group
        self.house_cost = house_cost
        self.house_count = 0
        pass

    def add_house(self):
        if (self.owned_by and 
            self.board.player_has_monopoly(self.owned_by, self.property_group) and 
            self.owned_by.transact(-self.house_cost)
            ):
            self.house_count += 1
            return True
        return False
            
    def sell_house(self):
        if self.house_count > 0 and self.owned_by:
            self.owned_by.transact(self.house_cost)
            self.house_count -= 1
            return True
        return False
    
    def get_curr_rent(self) -> int:
        return self.rent_costs[self.house_count]