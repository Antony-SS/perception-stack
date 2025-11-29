from geometry.gridmap import DenseGridLayer, SparseGridLayer
import cv2
import numpy as np


def visualize_dense_grid_layer(dense_grid_layer: DenseGridLayer, binary: bool = True, exponential_scaling: bool = False):

    if binary:
        occupancy_data = dense_grid_layer.occupancy_data > 0
    else:
        occupancy_data = dense_grid_layer.occupancy_data

    occupancy_data = occupancy_data.astype(np.uint8)
    if exponential_scaling:
        occupancy_data = np.exp(occupancy_data)
    else:
        occupancy_data = occupancy_data

    occupancy_vis = cv2.applyColorMap(occupancy_data, cv2.COLORMAP_JET)

    return occupancy_vis

def visualize_sparse_grid_layer(sparse_grid_layer: SparseGridLayer):
    raise NotImplementedError("Visualization of sparse grid layers is not implemented yet")