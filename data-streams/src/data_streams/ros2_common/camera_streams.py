from data_streams.impl.ros2 import Ros2DataStream, make_ros2_data_stream
from ros_python_conversions.ros2.raw_rgb_image import any_image_msg_to_image_instance

from rosbags.rosbag2 import Reader

def make_rgb_image_stream(ros2_mcap_path : str,
                       topic_name : str,
                       use_header_timestamps : bool = True) -> Ros2DataStream:
    
    return make_ros2_data_stream(
        ros2_mcap_path=ros2_mcap_path,
        topic=topic_name,
        decode_fn=any_image_msg_to_image_instance,
        interpolable=False,
        use_header_timestamps=use_header_timestamps
    )

#TODO: Depth camera streams, camera info streams