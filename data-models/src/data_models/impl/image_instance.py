from data_models.core.base_model import BaseInstance
from data_models.core.base_metadata import BaseMetadata

import numpy as np

class ImageInstance(BaseInstance):
    
    data : np.ndarray
    metadata : BaseMetadata

    class Config:
        arbitrary_types_allowed = True

    @property
    def timestamp(self) -> float:
        return self.metadata.timestamp
    
    @property
    def index(self) -> int:
        return self.metadata.index