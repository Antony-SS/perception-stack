from data_streams.ros2_common.camera_streams import make_rgb_image_stream
from data_models.impl.image_instance import ImageInstance

import os

def extract_rgb_frames(bag_path : str, image_topic_name : str, output_dir : str) -> None:

    data_stream = make_rgb_image_stream(bag_path, image_topic_name)

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for instance in data_stream:
        if isinstance(instance, ImageInstance):
            os.makedirs(output_dir, exist_ok=True)
            instance.image.save(f"{output_dir}/{instance.metadata.index}.png")