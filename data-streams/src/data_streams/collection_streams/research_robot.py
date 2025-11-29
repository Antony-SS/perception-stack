from data_streams.ros2_common.camera_streams import make_rgb_image_stream
from data_streams.impl.ros2 import Ros2DataStream
from data_models.impl.pose_instance import PoseInstance
from data_models.core.base_metadata import BaseMetadata
from data_models.impl.transforms import Transform3D
from ros_python_conversions.ros2.tf import tf_message_to_tf_instance
from data_models.impl.tf_instance import TFInstance
import numpy as np
from scipy.spatial.transform import Rotation
from typing import Callable
from data_models.core.base_model import BaseInstance
""" Hacky datastream to recover pose from tf stream which contains many irrelevant transforms. """

class tf_static_to_pose_stream(Ros2DataStream):

    def __init__(self, ros2_mcap_path : str, tf_topic_name : str, use_header_timestamps : bool = True):
        super().__init__(ros2_mcap_path=ros2_mcap_path, topic=tf_topic_name, decode_fn=tf_message_to_tf_instance, interpolable=False, use_header_timestamps=use_header_timestamps)


    def make_instance(self, instance_metadata : BaseMetadata) -> PoseInstance:

        timestamp = instance_metadata.timestamp
        index = instance_metadata.index

        map_to_odom = self.find_nearest_map_to_odom(timestamp).transforms.get("map->odom")
        odom_to_base_footprint = self.find_nearest_odom_to_base_footprint(timestamp).transforms.get("odom->base_footprint")
        
        # Rotate the translation of the second transform by the first rotation
        rotated_translation = map_to_odom.rotation.apply(odom_to_base_footprint.translation)
        
        # Add the translations
        combined_translation = map_to_odom.translation + rotated_translation
        
        # Compose rotations
        combined_rotation = map_to_odom.rotation * odom_to_base_footprint.rotation
        
        # Create the combined transform
        global_pose = Transform3D(
            translation=combined_translation,
            rotation=combined_rotation
        )

        return PoseInstance(pose=global_pose, metadata=instance_metadata)

    def find_nearest_odom_to_base_footprint(self, timestamp : float) -> TFInstance:

        # Find the nearest tf instance
        tf_metadata = super().get_nearest_instance_metadata(timestamp)
        tf_instance = Ros2DataStream.make_instance(self, instance_metadata=tf_metadata)
        tf_index = tf_metadata.index


        found = False

        # Iterate backwards through the tf stream until we find the nearest odom to base_footprint transform
        while (not found and tf_index > 0):

            tf_metadata = super().get_instance_metadata(index=tf_index)
            tf_instance = Ros2DataStream.make_instance(self, instance_metadata=tf_metadata)

            if tf_instance.transforms.get("odom->base_footprint") is not None:
                found = True
                break
            tf_index -= 1

        if not found:
            metadata = BaseMetadata(timestamp=timestamp, index=tf_index)
            return TFInstance(metadata=metadata, transforms={"odom->base_footprint": Transform3D(translation=np.array([0.0, 0.0, 0.0]), rotation=Rotation.from_euler("xyz", [0.0, 0.0, 0.0]))})

        return tf_instance


    def find_nearest_map_to_odom(self, timestamp : float) -> TFInstance:

        # Find the nearest tf instance
        tf_metadata = super().get_nearest_instance_metadata(timestamp)
        tf_index = tf_metadata.index

        found = False
        tf_instance = None

        # Iterate backwards through the tf stream until we find the nearest odom to base_footprint transform
        while (not found and tf_index > 0):

            tf_metadata = super().get_instance_metadata(index=tf_index)
            tf_instance = Ros2DataStream.make_instance(self, instance_metadata=tf_metadata)

            if tf_instance.transforms.get("map->odom") is not None:
                found = True
                break
            tf_index -= 1

        if not found:
            metadata = BaseMetadata(timestamp=timestamp, index=tf_index)
            return TFInstance(metadata=metadata, transforms={"map->odom": Transform3D(translation=np.array([0.0, 0.0, 0.0]), rotation=Rotation.from_euler("xyz", [0.0, 0.0, 0.0]))})

        return tf_instance

def make_tf_static_to_pose_stream(ros2_mcap_path : str, tf_topic_name : str, use_header_timestamps : bool = True) -> Ros2DataStream:
    return tf_static_to_pose_stream(ros2_mcap_path=ros2_mcap_path, tf_topic_name=tf_topic_name, use_header_timestamps=use_header_timestamps)