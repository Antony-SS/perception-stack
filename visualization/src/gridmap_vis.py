from geometry.gridmap import DenseGridLayer, SparseGridLayer, Gridmap
import cv2
import numpy as np

def visualize_gridmap(Gridmap: Gridmap, binary: bool = False, exponential_scaling: bool = True):
    """ Returns a visualization of the gridmap, one for dense layers and one for sparse layers. """
        
    dense_layers = Gridmap.get_dense_layers()
    sparse_layers = Gridmap.get_sparse_layers()

    sparse_vis = None
    dense_vis = None

    if len(dense_layers) > 0:
        dense_vis = visualize_stacked_dense_layers(Gridmap, binary=binary, exponential_scaling=exponential_scaling)
    if len(sparse_layers) > 0:
        sparse_vis = visualize_stacked_sparse_layers(Gridmap)
    
    return dense_vis, sparse_vis


def visualize_stacked_dense_layers(Gridmap: Gridmap, binary: bool = False, exponential_scaling: bool = True):
    summed_occupancy_data = np.zeros(Gridmap.gridmap_coordinates.shape)
    for layer in Gridmap.get_dense_layers():
        summed_occupancy_data += layer.occupancy_data

    return visualize_dense_grid_layer(summed_occupancy_data, binary=binary, exponential_scaling=exponential_scaling)

def visualize_stacked_sparse_layers(Gridmap: Gridmap):
    raise NotImplementedError("Visualization of stacked sparse layers is not implemented yet")

def visualize_dense_grid_layer(dense_grid_layer: DenseGridLayer, binary: bool = False, exponential_scaling: bool = False):

    if binary:
        occupancy_data = dense_grid_layer.occupancy_data > 0
    else:
        occupancy_data = dense_grid_layer.occupancy_data

    occupancy_data = occupancy_data.astype(np.uint8)

    if exponential_scaling:
        occupancy_data = np.exp(occupancy_data)
    else:
        occupancy_data = occupancy_data

    occupancy_data = (occupancy_data - occupancy_data.min()) / (occupancy_data.max() - occupancy_data.min())
    occupancy_vis = cv2.applyColorMap(occupancy_data, cv2.COLORMAP_JET)

    return occupancy_vis

def visualize_sparse_grid_layer(sparse_grid_layer: SparseGridLayer):
    raise NotImplementedError("Visualization of sparse grid layers is not implemented yet")