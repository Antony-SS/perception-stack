from data_streams.impl.ros2 import Ros2DataStream, make_ros2_data_stream
from ros_python_conversions.ros2.odometry import odometry_msg_to_pose_instance

def make_odometry_stream(ros2_mcap_path: str,
                         topic_name: str,
                         use_header_timestamps: bool = True) -> Ros2DataStream:
    """Create a ROS2 data stream for odometry messages.
    
    Parameters
    ----------
    ros2_mcap_path : str
        Path to the ROS2 MCAP bag file
    topic_name : str
        Topic name for odometry messages (typically '/odom')
    use_header_timestamps : bool
        Whether to use timestamps from message headers (default: True)
        
    Returns
    -------
    Ros2DataStream
        A data stream that yields PoseInstance objects
        
    Notes
    -----
    This stream reads nav_msgs/msg/Odometry messages from the specified topic.
    Each message contains a pose (position + orientation) which is extracted
    and converted to a PoseInstance. Twist (velocity) information is not included.
    """
    
    return make_ros2_data_stream(
        ros2_mcap_path=ros2_mcap_path,
        topic=topic_name,
        decode_fn=odometry_msg_to_pose_instance,
        interpolable=False,
        use_header_timestamps=use_header_timestamps
    )

