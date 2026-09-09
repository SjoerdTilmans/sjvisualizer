# Contributing

Install the checkout with `python -m pip install -e .`. Keep chart implementations
in `sjvisualizer/charts`, shared drawing code in `core`, and data loading in
`data`. Preserve public compatibility modules when changing internals. For a new
chart, start with `24. Empty.py`, add a self-contained numbered example, and
update the catalogue and API reference.

## Verification

Compile package and example sources:

```shell
python -m compileall -q sjvisualizer scripts Examples
python scripts/smoke_examples.py
```

The smoke runner executes all 24 numbered examples in separate processes with
`--smoke --seconds 1 --fps 5`. It requires Tk and a graphical display, and checks
initial, middle, final, and backward-seek rendering. It is not a full regression
suite and does not check visual appearance or video capture. For chart changes,
also run the affected example normally and inspect its animation.

## Documentation and distributions

```shell
python -m pip install -r docs/requirements.txt
python -m sphinx -b html docs docs/_build/html
python -m pip install build
python -m build
```

The wheel contains only the active package, logo, and map assets. The source
archive also includes documentation and numbered demos. `Examples/` contains
additional repository-only Excel/image examples. Map rebuild scripts consume
local source datasets; follow the [map guide](maps.md).

Before opening a pull request, review `git diff --check` and `git status`.
Environments, IDE state, caches, build output, and recorded videos are ignored.
Keep personal datasets and credentials out of commits. Ignore rules do not
remove files from earlier commits; review existing history before publishing
a formerly private repository. Keep the version in `setup.py` and
`docs/conf.py` synchronized when preparing a release.
