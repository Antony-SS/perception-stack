from data_streams.impl.ros2 import Ros2DataStream, make_ros2_data_stream
from ros_message_conversions.ros2.compressed_image import compressed_image_msg_to_image_snapshot
from ros_message_conversions.ros2.all_images import depth_image_msg_to_image_snapshot
from ros_message_conversions.ros2.cam_info import cam_info_msg_to_cam_info_snapshot

from rosbags.rosbag2 import Reader

def make_camera_stream(loaded_mcap : Reader,
                       topic_name : str,
                       use_header_timestamps : bool = True) -> Ros2DataStream:
    
    return make_ros2_data_stream(
        "",
        loaded_mcap=loaded_mcap,
        topic=topic_name,
        decode_fn=compressed_image_msg_to_image_snapshot,
        interpolable=False,
        use_header_timestamps=use_header_timestamps
    )

def make_depth_camera_stream(loaded_mcap: Reader,
                             topic_name: str,
                             use_header_timestamps: bool = True) -> Ros2DataStream:

    return make_ros2_data_stream(
        "",
        loaded_mcap=loaded_mcap,
        topic=topic_name,
        decode_fn=depth_image_msg_to_image_snapshot,
        interpolable=False,
        use_header_timestamps=use_header_timestamps
    )

def make_camera_info_stream(loaded_mcap : Reader,
                            topic_name : str,
                            use_header_timestamps : bool = True) -> Ros2DataStream:

    return make_ros2_data_stream(
        "",
        loaded_mcap=loaded_mcap,
        topic=topic_name,
        decode_fn=cam_info_msg_to_cam_info_snapshot,
        interpolable=False,
        use_header_timestamps=use_header_timestamps
    )
