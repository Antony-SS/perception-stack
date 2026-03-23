# data-models

Python types for **chronological data streams**: instances carry payload data plus **`BaseMetadata`** (timestamp, index).

## Design pattern

- **`BaseMetadata`** — Minimal identity for one sample in a stream.
- **`BaseInstance`** — Payload + metadata; concrete types live under `data_models.impl` (e.g. `ImageInstance`, pose/TF types).

Downstream code should depend on these models rather than on ROS message classes directly. Pair with **`ros-python-conversions`** at the bag boundary.
