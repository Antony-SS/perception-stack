# perception-stack
A lightweight toolbox for offline analysis of time series sensor data with a focus on robotics and vision applications.  Built around ros2 and leans on numpy, scipy, and cv2. 

_Many of the design philosophies in this repository are inspired by my first boss, Michael, who taught me a lot of what I know.  Thank you._

## Design Philosphy

All times series data is made up of a series of instances with a timestamp and index, where each instance is associated with piece of data, like an image.  With this in mind, everything in this repo is built around the `DataStream` and `BaseInstance` classes.  

The `DataStream` class provides a structured framework for chronological iteration, as well as acessing instances via timestamp/index.  Implementing a subclass of a `DataStream` is as simple as defining the `timestamps` and `make_instance` functions!

#### Ros <-> Python 
When working from ros2 bags, I define a conversion layer between ros messages and the `BaseInstance` data structure because I prefer to work with simple python datastructures.  See `ros-python-conversions` for examples.  It makes code much more readable.  All credit to my first boss, who introduced me to this design philosophy.

## Prerequisites

- ROS2 (Humble, Iron, or compatible distribution) installed and sourced
- Python 3.9+
- pip

## Installation

1. Ensure ROS2 is installed and sourced:
   ```bash
   source /opt/ros/humble/setup.bash  # Adjust for your ROS2 distribution
   ```

2. Install ROS2 Python packages (if not already installed):
   ```bash
   sudo apt-get install -y \
       python3-rosidl-runtime-py \
       ros-humble-cv-bridge \
       ros-humble-sensor-msgs \
       ros-humble-builtin-interfaces
   ```
   (Adjust `humble` for your ROS2 distribution)

3. Run `setup.sh` script.  Remember to make it an executable!

## Usage

Example: Extract RGB frames from a ROS2 bag:
```bash
cd analysis-core/scripts
python3 run_extract_rgb_frames.py --bag_path <PATH_TO_BAG> --image_topic <IMAGE_TOPIC> --output_dir <OUTPUT_DIR>
```
