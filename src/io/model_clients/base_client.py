from typing import Any, Optional, TypeVar
from pydantic import BaseModel


T = TypeVar("T", bound=BaseModel)

class BaseClient:
    def send_request(self, message: str, model: type[T], schema: Optional[dict[str, Any]]=None) -> T:
        raise NotImplementedError("send_request not implemented")