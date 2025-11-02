from pydantic import BaseModel, ConfigDict


class BaseMetadata(BaseModel):
    timestamp : float
    index: int
    model_config = ConfigDict(arbitrary_types_allowed=True)

    def __len__(self) -> int:
        return 1

    def __getitem__(self, index: int) -> 'BaseMetadata':
        return self