# geometry

**Grid maps and coordinate utilities** for 2D spatial indexing and visualization.

## Design pattern

- **`GridmapCoordinates`** — Bounds, resolution, cell centers, and edges; grid frames use **FLU** (forward, left, up) as documented on the class.
- **`Gridmap` / layers** — Dense and sparse grid layers for occupancy or scalar fields; conversions between world coordinates and grid indices live with these types.

Use this package for camera-independent 2D geometry; **`mapping`** builds higher-level map objects on top of it.
