
from typing import Optional
from .io_data_models import ActionInput, ActionInputInt, ActionRequest, GameStateModel


class BaseIO:
    def __init__(self, verbose: bool=False):
        self.verbose = verbose

    def request_action(self, options: ActionRequest, game_state: Optional[GameStateModel]=None) -> ActionInput | ActionInputInt:
        return ActionInput(action_name="Nothing", explanation="I do nothing.")
    
    def provide_info(self, message: str):
        pass

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
