from pydantic import BaseModel
from typing import Optional
import numpy as np
from typing import Dict, List, Union

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
        gridmap_shape = np.floor((gridmap_bounds[2:] - gridmap_bounds[:2]) / grid_resolution).astype(int)
        left_x_edges = np.flip(np.linspace(gridmap_bounds[0], gridmap_bounds[2], gridmap_shape[0] + 1))
        left_y_edges = np.flip(np.linspace(gridmap_bounds[1], gridmap_bounds[3], gridmap_shape[1] + 1))
        x_coords = (left_x_edges[:-1] + left_x_edges[1:]) / 2
        y_coords = (left_y_edges[:-1] + left_y_edges[1:]) / 2
        
        super().__init__(
            gridmap_bounds=gridmap_bounds,
            grid_resolution=grid_resolution,
            gridmap_shape=gridmap_shape,
            left_x_edges=left_x_edges,
            left_y_edges=left_y_edges,
            x_coords=x_coords,
            y_coords=y_coords
        )


    def xy_to_uv(self, x: np.ndarray, y: np.ndarray) -> np.ndarray:
        """ 
        Convert x, y coordinates to u, v indices, they will not necessarilly fall within the gridmap bounds.

        """
        if len(x) == 1 and len(y) == 1:
            x_idx = self.gridmap_shape[0] - 1 - np.floor((x[0] - self.gridmap_bounds[0]) / self.grid_resolution).astype(int)
            y_idx = self.gridmap_shape[1] - 1 - np.floor((y[0] - self.gridmap_bounds[1]) / self.grid_resolution).astype(int)
            return np.array([x_idx, y_idx])
        elif len(x) == len(y):
            x_idx = self.gridmap_shape[0] - 1 - np.floor((x - self.gridmap_bounds[0]) / self.grid_resolution).astype(int)
            y_idx = self.gridmap_shape[1] - 1 - np.floor((y - self.gridmap_bounds[1]) / self.grid_resolution).astype(int)
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
    class Config:
        arbitrary_types_allowed = True

    name: str = "dense_grid_layer"
    gridmap_coordinates: GridmapCoordinates
    occupancy_data: np.ndarray = None


    def __init__(self, name: str, gridmap_coordinates: GridmapCoordinates):
        shape = gridmap_coordinates.gridmap_shape
        occupancy_data = np.zeros(shape)
        
        super().__init__(
            name=name,
            gridmap_coordinates=gridmap_coordinates,
            occupancy_data=occupancy_data
        )

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

class SparseGridLayer(BaseModel):

    """ Sparse grid layer for a gridmap.  Only stores geometric objects like circles, boxes, lines, etc. at coordinate locations.
    Doesn't maintain occupancy data, but can visualize the objects on the gridmap.
    """

    class Config:
        arbitrary_types_allowed = True

    name: str = "sparse_grid_layer"
    gridmap_coordinates: GridmapCoordinates
    

    def __init__(self, name: str, gridmap_coordinates: GridmapCoordinates):
        shape = gridmap_coordinates.gridmap_shape
        occupancy_data = np.zeros(shape)
        
        super().__init__(
            name=name,
            gridmap_coordinates=gridmap_coordinates,
            occupancy_data=occupancy_data
        )

class Gridmap(BaseModel):
    class Config:
        arbitrary_types_allowed = True

    gridmap_coordinates: GridmapCoordinates
    layers: Optional[Dict[str, Union[DenseGridLayer, SparseGridLayer]]] = None

    def add_layer(self, layer: Union[DenseGridLayer, SparseGridLayer]):
        if self.layers is None:
            self.layers = {}
        self.layers[layer.name] = layer

    def get_layer_by_name(self, name: str) -> Union[DenseGridLayer, SparseGridLayer]:
        return self.layers[name] if self.layers is not None else None

    def get_layer_by_index(self, index: int) -> Union[DenseGridLayer, SparseGridLayer]:
        return self.layers[self.layer_names[index]] if self.layers is not None else None

    @property
    def layer_names(self) -> List[str]:
        return list(self.layers.keys()) if self.layers is not None else []

    def get_layer_count(self) -> int:
        return len(self.layer_names) if self.layers is not None else 0

    def get_dense_layers(self) -> List[DenseGridLayer]:
        return [layer for layer in self.layers.values() if isinstance(layer, DenseGridLayer)]

    def get_sparse_layers(self) -> List[SparseGridLayer]:
        return [layer for layer in self.layers.values() if isinstance(layer, SparseGridLayer)]

