from data_models.impl.pose_instance import PoseInstance
from data_models.impl.transforms import Transform3D
from data_models.core.base_metadata import BaseMetadata

from rclpy.time import Time

from ros_python_conversions.ros2.time import time_to_timestamp
from typing import Any, Union

import numpy as np
from scipy.spatial.transform import Rotation

########################################################
# ODOMETRY CONVERSIONS
########################################################

# ODOMETRY MESSAGE -> POSE INSTANCE

def odometry_msg_to_pose_instance(msg: Any, instance_index: int = -1, timestamp: Union[Time, float] = 0.0, use_header: bool = True) -> PoseInstance:
    """Convert a nav_msgs/msg/Odometry to a PoseInstance.
    
    Parameters  
    ----------
    msg : Any
        ROS2 Odometry message
    instance_index : int
        Index for this instance (default: -1)
    timestamp : Union[Time, float]
        Timestamp to use if use_header is False (default: 0.0)
    use_header : bool
        Whether to use header timestamp from message (default: True)
        
    Returns
    -------
    PoseInstance
        Converted pose instance containing position and orientation
        
    Notes
    -----
    Only extracts the pose (position + orientation) from the odometry message.
    Twist (velocity) information is not included in PoseInstance.
    """
    # Determine timestamp
    if use_header:
        timestamp_val = time_to_timestamp(msg.header.stamp)
    else:
        timestamp_val = time_to_timestamp(timestamp) if isinstance(timestamp, Time) else timestamp
    
    # Extract translation
    translation = np.array([
        msg.pose.pose.position.x,
        msg.pose.pose.position.y,
        msg.pose.pose.position.z
    ])
    
    # Extract rotation quaternion and create Rotation object
    # ROS uses [x, y, z, w] format, scipy also uses [x, y, z, w]
    quaternion = [
        msg.pose.pose.orientation.x,
        msg.pose.pose.orientation.y,
        msg.pose.pose.orientation.z,
        msg.pose.pose.orientation.w
    ]
    rotation = Rotation.from_quat(quaternion)
    
    pose_data = Transform3D(
        translation=translation,
        rotation=rotation
    )
    
    return PoseInstance(
        pose=pose_data,
        metadata=BaseMetadata(timestamp=timestamp_val, index=instance_index)
    )

### POSE INSTANCE -> ODOMETRY MESSAGE ###

#TODO: Implement reverse conversions if needed

