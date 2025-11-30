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

    def __init__(self, name: str, bounds: np.ndarray, padding_x = 1.0, padding_y = 1.0, resolution: float = 0.1, odometry_data: Optional[List[np.ndarray]] = None):

        if padding_x is not None:
            bounds[0] -= padding_x
            bounds[2] += padding_x
        if padding_y is not None:
            bounds[1] -= padding_y
            bounds[3] += padding_y

        super().__init__(
            name=name,
            gridmap_coords=GridmapCoordinates(bounds, resolution),
            odometry_data=odometry_data if odometry_data is not None else [],
        )

    def visualize(self, **args):
        raise NotImplementedError("Visualization of maps is not implemented yet")

    def draw_origin_axes(self, input_image: np.ndarray, size: float = 1.0):
        self.draw_axes(input_image, size, np.array([0, 0]), 0.0)
        return input_image

    def draw_axes(self, input_image: np.ndarray, size: float = 1.0, start_point: np.ndarray = np.array([0, 0]), yaw: float = 0.0, ):

        yaw = np.deg2rad(yaw)

        forward_vector = np.array([np.cos(yaw), np.sin(yaw)])
        left_vector = np.array([-np.sin(yaw), np.cos(yaw)])

        forward_point = start_point + forward_vector * size
        left_point = start_point + left_vector * size

        start_point_idx = self.gridmap_coords.xy_to_uv(np.array([start_point[0]]), np.array([start_point[1]]))
        forward_point_idx = self.gridmap_coords.xy_to_uv(np.array([forward_point[0]]), np.array([forward_point[1]]))
        left_point_idx = self.gridmap_coords.xy_to_uv(np.array([left_point[0]]), np.array([left_point[1]]))

        # flip indices for cv2 indexing
        forward_point_cv2 = (int(forward_point_idx[1]), int(forward_point_idx[0]))
        left_point_cv2 = (int(left_point_idx[1]), int(left_point_idx[0]))
        start_point_cv2 = (int(start_point_idx[1]), int(start_point_idx[0]))

        cv2.arrowedLine(input_image, start_point_cv2, forward_point_cv2, (0, 0, 255), 2)
        cv2.arrowedLine(input_image, start_point_cv2, left_point_cv2, (0, 255, 0), 2)

        return input_image

    def draw_odometry_data(self, input_image: np.ndarray, axis_size: float = 0.5):

        if not self.odometry_data or len(self.odometry_data) == 0:
            return input_image

        # Get the u,v indices for all odometry points
        all_x = np.array([pose[0] for pose in self.odometry_data])
        all_y = np.array([pose[1] for pose in self.odometry_data])
        uv_points = self.gridmap_coords.xy_to_uv(all_x, all_y)
        uv_points = uv_points.reshape(-1, 2)

        # Draw lines between all consecutive odometry points
        for i in range(1, len(uv_points)):
            pt1 = (int(uv_points[i-1][1]), int(uv_points[i-1][0]))  # cv2 uses (col, row)
            pt2 = (int(uv_points[i][1]), int(uv_points[i][0]))
            cv2.line(input_image, pt1, pt2, (0, 255, 255), 2)  # yellow in BGR

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