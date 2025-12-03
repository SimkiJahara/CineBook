import os
import sys

sys.path.insert(0, os.path.abspath('../..'))

# -- Project information -----------------------------------------------------

project = 'CineBook API'
copyright = '2025, Mahamudul Islam'
author = 'Mahamudul Islam'
release = '1.0'

# -- General configuration ---------------------------------------------------

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',   
]

templates_path = ['_templates']
exclude_patterns = []


autodoc_default_options = {
    'members': True,
    'undoc-members': True,
    'show-inheritance': True,
}


add_module_names = False

# -- Options for HTML output -------------------------------------------------

html_theme = 'sphinx_rtd_theme'   
html_static_path = ['_static']
