"""Sphinx configuration."""

from datetime import datetime

project = "Tuya quirks library"
author = "Home Assistant (created and maintained by @epenet)"
copyright = f"{datetime.now().year}, {author}"
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx_click",
    "myst_parser",
]
autodoc_typehints = "description"
html_theme = "furo"
