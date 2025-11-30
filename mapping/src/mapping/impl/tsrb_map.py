from mapping.core.map import Map
from geometry.gridmap import DenseGridLayer, GridmapCoordinates
import numpy as np
from typing import Optional, List
from pydantic import BaseModel
from visualization.gridmap_vis import visualize_dense_grid_layer

class TSRBMap(Map):

    class Config:
        arbitrary_types_allowed = True

    dense_layer: DenseGridLayer

    def __init__(self, bounds: np.ndarray, padding: float = 1.0, resolution: float = 0.1, odometry_data: Optional[List[np.ndarray]] = None):
        if padding is not None:
            bounds = bounds + padding * np.array([-1, -1, 1, 1])
        
        name = "tsrb_map"
        dense_layer = DenseGridLayer(name, GridmapCoordinates(bounds, resolution))
        
        # Call BaseModel.__init__ directly with all fields (bypassing Map.__init__)
        BaseModel.__init__(
            self,
            name=name,
            gridmap_coords=GridmapCoordinates(bounds, resolution),
            odometry_data=odometry_data if odometry_data is not None else [],
            dense_layer=dense_layer
        )

    def visualize(self, binary: bool = False, exponential_scaling: bool = True, visualize_origin: bool = True, visualize_odometry: bool = True):
        visualization = visualize_dense_grid_layer(self.dense_layer, binary=binary, exponential_scaling=exponential_scaling)
        if visualize_origin:
            visualization = self.draw_origin_axes(visualization, size=2.0)
        if visualize_odometry and self.odometry_data and len(self.odometry_data) > 0:
            visualization = self.draw_odometry_data(visualization, axis_size=1.0)
        return visualization
