from geometry.gridmap import DenseGridLayer, SparseGridLayer, Gridmap, GridmapCoordinates
import cv2
import numpy as np

def visualize_gridmap(Gridmap: Gridmap, binary: bool = False, exponential_scaling: bool = True, gridlines: float = 0.0):
    """ Returns a visualization of the gridmap, one for dense layers and one for sparse layers. """
        
    dense_layers = Gridmap.get_dense_layers()
    sparse_layers = Gridmap.get_sparse_layers()

    sparse_vis = None
    dense_vis = None

    if len(dense_layers) > 0:
        dense_vis = visualize_stacked_dense_layers(Gridmap, binary=binary, exponential_scaling=exponential_scaling, gridlines=gridlines)
    if len(sparse_layers) > 0:
        sparse_vis = visualize_stacked_sparse_layers(Gridmap, gridlines=gridlines)
    
    return dense_vis, sparse_vis


def visualize_stacked_dense_layers(Gridmap: Gridmap, binary: bool = False, exponential_scaling: bool = True):
    summed_occupancy_data = np.zeros(Gridmap.gridmap_coordinates.shape)
    for layer in Gridmap.get_dense_layers():
        summed_occupancy_data += layer.occupancy_data

    return visualize_dense_grid_layer(summed_occupancy_data, binary=binary, exponential_scaling=exponential_scaling)

def visualize_stacked_sparse_layers(Gridmap: Gridmap, gridlines: float = 0.0):
    raise NotImplementedError("Visualization of stacked sparse layers is not implemented yet")

def visualize_dense_grid_layer(dense_grid_layer: DenseGridLayer, binary: bool = False, exponential_scaling: bool = False, gridlines: float = 0.0):

    if binary:
        occupancy_data = (dense_grid_layer.occupancy_data > 0).astype(np.uint8)
    else:
        occupancy_data = dense_grid_layer.occupancy_data

    if exponential_scaling:
        occupancy_data = np.exp(occupancy_data)
    else:
        occupancy_data = occupancy_data

    occupancy_data = (occupancy_data - occupancy_data.min()) / (occupancy_data.max() - occupancy_data.min())
    occupancy_data = (occupancy_data * 255.0).astype(np.uint8)

    occupancy_vis = cv2.applyColorMap(occupancy_data, cv2.COLORMAP_JET)

    if gridlines > 0.0:
        occupancy_vis = draw_gridlines(occupancy_vis, dense_grid_layer.gridmap_coordinates, gridlines)

    return occupancy_vis

def visualize_sparse_grid_layer(sparse_grid_layer: SparseGridLayer, gridlines: float = 0.0):
    raise NotImplementedError("Visualization of sparse grid layers is not implemented yet")

def draw_gridlines(image: np.ndarray, gridmap_coordinates: GridmapCoordinates, distance: float = 5.0):

    # start at origin and draw lines at the given distance
    x_origin, y_origin = 0.0, 0.0

    bottom_u = gridmap_coordinates.gridmap_shape[0] - 1
    top_u = 0
    right_v = gridmap_coordinates.gridmap_shape[1] - 1
    left_v = 0

    while y_origin < gridmap_coordinates.gridmap_bounds[3]:
        uv_point = gridmap_coordinates.xy_to_uv(np.array([x_origin]), np.array([y_origin]))
        cv2.line(image, (uv_point[1], top_u), (uv_point[1], bottom_u), (100, 100, 100), 1)
        y_origin += distance
    
    x_origin, y_origin = 0.0, -distance
    while y_origin > gridmap_coordinates.gridmap_bounds[1]:
        uv_point = gridmap_coordinates.xy_to_uv(np.array([x_origin]), np.array([y_origin]))
        cv2.line(image, (uv_point[1], top_u), (uv_point[1], bottom_u), (100, 100, 100), 1)
        y_origin -= distance

    x_origin, y_origin = 0.0, 0.0
    while x_origin < gridmap_coordinates.gridmap_bounds[2]:
        uv_point = gridmap_coordinates.xy_to_uv(np.array([x_origin]), np.array([y_origin]))
        cv2.line(image, (left_v, uv_point[0]), (right_v, uv_point[0]), (100, 100, 100), 1)
        x_origin += distance

    x_origin, y_origin = -distance, 0.0
    while x_origin > gridmap_coordinates.gridmap_bounds[0]:
        uv_point = gridmap_coordinates.xy_to_uv(np.array([x_origin]), np.array([y_origin]))
        cv2.line(image, (left_v, uv_point[0]), (right_v, uv_point[0]), (100, 100, 100), 1)
        x_origin -= distance

    return image