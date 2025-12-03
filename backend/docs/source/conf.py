import os
import sys

# Add the parent directory (where app/ is located) to the Python path
sys.path.insert(0, os.path.abspath('../..'))

# Configuration file for the Sphinx documentation builder.

project = 'CineBook API'
copyright = '2025, Umme Jahara Simki'
author = 'Umme Jahara Simki'
release = '1.0'

# General configuration
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',  # For better Google-style and NumPy-style docstring support
]

templates_path = ['_templates']
exclude_patterns = []

# Options for autodoc
autodoc_default_options = {
    'members': True,
    'undoc-members': True,
    'show-inheritance': True,
}

# Options for HTML output
html_theme = 'alabaster'  # or 'sphinx_rtd_theme' if installed
html_static_path = ['_static']

# Ensure that autodoc can import private modules
add_module_names = False
