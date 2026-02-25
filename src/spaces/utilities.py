from ..spaces.property import BaseProperty

class Utlities(BaseProperty):
    UTILITY_PROPERTY_GROUP = "utilities"
    def __init__(self, 
                 name: str, 
                 price: int, 
                 mortgage_value: int, 
                 ):

        super().__init__(name, price, self.UTILITY_PROPERTY_GROUP, mortgage_value, [])

    def get_curr_rent(self) -> int:
        if not self.board:
            raise ValueError("Board not defined")

        if not self.owned_by:
            raise ValueError("Cannot get utility rent if not owned")

        multiplier = 4
        if self.name in self.board.player_monopolies(self.owned_by, self.property_group):
            multiplier = 10

        return self.board.last_roll * multiplier