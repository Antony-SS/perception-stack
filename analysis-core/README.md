# analysis-core

Small **scripts and utilities** that wire **`data-streams`** and **`ros-python-conversions`** for concrete offline tasks (e.g. exporting frames from bags).

## Design pattern

- Keep **library logic** in `data-streams` / `data-models` / `ros-python-conversions`.
- Use this package for **entry points** (`scripts/`), one-off pipelines, and examples that depend on OpenCV and tqdm but should not bloat the core stream libraries.

See `scripts/` for runnable examples.
