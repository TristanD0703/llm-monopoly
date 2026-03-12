from typing import Any

from .move_broadcaster import Move, MoveBroadcaster

from .io.io_data_models import ActionRequest
from .player import Player


class Auction:
    def __init__(self, curr_player: int, broadcaster: MoveBroadcaster):
        self.broadcaster = broadcaster
        self.curr_player_index = curr_player
        self.curr_price = 0
        self.board: Any = None
        self.auctioning = True
        self.curr_winner = None
        self.players_dropped: set[int] = set()
        self.property: Any = None 


    def run(self) -> tuple[Player, int]:
        move_data = Move(self.get_curr_player().name, 'begin_trade', "", {})
        self.broadcaster.add_move(move_data)

        while not self.is_over():
            curr_player = self.get_curr_player()
            if not self.curr_winner and curr_player.money > 0:
                self.curr_winner = curr_player

            if not curr_player.can_afford(self.curr_price):
                self.drop_player(self.curr_player_index)

            if self.curr_player_index in self.players_dropped:
                self.advance()
                continue

            req = ActionRequest(
                        request=f"You're currently in an auction for the property {self.property.name} - {self.property.property_group}, {curr_player.name}. Current winner is {self.curr_winner.name if self.curr_winner else 'no one'}. Highest price is ${self.curr_price}. You currently have ${curr_player.money}. How much do you bid on top of this? Enter <= 0 or over ${curr_player.money - self.curr_price} to exit the auction", 
                        available_actions=[], 
                        input_type='Int')

            res = curr_player.io.request_action_int(req, self.broadcaster)
            if res.number > 0 and curr_player.can_afford(res.number + self.curr_price):
                self.curr_price += res.number 
                self.curr_winner = curr_player
                move_data = Move(curr_player.name, 'raise_auction_bid', res.explanation, {'amount': res.number, 'total': self.curr_price})
                self.broadcaster.add_move(move_data)
            else:
                self.drop_player(self.curr_player_index)
            self.advance()

        if not self.curr_winner:
            raise ValueError("Auction ended with no winner?")
        return self.curr_winner, self.curr_price

    def get_player(self, index: int):
        players = self.board.players 
        return players[index % len(players)]

    def get_curr_player(self) -> Player:
        return self.get_player(self.curr_player_index)

    def advance(self):
        self.curr_player_index = (self.curr_player_index + 1) % len(self.board.players)

    def is_over(self):
        return len(self.board.players) - 1 == len(self.players_dropped)
    
    def drop_player(self, index: int):
        self.players_dropped.add(index)
        move_data = Move(self.get_player(index).name, 'player_drop_auction', 'player dropped', {})
        self.broadcaster.add_move(move_data)
        