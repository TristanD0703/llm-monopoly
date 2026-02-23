from ..io.base_io import BaseIO
from ..io.io_data_models import ActionInput, ActionRequest, GameStateModel


class CLI(BaseIO):
    def request_action(self, options: ActionRequest, game_state: GameStateModel | None) -> ActionInput:
        if game_state:
            print(self.game_state_message(game_state))

        print(self.action_request_message(options))
        return self.get_action(options)

    def get_action(self, options: ActionRequest) -> ActionInput:
        for i, item in enumerate(options.available_actions):
            print(f"{i+1}. {item.action_name}")

        inp = -1
        repeat = True
        while repeat: 
            try:
                inp = int(input()) - 1
                if inp >= 0 and inp < len(options.available_actions):
                    repeat = False
                    print("Number not an option")
            except ValueError:
                print("Not a number")

        name = options.available_actions[inp].action_name
        return ActionInput(action_name=name, explanation="")
        