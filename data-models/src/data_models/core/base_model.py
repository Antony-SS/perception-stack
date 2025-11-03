from pydantic import BaseModel, ConfigDict, Field
from .base_metadata import BaseMetadata
from typing import Any


class BaseModel(BaseModel):
    metadata : BaseMetadata
    data : Any

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def __len__(self) -> int:
        return 1

    def __getitem__(self, index: int) -> 'BaseModel':
        return self
