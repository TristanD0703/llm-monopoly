from board import BoardState
from spaces.property import BaseProperty

class Utlities(BaseProperty):
    UTILITY_PROPERTY_GROUP = "utilities"
    def __init__(self, 
                 name: str, 
                 price: int, 
                 property_group: str, 
                 mortgage_value: int, 
                 rent_costs: list[int], 
                 board: BoardState
                 ):

        super().__init__(name, price, property_group, mortgage_value, rent_costs, board)

    def get_curr_rent(self) -> int:
        if not self.owned_by:
            raise ValueError("Cannot get utility rent if not owned")

        multiplier = 4
        if self.board.player_has_monopoly(self.owned_by, self.UTILITY_PROPERTY_GROUP):
            multiplier = 10

        return self.board.last_roll * multiplier