from .io.io_data_models import ActionInput, ActionInputTrade, ActionItem, ActionRequest, GameStateModel
from .player import Player

class Trade:
    def __init__(self, player: Player, target_player: Player, game_state: GameStateModel, max_counteroffers: int=10):
        self.players: list[tuple[Player, bool]] = [(player, True), (target_player, False)]
        self.game_state = game_state
        self.curr_turn = 1
        self.counter_times = 0
        self.max_counteroffers = max_counteroffers

    def prompt_trade_details(self) -> ActionInputTrade:
        req = ActionRequest(request="Please enter the details of your trade deal", available_actions=[])
        return self.get_curr_player().io.request_trade_details(req, self.game_state, self.get_other_player().name, self.get_curr_player().name)

    def prompt_receive_offer(self, from_player: Player, to_player: Player, details: ActionInputTrade) -> ActionInput:
        mes = from_player.io.trade_details_message(details)
        actions: list[ActionItem] = [
            ActionItem(action_name="Accept", description="Accepts the trade and enacts all the proposed deals"),
            ActionItem(action_name="Counteroffer", description="Make another offer to the other player"),
            ActionItem(action_name="Decline", description="Stop the trading process.")
        ]
        req = ActionRequest(request=f"You received an offer from {from_player.name}! Here are the details:\n{mes}\nWhat will you do?", available_actions=actions)

        return to_player.io.request_action(req, self.game_state)

    def begin_trade(self):
        details = self.prompt_trade_details()

        while not self.is_deal_end():
            curr_player, _ = self.players[self.curr_turn]
            other_player, _ = self.players[self.get_next()]

            res = self.prompt_receive_offer(curr_player, other_player, details)

            if res.action_name == "Accept":
                self.enact_deal(details)
                self.players[self.curr_turn] = curr_player, True
                return
            elif res.action_name == "Counteroffer":
                self.curr_turn = self.get_next()
                details = self.prompt_trade_details()
            else:
                return
            self.counter_times += 1
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
        curr_player, _ = self.players[self.curr_turn]
        other_player, _ = self.players[self.get_next()]

        curr_player.transact(deal.amount - deal.amount_receiving)
        other_player.transact(deal.amount_receiving - deal.amount)

        recv = list(map(curr_player.name_to_property_index, deal.properties_recieving))
        give = list(map(other_player.name_to_property_index, deal.properties_giving))

        other_player.add_properties(recv)
        other_player.remove_properties(give)

        curr_player.add_properties(give)
        curr_player.remove_properties(recv)