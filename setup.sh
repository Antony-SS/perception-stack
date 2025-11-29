#!/bin/bash
set -e

echo "Setting up perception-stack..."

# Check if ROS2 is sourced
if [ -z "$ROS_DISTRO" ]; then
    echo "Warning: ROS2 environment not detected. Please source ROS2 setup.bash first."
    echo "Example: source /opt/ros/humble/setup.bash"
    exit 1
fi

echo "ROS2 distribution: $ROS_DISTRO"

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Install local packages
echo "Installing local packages..."
pip install -e ./data-models
pip install -e ./data-streams
pip install -e ./ros-python-conversions
pip install -e ./analysis-core
pip install -e ./mapping
pip install -e ./geometry
pip install -e ./visualization

echo "Installation complete!"
