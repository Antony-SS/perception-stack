# perception-stack

Lightweight libraries for **offline analysis of time-indexed sensor data**, with a focus on robotics and vision. The stack assumes ROS 2 bags for replay where relevant, and uses NumPy, SciPy, and OpenCV-style workflows on the Python side.

## Packages

| Package | Role |
|--------|------|
| **data-models** | Shared Python types for stream instances (`BaseInstance`, `BaseMetadata`, etc.). |
| **data-streams** | `DataStream` API: chronological access by index/timestamp; ROS 2 bag backends. |
| **ros-python-conversions** | ROS message ↔ `data-models` instances (images, depth, TF, odometry, …). |
| **geometry** | Grid maps, coordinate frames (FLU), and related geometric helpers. |
| **mapping** | Map types built on `geometry` gridmaps. |
| **visualization** | Plotting and image helpers for maps and grids. |
| **analysis-core** | Example scripts and small tools that compose the above packages. |

## Design pattern

1. **Streams** — All time series are modeled as ordered **instances**, each with a **timestamp** and **index**. `DataStream` subclasses implement `timestamps` and `make_instance` (and optional interpolation hooks). Callers use `get_instance`, `get_nearest_instance_metadata`, `iterate`, etc.

2. **Conversion layer** — Raw ROS messages are converted to small Python objects as soon as data leaves the bag reader. That keeps downstream code independent of `rosbags` message shapes and centralizes encoding quirks (compressed RGB, depth scaling, `ffmpeg_image_transport` packets, …).

See each package README for scope and how to extend it.

## Prerequisites

- ROS 2 (Humble, Iron, or compatible) sourced in your environment when using `cv_bridge` and message types
- Python 3.9+
- pip

## Installation

1. Source ROS 2, for example:

   ```bash
   source /opt/ros/humble/setup.bash   # adjust for your distro
   ```

2. Install system ROS Python packages if needed, for example:

   ```bash
   sudo apt-get install -y \
       python3-rosidl-runtime-py \
       ros-humble-cv-bridge \
       ros-humble-sensor-msgs \
       ros-humble-builtin-interfaces
   ```

3. Run `./setup.sh` from this directory (ensure it is executable).

## Usage

Example: extract RGB frames from a bag (see `analysis-core`):

```bash
cd analysis-core/scripts
python3 run_extract_rgb_frames.py --bag_path <PATH_TO_BAG> --image_topic <TOPIC> --output_dir <OUTPUT_DIR>
```
