from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

class ActionInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    action_name: str = Field(..., description="The name for the associated action you wish to take") 
    explanation: str = Field(..., description="A detailed explanation to why you chose this action.")

class ActionInputInt(BaseModel):
    model_config = ConfigDict(extra="forbid")
    number: int = Field(..., description="The number you want to respond with") 
    explanation: str = Field(..., description="A detailed explanation to why you chose this action.")

class ActionItem(BaseModel):
    model_config = ConfigDict(extra="forbid")
    action_name: str = Field(..., description="The name of the action the user should take. When responding, the action_name must match EXACTLY with one of these")
    description: str = Field(..., description="What the action will do")

class ActionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    available_actions: list[ActionItem] = Field(..., description="The actions available to the user")
    request: str = Field(..., description="Defines context to which the actions will be doing")
    input_type: Literal['Action', 'Int'] = 'Action'

class GameStateModel(BaseModel):
    model_config = ConfigDict(extra="forbid")
    player_locations: dict[str, str] = Field(..., description="A dictionary where they keys are player names and values are the names of the spaces they are currently standing")
    properties_owned: dict[str, list[str]] = Field(..., description="A dictionary where keys are the player names and values are the names of properties owned by the player")
    player_banks: dict[str, int] = Field(..., description="How much money each player has")
    last_roll: int = Field(..., description="The number you just rolled")
    doubles_count: int = Field(..., description="How many doubles you've rolled")
    previous_player_name: str = Field(..., description="name of previous player")


