# Framework performance review

Scope: the migrated `sjvisualizer/` package, including the playback loop,
subplot lifecycle, shared axes, data handling, line/bar charts and static elements.

## Changes

- Line charts map point histories with NumPy instead of calling Python axis
  projection methods twice per point. All existing points are retained.
- Axis ticks share one font per axis. Unchanged ticks skip geometry/text
  updates; already-hidden ticks do no Tk work. Visible ticks still raise their
  lines to preserve layering. Newly allocated ticks initialize their canvas
  items correctly and retain the configured tick length.
- Date ticks use the effective sticky limits, and position calculations no
  longer modify an all-zero axis's limits.
- Playback no longer repacks the widget or prints FPS every frame by default.
  Timing uses a monotonic clock. Duplicate subplot registration and repeated
  automatic logo insertion are prevented.
- Recording writes every frame directly, including the first two previously
  skipped frames. It uses canvas-relative screen coordinates, defaults to the
  canvas dimensions, validates the encoder and releases it if rendering fails.
  OpenCV loads only when recording. Screenshot buffering and fixed one-second
  startup/shutdown sleeps are removed.
- Data cache keys include the resolved source path, source modification time
  and size, frame count, tail count, log scaling and a cache format version.
  Pickle writes are atomic; corrupted caches are rebuilt; cache hits restore
  `dt`. Numeric column labels work. Interpolation operates on numeric columns.
- Line charts given `root=` initialize their state before drawing. Subplots
  using an SJVisualizer canvas inherit its color mapping unless explicitly
  overridden. Empty charts and invalid bar counts fail with clear errors.
- Bars avoid rereading rectangle geometry they just calculated and repeatedly
  deleting items that are already absent.

## Behavior changes

Use `canvas.play(..., show_fps=True)` to restore per-frame FPS output.
Recording width/height now default to the canvas size; explicit dimensions
still define the capture rectangle. Playback remains synchronous and paced.

Data caching writes pickle only by default. Set
`DataHandler(..., cache_excel=True)` for an additional Excel export.
`cache_location` points at the selected cache format. Old caches are retained
on disk but ignored because their filenames do not identify all settings.
`cache=False` does not create a cache directory. The legacy extra seven frames
and default tail of 180 frames remain unchanged. Duplicate or missing source
timestamps now raise `ValueError` instead of failing during reindexing.

## Validation and limitations

Run the numbered examples with `--smoke` as described in
[contributing](contributing.md). The former regression tests and benchmark
scripts are not present in this checkout; historical timings are omitted.

Playback owns a synchronous loop with `tk.update()`. Line histories send the
complete path to Tk each frame, so long animations can become expensive.
Screen capture requires a visible, unobscured window. Offscreen video export
and interactive pause/stop controls are not currently provided.
