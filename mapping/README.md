# mapping

**Map abstractions** that compose **`geometry`** gridmaps (bounds, resolution, world ↔ grid indexing).

## Design pattern

- Map types hold a **`GridmapCoordinates`** (and optional odometry or layer data depending on the implementation).
- Visualization hooks may delegate to **`visualization`** or local drawing helpers.

Extend here when you need named maps with consistent coordinate frames rather than ad hoc NumPy grids.
