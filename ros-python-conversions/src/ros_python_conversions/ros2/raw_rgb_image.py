from sensor_msgs.msg import CompressedImage
from sensor_msgs.msg import Image

from data_models.impl.image_instance import ImageInstance
from data_models.core.base_metadata import BaseMetadata

from cv_bridge import CvBridge

from rclpy.time import Time

from ros_python_conversions.ros2.time import time_to_timestamp

from typing import Union

bridge = CvBridge()

########################################################
# RGB IMAGE CONVERSIONS
########################################################

# IMAGE MESSAGE -> IMAGE INSTANCE

def any_image_msg_to_image_instance(msg : Union[CompressedImage, Image], instance_index : int = -1, timestamp : Time = Time(seconds=0, nanoseconds=0), use_header : bool = False) -> ImageInstance:
    if isinstance(msg, CompressedImage):
        return compressed_image_msg_to_image_instance(msg, instance_index=instance_index, timestamp=timestamp, use_header=use_header)
    elif isinstance(msg, Image):
        return image_msg_to_image_instance(msg, instance_index=instance_index, timestamp=timestamp, use_header=use_header)
    else:
        raise ValueError(f"Unsupported image message type: {type(msg)}")

def compressed_image_msg_to_image_instance(msg : CompressedImage, instance_index : int = -1, timestamp : Time = Time(seconds=0, nanoseconds=0), use_header : bool = False) -> ImageInstance:
    if use_header:
        timestamp = time_to_timestamp(msg.header.stamp)
    else:
        timestamp = timestamp
    return ImageInstance(data=bridge.compressed_imgmsg_to_cv2(msg), metadata=BaseMetadata(timestamp=timestamp, index=instance_index))

def image_msg_to_image_instance(msg : Image, instance_index : int = -1, timestamp : Time = Time(seconds=0, nanoseconds=0), use_header=False) -> ImageInstance:
    if use_header:
        timestamp = time_to_timestamp(msg.header.stamp)
    else:
        timestamp = timestamp
    return ImageInstance(data=bridge.imgmsg_to_cv2(msg), metadata=BaseMetadata(timestamp=timestamp, index=instance_index))

### IMAGE INSTANCE -> IMAGE MESSAGE ###

#TODO