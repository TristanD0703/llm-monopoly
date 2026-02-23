from .property import BaseProperty

class Railroad(BaseProperty):
    RAILROAD_PROPERTY_GROUP = "railroad"
    def __init__(
                self, 
                 name: str, 
                 price: int, 
                 mortgage_value: int, 
                 rent_costs: list[int], 
                 ):
        super().__init__(name, price, self.RAILROAD_PROPERTY_GROUP, mortgage_value, rent_costs)
    pass

    def get_curr_rent(self) -> int:
        if not self.board:
            raise ValueError("Board not assigned")

        if not self.owned_by:
            raise ValueError("Cannot get rent for railroad before owned")

        railroads_owned: int = self.board.count_owned_properties_within_group(
                self.owned_by, 
                self.RAILROAD_PROPERTY_GROUP
            ) 
        
        return self.rent_costs[railroads_owned-1]