from pydantic import BaseModel
from typing import Optional, Dict, Union
from geometry.gridmap import GridmapCoordinates, DenseGridLayer, SparseGridLayer
import numpy as np




class Map(BaseModel):

    gridmap_coords: Optional[GridmapCoordinates] = None
    gridmap_layer: Optional[Union[DenseGridLayer, SparseGridLayer]] = None

    def __init__(self, name: str, bounds: np.ndarray, padding: float = 1.0, resolution: float = 0.1):
        self.gridmap_coords = GridmapCoordinates(bounds, resolution)

    