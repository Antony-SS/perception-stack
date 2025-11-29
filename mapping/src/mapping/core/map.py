from pydantic import BaseModel
from typing import Optional, Dict, Union, List
from geometry.gridmap import GridmapCoordinates, Gridmap, DenseGridLayer, SparseGridLayer
import numpy as np
import cv2

class Map(BaseModel):
    class Config:
        arbitrary_types_allowed = True

    name: str
    gridmap_coords: GridmapCoordinates

    odometry_data: Optional[List[np.ndarray]] = None

    def __init__(self, name: str, bounds: np.ndarray, padding: float = 1.0, resolution: float = 0.1, odometry_data: Optional[List[np.ndarray]] = None):
        super().__init__(
            name=name,
            gridmap_coords=GridmapCoordinates(bounds, resolution),
            odometry_data=odometry_data if odometry_data is not None else []
        )

    def visualize(self, **args):
        raise NotImplementedError("Visualization of maps is not implemented yet")

    def draw_origin_axes(self, input_image: np.ndarray, size: float = 1.0):
        self.draw_axes(input_image, size, np.array([0, 0]), 0.0)
        return input_image

    def draw_axes(self, input_image: np.ndarray, size: float = 1.0, start_point: np.ndarray = np.array([0, 0]), yaw: float = 0.0, ):

        forward_vector = np.array([np.cos(yaw), np.sin(yaw)])
        left_vector = np.array([-np.sin(yaw), np.cos(yaw)])

        forward_point = start_point + forward_vector * size
        left_point = start_point + left_vector * size

        forward_point_idx = self.gridmap_coords.xy_to_uv(forward_point[0], forward_point[1])
        left_point_idx = self.gridmap_coords.xy_to_uv(left_point[0], left_point[1])

        # flip indices for cv2 indexing
        forward_point_cv2 = (int(forward_point_idx[1]), int(forward_point_idx[0]))
        left_point_cv2 = (int(left_point_idx[1]), int(left_point_idx[0]))

        cv2.arrowedLine(input_image, forward_point_cv2, left_point_cv2, (0, 0, 255), 2)
        cv2.arrowedLine(input_image, left_point_cv2, forward_point_cv2, (0, 255, 0), 2)

        return input_image

    def draw_odometry_data(self, input_image: np.ndarray, axis_size: float = 0.5):

        if not self.odometry_data or len(self.odometry_data) == 0:
            return input_image

        # Get the u,v indices for all odometry points
        all_x = np.array([pose[0] for pose in self.odometry_data])
        all_y = np.array([pose[1] for pose in self.odometry_data])
        uv_points = self.gridmap_coords.xy_to_uv(all_x, all_y)

        # Draw lines between all consecutive odometry points
        for i in range(1, len(uv_points)):
            pt1 = (int(uv_points[i-1, 1]), int(uv_points[i-1, 0]))  # cv2 uses (col, row)
            pt2 = (int(uv_points[i, 1]), int(uv_points[i, 0]))
            cv2.line(input_image, pt1, pt2, (0, 0, 255), 2)

        # At the final point, draw axis representing robot pose if theta is available
        last_pose = self.odometry_data[-1]

        yaw = last_pose[2]

        last_xy = np.array([last_pose[0], last_pose[1]])
        self.draw_axes(input_image, axis_size, last_xy, yaw)

        return input_image

    
    def add_odometry_data(self, odometry_data: List[np.ndarray]):
        if self.odometry_data is None:
            self.odometry_data = []
        self.odometry_data.extend(odometry_data)