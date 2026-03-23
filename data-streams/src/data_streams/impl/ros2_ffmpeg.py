"""Ros2 bag stream for ``ffmpeg_image_transport`` ``FFMPEGPacket`` topics."""

from typing import Any

from data_models.core.base_metadata import BaseMetadata
from data_models.impl.image_instance import ImageInstance

from data_streams.impl.ros2 import Ros2DataStream

from ros_python_conversions.ros2.ffmpeg_transport import ffmpeg_packets_to_bgr_frames


class Ros2FfmpegPacketStream(Ros2DataStream):
    """Decode OAK / low-bandwidth ``FFMPEGPacket`` topics to ``ImageInstance``."""

    def __init__(self, **data: Any) -> None:
        super().__init__(**data)
        # Pydantic v1 blocks unknown attrs; bypass for decode cache.
        object.__setattr__(self, "_bgr_frames", None)

    def make_instance(self, instance_metadata: BaseMetadata) -> ImageInstance:
        """Return the BGR frame for the given message index.

        Parameters
        ----------
        instance_metadata : BaseMetadata
            Index and timestamp for this message.

        Returns
        -------
        ImageInstance
            Decoded BGR image.

        Notes
        -----
        On first call, all packets on the topic are loaded and decoded; later
        calls are O(1). Random access by index is supported.
        """
        bgr = object.__getattribute__(self, "_bgr_frames")
        if bgr is None:
            msgs = []
            for conn, _ts, raw in self.loaded_ros2_mcap_reader.messages(
                connections=[self.connection]
            ):
                msgs.append(self.typestore.deserialize_cdr(raw, conn.msgtype))
            bgr = ffmpeg_packets_to_bgr_frames(msgs)
            object.__setattr__(self, "_bgr_frames", bgr)

        idx = instance_metadata.index
        return ImageInstance(
            data=bgr[idx],
            metadata=BaseMetadata(
                timestamp=instance_metadata.timestamp, index=idx
            ),
        )
