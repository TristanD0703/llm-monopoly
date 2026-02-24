from typing import Any

from .io.io_data_models import ActionRequest
from .player import Player


class Auction:
    def __init__(self, curr_player: int):
        self.curr_player_index = curr_player
        self.curr_price = 0
        self.board: Any = None
        self.auctioning = True
        self.curr_winner = None
        self.players_dropped: set[int] = set()
        self.property: Any = None 


    def run(self) -> tuple[Player, int]:
        while not self.is_over():
            curr_player = self.get_curr_player()

            if self.curr_player_index in self.players_dropped or not curr_player.can_afford(self.curr_price):
                self.curr_player_index += 1
                continue

            req = ActionRequest(request=f"You're currently in an auction for the property {self.property.name} - {self.property.property_group}, {curr_player.name}. Current winner is {self.curr_winner.name if self.curr_winner else 'no one'}. Highest price is ${self.curr_price}. You currently have ${curr_player.money}. How much do you bid on top of this? Enter <= 0 or over ${curr_player.money - self.curr_price} to exit the auction", 
                        available_actions=[], 
                        input_type='Int')

            res = curr_player.io.request_action_int(req)
            if res.number > 0 and curr_player.can_afford(res.number + self.curr_price):
                self.curr_price += res.number 
                self.curr_winner = curr_player
            else:
                self.players_dropped.add(self.curr_player_index)
            self.curr_player_index += 1

        if not self.curr_winner:
            raise ValueError("Auction ended with no winner?")
        print(f"AUCTION RETURNED PRICE {self.curr_price}") 
        return self.curr_winner, self.curr_price

    def get_curr_player(self) -> Player:
        players = self.board.players 
        return players[self.curr_player_index % len(players)]
    
    def is_over(self):
        return len(self.board.players) - 1 == len(self.players_dropped)