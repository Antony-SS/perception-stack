from data_models.impl.tf_instance import TFInstance
from data_models.impl.transforms import Transform3D
from data_models.core.base_metadata import BaseMetadata

from rclpy.time import Time

from ros_python_conversions.ros2.time import time_to_timestamp
from typing import Any, Dict, Union

import numpy as np
from scipy.spatial.transform import Rotation

########################################################
# TF CONVERSIONS
########################################################

# TF MESSAGE -> TF INSTANCE

def tf_message_to_tf_instance(msg: Any, instance_index: int = -1, timestamp: Union[Time, float] = 0.0, use_header: bool = False) -> TFInstance:
    """Convert a tf2_msgs/msg/TFMessage to a TFInstance.
    
    Parameters
    ----------
    msg : Any
        ROS2 TFMessage containing an array of TransformStamped messages
    instance_index : int
        Index for this instance (default: -1)
    timestamp : Union[Time, float]
        Timestamp to use if use_header is False (default: 0.0)
    use_header : bool
        Whether to use header timestamps from messages (default: False)
        
    Returns
    -------
    TFInstance
        Converted TF instance containing all transforms
        
    Notes
    -----
    If use_header is True, the timestamp from the first transform's header will be used.
    If multiple transforms have different timestamps, the first one is used.
    When called from ros2.py, use_header defaults to False and the timestamp passed
    from the stream is used. Note that TFMessage doesn't have a header itself, so
    use_header_timestamps in make_tf_stream should be set to False.
    """
    transforms: Dict[str, Transform3D] = {}
    
    # Determine timestamp
    if use_header and len(msg.transforms) > 0:
        timestamp_val = time_to_timestamp(msg.transforms[0].header.stamp)
    else:
        timestamp_val = time_to_timestamp(timestamp) if isinstance(timestamp, Time) else timestamp
    
    # Convert each TransformStamped to TransformData
    for transform_stamped in msg.transforms:
        parent_frame_id = transform_stamped.header.frame_id
        child_frame_id = transform_stamped.child_frame_id
        
        # Extract translation
        translation = np.array([
            transform_stamped.transform.translation.x,
            transform_stamped.transform.translation.y,
            transform_stamped.transform.translation.z
        ])
        
        # Extract rotation quaternion and create Rotation object
        # ROS uses [x, y, z, w] format, scipy also uses [x, y, z, w]
        quaternion = [
            transform_stamped.transform.rotation.x,
            transform_stamped.transform.rotation.y,
            transform_stamped.transform.rotation.z,
            transform_stamped.transform.rotation.w
        ]
        rotation = Rotation.from_quat(quaternion)
        
        transforms[parent_frame_id + "->" + child_frame_id] = Transform3D(
            translation=translation,
            rotation=rotation
        )
    
    return TFInstance(
        transforms=transforms,
        metadata=BaseMetadata(timestamp=timestamp_val, index=instance_index)
    )

def transform_stamped_to_tf_instance(msg: Any, instance_index: int = -1, timestamp: Union[Time, float] = 0.0, use_header: bool = False) -> TFInstance:
    """Convert a single geometry_msgs/msg/TransformStamped to a TFInstance.
    
    Parameters
    ----------
    msg : Any
        ROS2 TransformStamped message
    instance_index : int
        Index for this instance (default: -1)
    timestamp : Union[Time, float]
        Timestamp to use if use_header is False (default: 0.0)
    use_header : bool
        Whether to use header timestamp from message (default: False)
        
    Returns
    -------
    TFInstance
        Converted TF instance containing the single transform
        
    Notes
    -----
    This is a convenience function for when you have a single transform rather than
    a TFMessage containing multiple transforms.
    """
    transforms: Dict[str, Transform3D] = {}
    
    # Determine timestamp
    if use_header:
        timestamp_val = time_to_timestamp(msg.header.stamp)
    else:
        timestamp_val = time_to_timestamp(timestamp) if isinstance(timestamp, Time) else timestamp
    
    # Extract translation
    translation = np.array([
        msg.transform.translation.x,
        msg.transform.translation.y,
        msg.transform.translation.z
    ])
    
    # Extract rotation quaternion and create Rotation object
    # ROS uses [x, y, z, w] format, scipy also uses [x, y, z, w]
    quaternion = [
        msg.transform.rotation.x,
        msg.transform.rotation.y,
        msg.transform.rotation.z,
        msg.transform.rotation.w
    ]
    rotation = Rotation.from_quat(quaternion)
    
    transforms[msg.child_frame_id] = Transform3D(
        translation=translation,
        rotation=rotation
    )
    
    return TFInstance(
        transforms=transforms,
        metadata=BaseMetadata(timestamp=timestamp_val, index=instance_index)
    )

### TF INSTANCE -> TF MESSAGE ###

#TODO: Implement reverse conversions if needed

