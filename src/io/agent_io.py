import json
from typing import Any, TypeVar

from pydantic import BaseModel

from .model_clients.base_client import BaseClient
from .model_clients.claude_client import ClaudeClient
from .model_clients.openai_client import OpenAIClient

from ..move_broadcaster import MoveBroadcaster

from ..io.base_io import BaseIO
from ..io.io_data_models import ActionInput, ActionInputInt, ActionInputTrade, ActionRequest, GameStateModel
from ..io.prompts.init_prompt import SYSTEM_PROMPT
import os

T = TypeVar("T", bound=BaseModel)

OPEN_ROUTER_BASE = 'https://openrouter.ai/api/v1'
GEMINI_OPENAI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"
OLLAMA_BASE_URL = 'http://localhost:11434/v1'
class AgentIO(BaseIO):
    def __init__(self, client: BaseClient):
        self.prev_info = ""
        self.verbose = True
        self.client = client

    @classmethod
    def open_router_from_env(cls, model_name: str, system_prompt: str = SYSTEM_PROMPT): 
        key = os.getenv('OPENROUTER_API_KEY')
        if not key:
            raise ValueError("OPENROUTER_API_KEY missing in environment")

        client = OpenAIClient(key, system_prompt, model_name, OPEN_ROUTER_BASE)
        return cls(client)

    @classmethod
    def local_model_ollama(cls, model_name: str, system_prompt: str = SYSTEM_PROMPT, service_url: str = OLLAMA_BASE_URL): 
        key = "ollama"
        client = OpenAIClient(key, system_prompt, model_name, service_url)
        return cls(client)
    
    @classmethod
    def openai_from_env(cls, openai_model_name: str, system_prompt: str = SYSTEM_PROMPT):
        key = os.getenv('OPENAI_API_KEY')
        if not key:
            raise ValueError("OPENAI_API_KEY missing in environment")
        client = OpenAIClient(key, system_prompt, openai_model_name)
        return cls(client)

    @classmethod
    def gemini_from_env(cls, gemini_model_name: str, system_prompt: str = SYSTEM_PROMPT):
        key = os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY')
        if not key:
            raise ValueError("GEMINI_API_KEY or GOOGLE_API_KEY missing in environment")
        client = OpenAIClient(key, system_prompt, gemini_model_name, GEMINI_OPENAI_BASE_URL) 
        return cls(client)

    @classmethod
    def claude_from_env(cls, claude_model_name: str, system_prompt: str = SYSTEM_PROMPT):
        key = os.getenv('ANTHROPIC_API_KEY')
        if not key:
            raise ValueError("ANTHROPIC_API_KEY missing in environment")
        client = ClaudeClient(key, system_prompt, claude_model_name)
        return cls(client)

    def action_input_json_schema(self, options: ActionRequest) -> dict[str, Any]:
        json = ActionInput.model_json_schema()
        
        str_list: list[str] = []
        for item in options.available_actions:
            str_list.append(item.action_name)

        json['properties']['action_name']['enum'] = str_list
        return json

    def request_action(self, options: ActionRequest, broadcaster: MoveBroadcaster, game_state: GameStateModel | None = None) -> ActionInput:
        message = self.build_message(options, broadcaster, game_state)
        res = self.client.send_request(message, ActionInput, self.action_input_json_schema(options))

        return res
    
    def request_action_int(self, options: ActionRequest, broadcaster: MoveBroadcaster, game_state: GameStateModel | None = None) -> ActionInputInt:
        message = self.build_message(options, broadcaster, game_state)
        res = self.client.send_request(message, ActionInputInt)

        return res
    
    def request_trade_details(self, options: ActionRequest, game_state: GameStateModel, from_player_name: str, to_player_name: str, broadcaster: MoveBroadcaster) -> ActionInputTrade:
        trade_request = ActionRequest(
            request=(
                f"{options.request}\n\n"
                f"{self.trade_context_message(game_state, from_player_name, to_player_name)}"
            ),
            available_actions=options.available_actions,
            input_type=options.input_type,
        )
        message = self.build_message(trade_request, broadcaster, game_state)
        res = self.client.send_request(message, ActionInputTrade)

        return res

    def build_message(self, options: ActionRequest, broadcaster: MoveBroadcaster, game_state: GameStateModel | None) -> str:
        moves = ""
        if broadcaster:
            moves = json.dumps(broadcaster.get_history())
        message = f"{moves} \n\n {self.prev_info}"
        if game_state:
            message += self.game_state_message(game_state)
        message += self.action_request_message(options)
        self.prev_info = ""
        return message
    
    def provide_info(self, message: str):
        self.prev_info += message
