from pydantic.main import BaseModel


from typing import Any


from data_streams.ros2_common.camera_streams import make_rgb_image_stream
from data_models.impl.image_instance import ImageInstance

import os
import cv2
from tqdm import tqdm

def extract_rgb_frames(bag_path : str, image_topic_name : str, output_dir : str, use_header_timestamps : bool = True) -> None:

    data_stream = make_rgb_image_stream(ros2_mcap_path=bag_path, topic_name=image_topic_name, use_header_timestamps=use_header_timestamps)

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    if len(data_stream) == 0:
        raise ValueError(f"No images found in bag {bag_path} and topic {image_topic_name}")
        return

    print(data_stream.timestamps)

    for index, image_instance in tqdm(enumerate(data_stream.iterate()), total=len(data_stream)):
        image = image_instance.data
        index = image_instance.index
        cv2.imwrite(f"{output_dir}/{index:06d}.png", image)