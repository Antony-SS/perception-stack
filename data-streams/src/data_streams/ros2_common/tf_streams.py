from data_streams.impl.ros2 import Ros2DataStream, make_ros2_data_stream
from ros_python_conversions.ros2.tf import tf_message_to_tf_instance

from rosbags.rosbag2 import Reader

def make_tf_stream(ros2_mcap_path: str,
                   topic_name: str,
                   use_header_timestamps: bool = False) -> Ros2DataStream:
    """Create a ROS2 data stream for TF (transform) messages.
    
    Parameters
    ----------
    ros2_mcap_path : str
        Path to the ROS2 MCAP bag file
    topic_name : str
        Topic name for TF messages (typically '/tf' or '/tf_static')
    use_header_timestamps : bool
        Whether to use timestamps from message headers (default: False)
        
    Returns
    -------
    Ros2DataStream
        A data stream that yields TFInstance objects
        
    Notes
    -----
    This stream reads tf2_msgs/msg/TFMessage messages from the specified topic.
    Each message contains an array of TransformStamped messages, which are
    converted to a single TFInstance containing all transforms.
    
    Note: TFMessage doesn't have a header, so use_header_timestamps should
    typically be False. The decode function will extract timestamps from the
    individual TransformStamped headers if needed.
    """
    
    return make_ros2_data_stream(
        ros2_mcap_path=ros2_mcap_path,
        topic=topic_name,
        decode_fn=tf_message_to_tf_instance,
        interpolable=False,
        use_header_timestamps=use_header_timestamps
    )

