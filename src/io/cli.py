from typing import Any, Optional

from ..io.io_data_models import ActionInputTrade
from ..io.base_io import BaseIO
from ..io.io_data_models import ActionInput, ActionInputInt, ActionRequest, GameStateModel


class CLI(BaseIO):
    def request_action(self, options: ActionRequest, game_state: GameStateModel | None=None) -> ActionInput:
        if game_state:
            print(self.game_state_message(game_state))

        print(self.action_request_message(options))

        return self.get_action(options)

    def request_action_int(self, options: ActionRequest, game_state: Optional[GameStateModel]=None) -> ActionInputInt:
        if game_state:
            print(self.game_state_message(game_state))

        print(self.action_request_message(options))
        return self.get_action_int()

    def request_trade_details(self, options: ActionRequest, game_state: GameStateModel, from_player_name: str, to_player_name: str) -> ActionInputTrade:
        print(options.request + "\nGive money amount:")
        give = self.get_optional_int()

        print(options.request + "\nReceive money amount:")
        recv = self.get_optional_int()

        print(f"Please choose the properties you want to give to {to_player_name}. Enter a comma-separated list of numbers corresponding to your choices. Type enter to skip")
        from_player_props = game_state.properties_owned[from_player_name]
        giving: list[str] = []
        if len(from_player_props) > 0:
            for i, prop in enumerate(from_player_props):
                print(f"{i+1}. {prop}")

            giving = self.get_list(from_player_props)
            
        print(f"Please choose the properties you want to receive from {to_player_name}. Enter a comma-separated list of numbers corresponding to your choices. Type enter to skip")
        to_player_props = game_state.properties_owned[to_player_name]
        receiving: list[str] = []
        if len(to_player_props) > 0:
            for i, prop in enumerate(to_player_props):
                print(f"{i+1}. {prop}")

            receiving = self.get_list(to_player_props)
        
        return ActionInputTrade(reason="", amount=give.number if give else 0, amount_receiving=recv.number if recv else 0, properties_giving=giving, properties_recieving=receiving)

    def get_list(self, assoc_values: list[Any] | None=None) -> list[Any]:
        repeat = True
        ret: list[Any] = []
        while repeat:
            ret = []
            repeat = False
            inp = input()
            nums = inp.strip().split(',')
            if len(inp) == 0:
                return []
            for i, n in enumerate(nums):
                curr = -1
                try:
                    curr = int(n)-1
                except ValueError:
                    repeat = True
                    print(f"Number at pos {i+1} not valid")
                    break
                if assoc_values:
                    if curr < 0 or curr >= len(assoc_values):
                        repeat = True
                        print(f"Number at pos {i+1} not an option")
                    else:
                        ret.append(assoc_values[curr])
                else:
                    ret.append(curr)
        return ret

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

    def get_optional_int(self) -> ActionInputInt | None:
        while True:
            try:
                inp = input()
                if len(inp) == 0:
                    return None
                inpt = int(inp)
                return ActionInputInt(number=inpt, explanation="") 
            except ValueError:
                print("Not a number")
    def provide_info(self, message: str):
        print(message)