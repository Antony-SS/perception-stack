"""Depth ``sensor_msgs/Image`` to 2D float grid (``ImageInstance``)."""

from __future__ import annotations

from typing import Any

import numpy as np

from data_models.core.base_metadata import BaseMetadata
from data_models.impl.image_instance import ImageInstance

from ros_python_conversions.ros2.time import time_to_timestamp

from cv_bridge import CvBridge

_bridge = None


def _get_bridge() -> CvBridge:
    """Get or create CvBridge instance (lazy-loaded).

    Returns
    -------
    CvBridge
        Shared bridge instance.
    """
    global _bridge
    if _bridge is None:
        _bridge = CvBridge()
    return _bridge


def _depth_to_float32(depth: np.ndarray, encoding: str) -> np.ndarray:
    """Map raw depth array to float32 (encoding-based scale only).

    Parameters
    ----------
    depth : ndarray
        Raw image from ``imgmsg_to_cv2(..., passthrough)``.
    encoding : str
        ``msg.encoding``.

    Returns
    -------
    ndarray
        float32, same shape. ``16UC1`` / ``mono16`` scaled by ``0.001`` (mm→m);
        all other encodings cast only.
    """
    enc = encoding.lower().replace(" ", "")
    out = depth.astype(np.float32, copy=False)
    if enc in ("16uc1", "mono16"):
        return np.multiply(out, 0.001, dtype=np.float32)
    return np.asarray(out, dtype=np.float32, order="C")


def depth_image_msg_to_image_instance(
    msg: Any,
    instance_index: int = -1,
    timestamp: float = 0.0,
    use_header: bool = False,
) -> ImageInstance:
    """Convert a depth ``sensor_msgs/msg/Image`` to a 2D float depth grid.

    No validity masking: values are whatever the message contains. Only
    ``16UC1`` / ``mono16`` get a fixed mm→m scale; other encodings are cast to
    float32 as-is.

    Parameters
    ----------
    msg : Any
        ``sensor_msgs/msg/Image`` depth message.
    instance_index : int, optional
        Instance index for metadata, by default -1.
    timestamp : float, optional
        Timestamp in seconds if ``use_header`` is False, by default 0.0.
    use_header : bool, optional
        If True, use ``msg.header.stamp`` for metadata timestamp, by default False.

    Returns
    -------
    ImageInstance
        ``data`` is float32, shape ``(H, W)``.
    """
    if use_header:
        timestamp = time_to_timestamp(msg.header.stamp)
    bridge = _get_bridge()
    depth = bridge.imgmsg_to_cv2(msg, desired_encoding="passthrough")
    enc = getattr(msg, "encoding", "") or ""
    out = _depth_to_float32(depth, enc)
    return ImageInstance(
        data=out,
        metadata=BaseMetadata(timestamp=timestamp, index=instance_index),
    )


def any_depth_image_msg_to_image_instance(
    msg: Any,
    instance_index: int = -1,
    timestamp: float = 0.0,
    use_header: bool = False,
) -> ImageInstance:
    """Decode a depth image message to a float32 ``ImageInstance``.

    Parameters
    ----------
    msg : Any
        ROS image message (``sensor_msgs/msg/Image``).
    instance_index : int, optional
        Instance index, by default -1.
    timestamp : float, optional
        Timestamp when not using header, by default 0.0.
    use_header : bool, optional
        Use message header stamp when True, by default False.

    Returns
    -------
    ImageInstance
        Float32 ``(H, W)``; see ``depth_image_msg_to_image_instance``.

    Raises
    ------
    ValueError
        If message type is not supported.
    """
    mt = msg.__msgtype__
    if mt == "sensor_msgs/msg/Image":
        return depth_image_msg_to_image_instance(
            msg,
            instance_index=instance_index,
            timestamp=timestamp,
            use_header=use_header,
        )
    raise ValueError(f"Unsupported depth image message type: {mt}")
