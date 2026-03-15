
from ..move_broadcaster import MoveBroadcaster
from .io_data_models import ActionInput, ActionInputInt, ActionInputTrade, ActionRequest, GameStateModel


class BaseIO:
    def __init__(self, verbose: bool=False):
        self.verbose = verbose

    def request_action(self, options: ActionRequest, broadcaster: MoveBroadcaster, game_state: GameStateModel | None = None) -> ActionInput:
        return ActionInput(action_name="Nothing", explanation="I do nothing.")
    
    def request_action_int(self, options: ActionRequest, broadcaster: MoveBroadcaster, game_state: GameStateModel | None = None) -> ActionInputInt:
        raise NotImplementedError("request_action_int not implemented")
    
    def request_trade_details(self, options: ActionRequest, game_state: GameStateModel, from_player_name: str, to_player_name: str, broadcaster: MoveBroadcaster) -> ActionInputTrade:
        raise NotImplementedError("request_trade_details not implemented")

    def provide_info(self, message: str):
        pass

    def trade_details_message(self, trade: ActionInputTrade) -> str:
        message = ""

        if trade.amount > 0:
            message += f"Money you will receive: ${trade.amount}\n"

        if trade.amount_receiving > 0: 
            message += f"\nMoney you will give: ${trade.amount_receiving}\n"

        if len(trade.properties_giving) > 0:
            message += "Properties they will give you:\n"
            for prop in trade.properties_giving:
                message += f"{prop}\n"
            message += '\n'

        if len(trade.properties_recieving) > 0:
            message += "\nProperties they want from you:\n"
            for prop in trade.properties_recieving:
                message += f"{prop}\n"
            message += '\n'

        if len(trade.reason) > 0:
            message += f"Their reasoning behind the trade: {trade.reason}"
        return message

    def trade_context_message(self, game_state: GameStateModel, from_player_name: str, to_player_name: str) -> str:
        your_properties = game_state.properties_owned.get(from_player_name, [])
        other_properties = game_state.properties_owned.get(to_player_name, [])
        your_balance = game_state.player_banks.get(from_player_name, 0)
        other_balance = game_state.player_banks.get(to_player_name, 0)

        message = (
            f"You are {from_player_name}. You are proposing a trade to {to_player_name}.\n"
            f"Only include properties from your own list in properties_giving.\n"
            f"Only include properties from {to_player_name}'s list in properties_recieving.\n\n"
            f"Your bank balance: ${your_balance}\n"
            f"{to_player_name}'s bank balance: ${other_balance}\n\n"
            f"Properties owned by {from_player_name}:\n"
        )

        if your_properties:
            for prop in your_properties:
                message += f"- {prop}\n"
        else:
            message += "- None\n"

        message += f"\nProperties owned by {to_player_name}:\n"
        if other_properties:
            for prop in other_properties:
                message += f"- {prop}\n"
        else:
            message += "- None\n"

        message += "\n"
        return message

    def game_state_message(self, game_state: GameStateModel) -> str:
        message = "Here is the current game state:\n\n"

        for player_named, owned_properties in game_state.properties_owned.items():
            if len(owned_properties) == 0:
                continue

            message += f"{player_named} currently owns the following properties:\n"
            for prop in owned_properties:
                message += f"{prop}\n"
            message += "\n"

        message += "Player bank accounts:\n"
        for name, amount in game_state.player_banks.items():
            message += f"{name}: ${amount}\n"

        message += "\n"
        message += "Locations: \n"
        for name, location in game_state.player_locations.items():
            message += f"{name} is currently located on {location}\n"

        message += "\n"
        if game_state.last_roll > 0:
            message += f"{game_state.previous_player_name} just rolled a {game_state.last_roll}.\n"

        if game_state.doubles_count > 0:
            message += f"You rolled {game_state.doubles_count} doubles!\n"

        return message

    def action_request_message(self, actions: ActionRequest):
        message = actions.request

        if self.verbose: 
            message += "\nOptions:\n"
            for action in actions.available_actions:
                message += f"{action.action_name}: {action.description}\n\n"

        return message
