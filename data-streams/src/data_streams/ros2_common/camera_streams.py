from data_streams.impl.ros2 import Ros2DataStream, make_ros2_data_stream
from data_streams.impl.ros2_ffmpeg import Ros2FfmpegPacketStream
from ros_python_conversions.ros2.ffmpeg_transport import is_ffmpeg_packet_msgtype
from ros_python_conversions.ros2.depth_image import any_depth_image_msg_to_image_instance
from ros_python_conversions.ros2.raw_rgb_image import any_image_msg_to_image_instance


def make_rgb_image_stream(
    ros2_mcap_path: str,
    topic_name: str,
    use_header_timestamps: bool = True,
):
    """Open an RGB image stream (raw, compressed, or FFMPEGPacket transport).

    Parameters
    ----------
    ros2_mcap_path : str
        Path to rosbag2 (directory or ``.mcap``).
    topic_name : str
        Image topic.
    use_header_timestamps : bool, optional
        Use message header time when True.

    Returns
    -------
    Ros2DataStream
        ``Ros2FfmpegPacketStream`` for ``ffmpeg_image_transport`` / OAK
        low-bandwidth topics; otherwise standard ``Ros2DataStream``.
    """
    base = make_ros2_data_stream(
        ros2_mcap_path=ros2_mcap_path,
        topic=topic_name,
        decode_fn=any_image_msg_to_image_instance,
        interpolable=False,
        use_header_timestamps=use_header_timestamps,
    )
    if base.connection is not None and is_ffmpeg_packet_msgtype(base.connection.msgtype):
        return Ros2FfmpegPacketStream(
            ros2_mcap_path=ros2_mcap_path,
            loaded_ros2_mcap_reader=base.loaded_ros2_mcap_reader,
            decode_fn=base.decode_fn,
            topic=topic_name,
            interpolable=False,
            use_header_timestamps=use_header_timestamps,
        )
    return base


# TODO: camera info streams


def make_depth_image_stream(
    ros2_mcap_path: str,
    topic_name: str,
    use_header_timestamps: bool = True,
) -> Ros2DataStream:
    """Open a depth image stream (``sensor_msgs/Image``)."""
    return make_ros2_data_stream(
        ros2_mcap_path=ros2_mcap_path,
        topic=topic_name,
        decode_fn=any_depth_image_msg_to_image_instance,
        interpolable=False,
        use_header_timestamps=use_header_timestamps,
    )
