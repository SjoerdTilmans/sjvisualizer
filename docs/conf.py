"""Sphinx configuration; runnable from any working directory."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

project = "sjvisualizer"
copyright = "2026, Sjoerd Tilmans"
author = "Sjoerd Tilmans"
release = "0.0.15"
extensions = ["sphinx.ext.autodoc", "sphinx.ext.napoleon", "sphinx.ext.viewcode", "myst_parser"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]
html_theme = "sphinx_rtd_theme"
