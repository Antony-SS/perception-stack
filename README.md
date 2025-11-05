# perception-stack
A toolbox for offline analysis of timestamped sensor data with a focus on robotics and vision applications.

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