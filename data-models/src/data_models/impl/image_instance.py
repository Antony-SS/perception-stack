from data_models.core.base_model import BaseModel
from data_models.core.base_metadata import BaseMetadata

from pydantic import ConfigDict
import numpy as np

class ImageInstance(BaseModel):
    
    data : np.ndarray
    metadata : BaseMetadata

    model_config = ConfigDict(arbitrary_types_allowed=True)

    @property
    def timestamp(self) -> float:
        return self.metadata.timestamp
    
    @property
    def index(self) -> int:
        return self.metadata.index