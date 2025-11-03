from data_models.impl.image_instance import ImageInstance
from data_models.core.base_metadata import BaseMetadata

from cv_bridge import CvBridge

from rclpy.time import Time

from ros_python_conversions.ros2.time import time_to_timestamp
from typing import Any

bridge = CvBridge()

########################################################
# RGB IMAGE CONVERSIONS
########################################################

# IMAGE MESSAGE -> IMAGE INSTANCE

def any_image_msg_to_image_instance(msg : Any, instance_index : int = -1, timestamp : Time = Time(seconds=0, nanoseconds=0), use_header : bool = False) -> ImageInstance:
    if msg.__msgtype__ == "sensor_msgs/msg/CompressedImage":
        return compressed_image_msg_to_image_instance(msg, instance_index=instance_index, timestamp=timestamp, use_header=use_header)
    elif msg.__msgtype__ == "sensor_msgs/msg/Image":
        return image_msg_to_image_instance(msg, instance_index=instance_index, timestamp=timestamp, use_header=use_header)
    else:
        raise ValueError(f"Unsupported image message type: {msg.__msg_type__}")

def compressed_image_msg_to_image_instance(msg : Any, instance_index : int = -1, timestamp : Time = Time(seconds=0, nanoseconds=0), use_header : bool = False) -> ImageInstance:
    if use_header:
        timestamp = time_to_timestamp(msg.header.stamp)
    else:
        timestamp = timestamp
    return ImageInstance(data=bridge.compressed_imgmsg_to_cv2(msg, desired_encoding="bgr8"), metadata=BaseMetadata(timestamp=timestamp, index=instance_index))

def image_msg_to_image_instance(msg : Any, instance_index : int = -1, timestamp : Time = Time(seconds=0, nanoseconds=0), use_header=False) -> ImageInstance:
    if use_header:
        timestamp = time_to_timestamp(msg.header.stamp)
    else:
        timestamp = timestamp
    return ImageInstance(data=bridge.imgmsg_to_cv2(msg, desired_encoding="bgr8"), metadata=BaseMetadata(timestamp=timestamp, index=instance_index))

### IMAGE INSTANCE -> IMAGE MESSAGE ###

#TODO