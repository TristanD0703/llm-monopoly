
from typing import Optional
from .io_data_models import ActionInput, ActionRequest, GameStateModel


class BaseIO:
    def request_action(self, options: ActionRequest, game_state: Optional[GameStateModel]) -> ActionInput:
        return ActionInput(action_name="Nothing", explanation="I do nothing.")

    def game_state_message(self, game_state: GameStateModel) -> str:
        message = "Here is the current game state:\n\n"
        for name, location in game_state.player_locations.items():
            message += f"{name} is currently located in {location}\n"

        message += "\n"
        for player_named, owned_properties in game_state.properties_owned.items():
            if len(owned_properties) == 0:
                continue

            message += f"{player_named} currently owns the following properties:\n"
            for prop in owned_properties:
                message += f"{prop}\n"

        message += "\n"
        message += f"You just rolled a {game_state.last_roll}.\n"
        if game_state.doubles_count > 0:
            message += f"You rolled {game_state.doubles_count} doubles!\n"

        return message

    def action_request_message(self, actions: ActionRequest):
        message = actions.request + "Options:\n"
        for action in actions.available_actions:
            message += f"{action.action_name}: {action.description}\n\n"

        return message
