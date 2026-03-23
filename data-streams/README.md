# data-streams

**Iterators and random access** over chronological sensor data for offline analysis.

## Design pattern

- **`DataStream`** (in `core/data_stream.py`) — Abstract chronological API: `timestamps`, `get_instance`, nearest-by-time queries, optional interpolation flags, etc.
- **`impl/ros2.py` — `Ros2DataStream`** — Backs a stream from a ROS 2 bag (directory or `.mcap`) and a single topic; deserializes with `rosbags` and calls a **`decode_fn(msg, index, timestamp)`** that returns a `BaseInstance`.
- **`impl/ros2_ffmpeg.py` — `Ros2FfmpegPacketStream`** — Same bag/topic wiring, but decodes **`ffmpeg_image_transport` / `FFMPEGPacket`** (e.g. H.264/HEVC) to BGR frames and returns `ImageInstance` by index.
- **`ros2_common/camera_streams.py`** — **`make_rgb_image_stream`** picks `Ros2FfmpegPacketStream` when the topic type is `FFMPEGPacket`, otherwise plain `Ros2DataStream` with RGB/compressed image decoding. **`make_depth_image_stream`** wires depth `sensor_msgs/Image` → float depth grids via **`ros-python-conversions`**.
- **`collection_streams/`** — Higher-level streams that combine multiple bag topics (e.g. TF-derived poses).

Implementing a new source: subclass `DataStream`, supply ordered timestamps, and implement **`make_instance`** (and any metadata helpers your base class expects).
