# ros-python-conversions

Conversions for moving to and from ros messages/python classes (defined in data-models).  

## Motivation

Very few libraries actually work on raw ros messages, so every piece of code that interacts with ros messages would require some conversion to a more useful datastructure.  That's messy.  

A good design pattern is to maintain a conversion layer between ros messages and python objects, so we convert to python objects as we read out from rosbags.

For chronological data, we always want a timestamp and index, which is the bare minimum a python object for a given message type will hold.

## Implementing New Conversions

To implement a new conversion follow this process:

1. Create a python datastructure for the ros-message you want to interface with.  For image data, this means I convert the ros message into a python object with a timestamp, index, and np.array data field
   
2. Define conversions in `ros_python_conversions`.  See `raw_rgb_image.py` for an example.  You should define conversions for ros message -> python and from python -> ros message