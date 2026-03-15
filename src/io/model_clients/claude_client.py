import json
from typing import Any, TypeVar

from pydantic import BaseModel

from .base_client import BaseClient

from anthropic import Anthropic

T = TypeVar("T", bound=BaseModel)

RESPONSE_TOOL_NAME = "response"


class ClaudeClient(BaseClient):
    def __init__(self, key: str, system_prompt: str, model_name: str):
        self.client: Anthropic = Anthropic(api_key=key)
        self.system_prompt = system_prompt
        self.model_name = model_name

    def send_request(self, message: str, model: type[T], schema: dict[str, Any] | None = None) -> T:
        json_schema = schema if schema else model.model_json_schema()
        error_count = 10

        for _ in range(error_count):
            res = self.client.messages.create(
                model=self.model_name,
                system=self.system_prompt,
                max_tokens=1024,
                tools=[
                    {
                        "name": RESPONSE_TOOL_NAME,
                        "description": "Return the final structured response for this turn.",
                        "input_schema": json_schema,
                    }
                ],
                tool_choice={"type": "tool", "name": RESPONSE_TOOL_NAME},
                messages=[
                    {
                        "role": "user",
                        "content": message,
                    }
                ],
            )

            for block in res.content:
                if getattr(block, "type", None) != "tool_use":
                    continue
                if getattr(block, "name", None) != RESPONSE_TOOL_NAME:
                    continue

                try:
                    return model.model_validate(block.input) # type: ignore
                except ValueError as e:
                    print(e)
                    break
            else:
                text = self._extract_text(res.content)
                if not text:
                    continue

                try:
                    parsed = model.model_validate(json.loads(text.strip()))
                    return parsed
                except ValueError as e:
                    print(e)
                    continue

        raise ValueError(f"Model responded with incorrect schema {error_count} times. Aborting.")

    def _extract_text(self, content: list[Any]) -> str:
        text_blocks: list[str] = []
        for block in content:
            if getattr(block, "type", None) == "text" and getattr(block, "text", None):
                text_blocks.append(block.text)

        combined = "\n".join(text_blocks).strip()
        if combined.startswith("```"):
            lines = combined.splitlines()
            if len(lines) >= 3:
                return "\n".join(lines[1:-1]).strip()
        return combined
