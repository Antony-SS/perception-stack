
from data_streams.ros2_common.camera_streams import make_rgb_image_stream
from data_streams.ros2_common.pose_streams import make_odometry_stream

import os
import cv2
from tqdm import tqdm
from datetime import datetime

def extract_rgb_frames(bag_path : str, image_topic_name : str, output_dir : str, overlay_timestamps : bool = True, overlay_pose : bool = True, pose_topic_name : str = "/pose", use_header_timestamps : bool = True) -> None:

    image_stream = make_rgb_image_stream(ros2_mcap_path=bag_path, topic_name=image_topic_name, use_header_timestamps=use_header_timestamps)
    pose_stream = None

    if overlay_pose:
        pose_stream = make_odometry_stream(ros2_mcap_path=bag_path, topic_name=pose_topic_name, use_header_timestamps=use_header_timestamps)

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    if len(image_stream) == 0:
        raise ValueError(f"No images found in bag {bag_path} and topic {image_topic_name}")

    if pose_stream is not None:
        if len(pose_stream) == 0:
            raise ValueError(f"No poses found in bag {bag_path} and topic {pose_topic_name} to overlay on images")


    for index, image_instance in tqdm(enumerate(image_stream.iterate()), total=len(image_stream)):
        image = image_instance.data
        index = image_instance.index
        timestamp = image_instance.timestamp

        if overlay_timestamps:
            timestamp_str = datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")
            cv2.putText(image, timestamp_str, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

        if overlay_pose:
            pose_instance = pose_stream.get_nearest_instance(timestamp)
            pose = pose_instance.pose
            translation = pose.translation
            rotation = pose.euler_flu_degrees()
            cv2.putText(image, f"Translation: {translation}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
            cv2.putText(image, f"Rotation: {rotation}", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

        cv2.imwrite(f"{output_dir}/{index:06d}.png", image)