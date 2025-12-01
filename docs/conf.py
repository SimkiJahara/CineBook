import os
import sys

# Set a flag to tell application code that Sphinx is running
os.environ['SPHINX_BUILD'] = '1'

# -------------------------------------------------------------------
# PATH SETUP: Crucial for Autodoc to find your Python code in the 'app/' directory
# '..' navigates up one level from 'docs' to the project root.
sys.path.insert(0, os.path.abspath('..')) 
# -------------------------------------------------------------------


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

# -------------------------------------------------------------------
# EXTENSIONS: Added sphinx.ext.autodoc, napoleon, typehints, and theme
# -------------------------------------------------------------------
extensions = [
    # Make sure sphinx.ext.autodoc loads before typehints
    'sphinx.ext.autodoc',
    'sphinx_autodoc_typehints',
    'sphinx.ext.napoleon', 
    'sphinx.ext.viewcode',
    # ... other extensions
]

# -------------------------------------------------------------------
# CRITICAL FIX: AGGRESSIVE MOCKING WITH sys.modules
# (ONLY external libraries are mocked; internal 'app' modules are NOT MOCKED)
# -------------------------------------------------------------------
try:
    from unittest.mock import MagicMock
except ImportError:
    from mock import Mock as MagicMock 

# External Libraries & Core Frameworks ONLY
MOCK_MODULES = [
    'sqlalchemy', 'fastapi', 'pydantic', 'typer', 'uvicorn', 
    'bcrypt', 'passlib', 'alembic', 'pydantic_settings', 
    'dnspython', 'typing_extensions', 'starlette', 'email_validator',
]

for mod_name in MOCK_MODULES:
    sys.modules[mod_name] = MagicMock()

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']


# -------------------------------------------------------------------
# AUTODOC CONFIGURATION (Optional but recommended defaults)
# -------------------------------------------------------------------
# This allows Sphinx to document members inherited from base classes (like Pydantic's BaseSettings)
autodoc_inherit_docstrings = True
# Display documentation in the order they appear in the source code
autodoc_member_order = 'bysource'
# Set the default options for autodoc directives
autodoc_default_options = {
    'members': True,
    'undoc-members': True,
    'show-inheritance': True,
    'inherited-members': True,
}

# Tell autodoc_typehints to process Pydantic types correctly
autodoc_pydantic_model_show_config = False
autodoc_pydantic_model_show_validator_members = False

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

# -------------------------------------------------------------------
# THEME: Changed default 'alabaster' to 'sphinx_rtd_theme'
# -------------------------------------------------------------------
html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']