# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------
import os
import sys

# add hooks package to path:
sys.path.insert(0, os.path.abspath(".."))


# -- Project information -----------------------------------------------------
project = "hooks"
copyright = "2021, Hartree Centre - STFC"
author = "Tom Collingwood <tom.collingwood@stfc.ac.uk>"


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = ["sphinx.ext.autodoc", "sphinx_rtd_theme", "sphinx.ext.napoleon"]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "sphinx_rtd_theme"

# sphinx_rtd_theme specific options are detailed here:
# https://sphinx-rtd-theme.readthedocs.io/en/latest/configuring.html
html_theme_options = {
    "style_external_links": True,
    "logo_only": True,
    "collapse_navigation": False,
    "prev_next_buttons_location": "both",
    "style_nav_header_background": "#007681",
}

# add the Hartree Centre logo:
html_logo = "./_static/hartree_logo.png"  # located in `html_static_path`

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]

# hide the 'built with sphinx using a theme provided by readthedocs' footer:
html_show_sphinx = False

todo_include_todos = True
