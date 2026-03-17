import json
from typing import Any, Optional, TypeVar

from openai import OpenAI
from pydantic import BaseModel

from .base_client import BaseClient

T = TypeVar("T", bound=BaseModel)

class OpenAIClient(BaseClient):
    def __init__(self, key: str, system_prompt: str, model_name: str, base_url: Optional[str] = None):
        self.client = OpenAI(api_key=key, base_url=base_url)
        self.system_prompt = system_prompt 
        self.model_name = model_name

    def send_request(self, message: str, model: type[T], schema: Optional[dict[str, Any]]=None, error_count: int = 3) -> T:
        json_schema = schema if schema else model.model_json_schema() 
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
                json_res = json.loads(text.strip())
                parsed = model.model_validate(json_res)
                return parsed
            except ValueError as e:
                print(e)
                continue
        raise ValueError(f"Model responded with incorrect schema {error_count} times. Aborting.")