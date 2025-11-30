from mapping.core.map import Map
from geometry.gridmap import DenseGridLayer, GridmapCoordinates
import numpy as np
from typing import Optional, List
from pydantic import BaseModel
from visualization.gridmap_vis import visualize_dense_grid_layer
import cv2

GRIDLINES = 5.0
ORIGIN_AXES_SIZE = 2.0
ODOMETRY_AXES_SIZE = 1.0
ROBOT_RADIUS = 0.4

class TSRBMap(Map):

    class Config:
        arbitrary_types_allowed = True

    dense_layer: DenseGridLayer

    def __init__(self, bounds: np.ndarray, padding_x: float = 1.0, padding_y: float = 1.0, resolution: float = 0.1, odometry_data: Optional[List[np.ndarray]] = None):
        if padding_x is not None:
            bounds[0] -= padding_x
            bounds[2] += padding_x
        if padding_y is not None:
            bounds[1] -= padding_y
            bounds[3] += padding_y
        
        name = "tsrb_map"

        dense_layer = DenseGridLayer(name, GridmapCoordinates(bounds, resolution))

        BaseModel.__init__(
            self,
            name=name,
            gridmap_coords=GridmapCoordinates(bounds, resolution),
            odometry_data=odometry_data if odometry_data is not None else [],
            dense_layer=dense_layer
        )

    def visualize(self, binary: bool = False, exponential_scaling: bool = True, visualize_origin: bool = True, visualize_odometry: bool = True, visualize_robot: bool = True):
        visualization = visualize_dense_grid_layer(self.dense_layer, binary=binary, exponential_scaling=exponential_scaling, gridlines=GRIDLINES)
        if visualize_robot:
            visualization = self.draw_robot(visualization)
        if visualize_origin:
            visualization = self.draw_origin_axes(visualization, size=ORIGIN_AXES_SIZE)
        if visualize_odometry and self.odometry_data and len(self.odometry_data) > 0:
            visualization = self.draw_odometry_data(visualization, axis_size=ODOMETRY_AXES_SIZE)
        return visualization

    def draw_robot(self, input_vis: np.ndarray): # this is sloppy, should be factored out to visualization package
        current_pose = self.odometry_data[-1]
        current_pose_xy = current_pose[:2]
        robot_radius_pixels = int(ROBOT_RADIUS / self.gridmap_coords.grid_resolution)
        uv_point = self.gridmap_coords.xy_to_uv(np.array([current_pose_xy[0]]), np.array([current_pose_xy[1]]))
        cv2.circle(input_vis, (uv_point[1], uv_point[0]), robot_radius_pixels, (255, 255, 255), -1)
        return input_vis
