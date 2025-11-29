from mapping.src.core.map import Map
from geometry.gridmap import DenseGridLayer, GridmapCoordinates
import numpy as np
from typing import Optional, List


class TSRBMap(Map):

    class Config:
        arbitrary_types_allowed = True

    dense_layer: DenseGridLayer

    def __init__(self, name: str, bounds: np.ndarray, padding: float = 1.0, resolution: float = 0.1, odometry_data: Optional[List[np.ndarray]] = None):
        super().__init__(name, bounds, padding, resolution)
        self.dense_layer = DenseGridLayer(name, self.gridmap_coords)
        self.odometry_data = odometry_data if odometry_data is not None else []

    def visualize(self, binary: bool = False, exponential_scaling: bool = True, visualize_origin: bool = True, visualize_odometry: bool = True):
        visualization = self.dense_layer.visualize(binary=binary, exponential_scaling=exponential_scaling)
        if visualize_origin:
            visualization = self.draw_origin_axes(visualization)
        if visualize_odometry and self.odometry_data and len(self.odometry_data) > 0:
            visualization = self.draw_odometry_data(visualization)
        return visualization
