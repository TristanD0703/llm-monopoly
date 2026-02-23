from ..io.base_io import BaseIO
from ..io.io_data_models import ActionInput, ActionInputInt, ActionRequest, GameStateModel


class CLI(BaseIO):
    def request_action(self, options: ActionRequest, game_state: GameStateModel | None=None) -> ActionInput | ActionInputInt:
        if game_state:
            print(self.game_state_message(game_state))

        print(self.action_request_message(options))
        if options.input_type == 'Int':
            return self.get_action_int()
        return self.get_action(options)


    def get_action(self, options: ActionRequest) -> ActionInput | ActionInputInt:
        for i, item in enumerate(options.available_actions):
            print(f"{i+1}. {item.action_name}")

        inp = -1
        repeat = True
        while repeat: 
            try:
                inp = int(input()) - 1
                if inp >= 0 and inp < len(options.available_actions):
                    repeat = False
                else:
                    print("Number not an option")
            except ValueError:
                print("Not a number")

        name = options.available_actions[inp].action_name
        return ActionInput(action_name=name, explanation="")
    
    def get_action_int(self) -> ActionInputInt:
        while True:
            try:
                inpt = int(input())
                return ActionInputInt(number=inpt, explanation="") 
            except ValueError:
                print("Not a number")

    def provide_info(self, message: str):
        print(message)