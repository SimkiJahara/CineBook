import os
import sys

# -------------------- [START] Added for Autodoc and Module Path --------------------
# 1. Add the project root directory to the Python path.
# This allows Sphinx to import your modules (the 'app' folder is one level up from 'docs').
# Assuming conf.py is in /docs, '..' refers to the project root containing the 'app' directory.
sys.path.insert(0, os.path.abspath('../../'))
# -------------------- [END] Added for Autodoc and Module Path ----------------------


# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'CineBook'
copyright = '2025, Nafisa'
author = 'Nafisa'
release = '1.0.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

# 2. Add the required extensions for documentation generation and style.
extensions = [
    'sphinx.ext.autodoc',             # Core extension to document Python code
    'sphinx.ext.napoleon',            # Supports Google and NumPy style docstrings
    'sphinx_autodoc_typehints',       # Better rendering of Python type hints
    'sphinx.ext.viewcode',            # Links to the source code
    # 'myst_parser',                  # Uncomment if you want to use Markdown syntax in .rst files
]

templates_path = ['_templates']
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

# 3. Change the visual theme to the Read the Docs theme.
html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

# -------------------- [Optional] Autodoc Customization --------------------
# Show members inherited from base classes (like Pydantic's BaseModel or SQLAlchemy's Base)
autodoc_inherit_docstrings = True
# Display documentation in the order it appears in the source code
autodoc_member_order = 'bysource'