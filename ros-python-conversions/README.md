# ros-python-conversions

Conversions between **ROS 2 messages** and **Python types** in **`data-models`**.

## Motivation

Few algorithms should depend on raw ROS message objects end-to-end. A dedicated conversion layer keeps bag-reading code small and pushes quirks (encodings, transports, stamps) into one place.

For chronological data, each converted value should carry at least **timestamp** and **index** via `BaseMetadata` on the corresponding `BaseInstance`.

## Layout (examples)

| Module | Purpose |
|--------|---------|
| `ros2/raw_rgb_image.py` | `sensor_msgs/Image`, `CompressedImage` → `ImageInstance` (BGR). |
| `ros2/depth_image.py` | Depth `sensor_msgs/Image` → `ImageInstance` (float32 `(H, W)`; `16UC1` / `mono16` scaled mm→m). |
| `ros2/ffmpeg_transport.py` | Detect `FFMPEGPacket`; concatenate/decode H.264/HEVC with **PyAV** (`av`), with Annex-B vs length-prefixed handling and optional **`ffmpeg`** CLI fallback. |
| `ros2/time.py`, `tf.py`, `odometry.py` | Stamps and common nav message conversions. |

## Implementing new conversions

1. Define or reuse a **`data-models`** type for the payload (fields + `BaseMetadata`).
2. Add functions under `ros_python_conversions/ros2/`, following existing modules: **message → instance** for bag replay; add **instance → message** only if you need publishing or round-trips.
3. For bag streams, use your decode function as the **`decode_fn`** passed into `Ros2DataStream` (see **`data-streams`** README).

**Dependencies:** depth and RGB paths use **`cv_bridge`** (ROS environment). `FFMPEGPacket` decoding requires **`av`** (PyAV); system **`ffmpeg`** is optional for difficult bitstreams when width/height are known.
