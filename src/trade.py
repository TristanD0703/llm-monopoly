from .move_broadcaster import Move, MoveBroadcaster

from .io.io_data_models import ActionInput, ActionInputTrade, ActionItem, ActionRequest, GameStateModel
from .player import Player

class Trade:
    def __init__(self, player: Player, target_player: Player, game_state: GameStateModel, broadcaster: MoveBroadcaster, max_counteroffers: int=10):
        self.broadcaster = broadcaster
        self.players: list[tuple[Player, bool]] = [(player, True), (target_player, False)]
        self.game_state = game_state
        self.curr_turn = 0
        self.counter_times = 0
        self.max_counteroffers = max_counteroffers

    def prompt_trade_details(self) -> ActionInputTrade:
        req = ActionRequest(request="Please enter the details of your trade deal", available_actions=[])
        curr_player = self.get_curr_player() 
        curr_io = curr_player.io
        other_player = self.get_other_player()
        res = curr_io.request_trade_details(req, self.game_state, curr_player.name, other_player.name, broadcaster=self.broadcaster)

        while res.amount > curr_player.money or res.amount_receiving > other_player.money:
            curr_player.io.provide_info("Players cannot afford to trade that amount of money.")
            res = curr_io.request_trade_details(req, self.game_state, curr_player.name, other_player.name, self.broadcaster)
        return res

    def prompt_receive_offer(self, to_player: Player, from_player: Player, details: ActionInputTrade) -> ActionInput:
        mes = to_player.io.trade_details_message(details)
        actions: list[ActionItem] = [
            ActionItem(action_name="Accept", description="Accepts the trade and enacts all the proposed deals"),
            ActionItem(action_name="Counteroffer", description="Make another offer to the other player"),
            ActionItem(action_name="Decline", description="Stop the trading process.")
        ]
        req = ActionRequest(request=f"You received an offer from {from_player.name}! Here are the details:\n{mes}\nWhat will you do?", available_actions=actions)

        return to_player.io.request_action(req, self.broadcaster, self.game_state)

    def begin_trade(self):
        details = self.prompt_trade_details()

        move_data = Move(
            self.players[0][0].name, 
            'begin_trade', details.reason, 
            {
                'other_player_name': self.players[1][0].name,
                'details': details.model_dump()
            })
        self.broadcaster.add_move(move_data)
        self.curr_turn += 1
        while not self.is_deal_end():
            curr_player, _ = self.players[self.curr_turn]
            other_player, _ = self.players[self.get_next()]

            res = self.prompt_receive_offer(curr_player, other_player, details)
            if res.action_name == "Accept":
                move_data = Move(curr_player.name, 'accept_trade', res.explanation, {})
                self.broadcaster.add_move(move_data)
                self.enact_deal(details)
                self.players[self.curr_turn] = curr_player, True
                return
            elif res.action_name == "Counteroffer":
                details = self.prompt_trade_details()
            elif res.action_name == "Decline":
                move_data = Move(curr_player.name, 'decline_trade', res.explanation, {})
                self.broadcaster.add_move(move_data)
                return

            move_data = Move(curr_player.name, 'counteroffer', details.reason, {'other_player_name': self.players[1][0], 'details': details.model_dump()})
            self.broadcaster.add_move(move_data)
            self.counter_times += 1
            self.curr_turn = self.get_next()
        self.players[0][0].io.provide_info("Trade cancelled due to too many counteroffers.")

    def is_deal_end(self) -> bool:
        all_accepted = True
        for _, accepted in self.players:
            if not accepted:
                all_accepted = False
                break
        
        return all_accepted or self.counter_times >= self.max_counteroffers
    
    def get_next(self) -> int:
        return (self.curr_turn + 1) % 2

    def get_curr_player(self) -> Player:
        return self.players[self.curr_turn][0]

    def get_other_player(self) -> Player:
        return self.players[self.get_next()][0]

    def enact_deal(self, deal: ActionInputTrade):
        other_player = self.get_curr_player() 
        curr_player = self.get_other_player() 

        curr_player.transact(deal.amount - deal.amount_receiving)
        other_player.transact(deal.amount_receiving - deal.amount)

        recv = list(map(other_player.name_to_property_index, deal.properties_recieving))
        give = list(map(curr_player.name_to_property_index, deal.properties_giving))


        curr_player.remove_properties(give)
        other_player.add_properties(give)

        curr_player.add_properties(recv)
        other_player.remove_properties(recv)