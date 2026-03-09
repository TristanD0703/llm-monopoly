import json
from typing import Any, Optional, TypeVar

from openai import OpenAI
from pydantic import BaseModel

from ..io.base_io import BaseIO
from ..io.io_data_models import ActionInput, ActionInputInt, ActionInputTrade, ActionRequest, GameStateModel
from ..io.prompts.init_prompt import SYSTEM_PROMPT
import os

T = TypeVar("T", bound=BaseModel)

OPEN_ROUTER_BASE = 'https://openrouter.ai/api/v1'
class AgentIO(BaseIO):
    def __init__(self, model_name: str, api_key: str, base_url: str | None=None):
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.system_prompt = SYSTEM_PROMPT
        self.model_name = model_name
        self.prev_info = ""
        self.verbose = True

    @classmethod
    def open_router_from_env(cls, model_name: str): 
        key = os.getenv('OPENROUTER_API_KEY')
        if not key:
            raise ValueError("OPENROUTER_API_KEY missing in environment")
        return cls(model_name, key, OPEN_ROUTER_BASE)

    @classmethod
    def local_model_ollama(cls, model_name: str): 
        return cls(model_name, 'ollama', 'http://localhost:11434/v1')
    
    @classmethod
    def openai_from_env(cls, openai_model_name: str):
        key = os.getenv('OPENAI_API_KEY')
        if not key:
            raise ValueError("OPENROUTER_API_KEY missing in environment")
        return cls(openai_model_name, key)

    def action_input_json_schema(self, options: ActionRequest) -> dict[str, Any]:
        json = ActionInput.model_json_schema()
        
        str_list: list[str] = []
        for item in options.available_actions:
            str_list.append(item.action_name)

        json['properties']['action_name']['enum'] = str_list
        return json

    def request_action(self, options: ActionRequest, game_state: GameStateModel | None = None) -> ActionInput:
        message = self.build_message(options, game_state)
        res = self.send_request(message, ActionInput, self.action_input_json_schema(options))

        return res
    
    def request_action_int(self, options: ActionRequest, game_state: GameStateModel | None = None) -> ActionInputInt:
        message = self.build_message(options, game_state)
        res = self.send_request(message, ActionInputInt)

        return res
    
    def request_trade_details(self, options: ActionRequest, game_state: GameStateModel, from_player_name: str, to_player_name: str) -> ActionInputTrade:
        message = self.build_message(options, game_state)
        res = self.send_request(message, ActionInputTrade)

        return res

    def build_message(self, options: ActionRequest, game_state: GameStateModel | None) -> str:
        message = self.prev_info 
        if game_state:
            message += self.game_state_message(game_state)
        message += self.action_request_message(options)
        self.prev_info = ""
        return message
    
    def provide_info(self, message: str):
        self.prev_info += message

    def send_request(self, message: str, model: type[T], schema: Optional[dict[str, Any]]=None) -> T:
        json_schema = schema if schema else model.model_json_schema() 
        error_count = 10 
        print(message)
        for _ in range(error_count):
            res = self.client.chat.completions.create(messages=[
                {
                    'role': 'system',
                    'content': self.system_prompt
                },
                {
                    'role': 'user',
                    'content': message
                }
            ], 
            model=self.model_name,
            response_format={"type": 'json_schema', 'json_schema': {"name": "response", "schema": json_schema}}
            )
            text = res.choices[0].message.content 
            if not text:
                continue

            try:
                print(text)
                json_res = json.loads(text.strip())
                parsed = model.model_validate(json_res)
                return parsed
            except ValueError as e:
                print(e)
                continue
        raise ValueError(f"Model responded with incorrect schema {error_count} times. Aborting.")