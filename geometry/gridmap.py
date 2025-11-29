from pydantic import BaseModel
from typing import Optional
import numpy as np

class GridmapCoordinates(BaseModel):
    """
    Model for gridmap coordinates.  All gridmap classes make use of this for coordinate conversions.
    """

    class Config:
        arbitrary_types_allowed = True

    gridmap_bounds: np.ndarray # [xmin, ymin, xmax, ymax]
    grid_resolution: float # in meters

    # These are calculated on initialization
    gridmap_shape: Optional[np.ndarray] = None
    left_y_edges: Optional[np.ndarray] = None
    left_x_edges: Optional[np.ndarray] = None
    x_coords: Optional[np.ndarray] = None # coordinates of the bin centers in the x direction
    y_coords: Optional[np.ndarray] = None # coordinates of the bin centers in the y direction

    def __init__(self, gridmap_bounds: np.ndarray, grid_resolution: float):
        self._gridmap_shape = np.floor((gridmap_bounds[2:] - gridmap_bounds[:2]) / grid_resolution).astype(int)
        self.left_x_edges = np.flip(np.linspace(gridmap_bounds[0], gridmap_bounds[2], self._gridmap_shape[0] + 1))
        self.left_y_edges = np.flip(np.linspace(gridmap_bounds[1], gridmap_bounds[3], self._gridmap_shape[1] + 1))
        self.x_coords = (self.left_x_edges[:-1] + self.left_x_edges[1:]) / 2
        self.y_coords = (self.left_y_edges[:-1] + self.left_y_edges[1:]) / 2


    def xy_to_uv(self, x: np.ndarray, y: np.ndarray) -> np.ndarray:
        """ 
        Convert x, y coordinates to u, v indices, they will not necessarilly fall within the gridmap bounds.

        """
        if len(x) == 1 and len(y) == 1:
            x_idx = self._gridmap_shape[0] - 1 - np.floor((x[0] - self.gridmap_bounds[0]) / self.grid_resolution).astype(int)
            y_idx = self._gridmap_shape[1] - 1 - np.floor((y[0] - self.gridmap_bounds[1]) / self.grid_resolution).astype(int)
            return np.array([x_idx, y_idx])
        elif len(x) == len(y):
            x_idx = self._gridmap_shape[0] - 1 - np.floor((x - self.gridmap_bounds[0]) / self.grid_resolution).astype(int)
            y_idx = self._gridmap_shape[1] - 1 - np.floor((y - self.gridmap_bounds[1]) / self.grid_resolution).astype(int)
            return np.concatenate((x_idx.reshape(-1, 1), y_idx.reshape(-1, 1)), axis=1)
        else:
            raise ValueError("x and y must have the same length")
        
    def uv_to_xy(self, u: np.ndarray, v: np.ndarray) -> np.ndarray:
        if len(u) == 1 and len(v) == 1:
            return np.array([self.x_coords[u[0]], self.y_coords[v[0]]]).reshape(1, -1)
        elif len(u) == len(v):
            return np.concatenate((self.x_coords[u].reshape(-1, 1), self.y_coords[v].reshape(-1, 1)), axis=1)
        else:
            raise ValueError("u and v must have the same length")

class DenseGridLayer(BaseModel):

    gridmap_coordinates: GridmapCoordinates
    occupancy_data: np.ndarray = None


    def __init__(self, gridmap_coordinates: GridmapCoordinates):
        self.gridmap_coordinates = gridmap_coordinates
        self.occupancy_data = np.zeros(self.shape)

    @property
    def shape(self) -> np.ndarray:
        return self.gridmap_coordinates.gridmap_shape
    
    @property
    def bounds(self) -> np.ndarray:
        return self.gridmap_coordinates.gridmap_bounds
    
    @property
    def resolution(self) -> float:
        return self.gridmap_coordinates.grid_resolution

    def uv_to_xy(self, u: np.ndarray, v: np.ndarray) -> np.ndarray:
        return self.gridmap_coordinates.uv_to_xy(u, v)

    def add_points(self, points: np.ndarray):
        x_edges = np.linspace(self.gridmap_coordinates.gridmap_bounds[0], self.gridmap_coordinates.gridmap_bounds[2], self.shape[0] + 1)
        y_edges = np.linspace(self.gridmap_coordinates.gridmap_bounds[1], self.gridmap_coordinates.gridmap_bounds[3], self.shape[1] + 1)
        histogram, _, _ = np.histogram2d(points[:, 0], points[:, 1], bins=(x_edges, y_edges))

        histogram = np.fliplr(np.flipud(histogram))
        self.occupancy_data += histogram



