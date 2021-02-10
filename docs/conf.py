import os
import sys

sys.path.insert(0, os.path.abspath(".."))

from discord.ext.ipc import __version__ as version


# -- Project information -----------------------------------------------------

project = "discord-ext-ipc"
copyright = "2021, Ext-Creators"
author = "Ext-Creators"

# The full version, including alpha/beta/rc tags
release = version


# -- General configuration ---------------------------------------------------
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.intersphinx",
    "sphinx-rtd-theme",
    "sphinxcontrib_trio",
]


html_theme = "sphinx_rtd_theme"

autodoc_typehints = "none"
intersphinx_mapping = {
    "aiohttp": ("https://docs.aiohttp.org/en/stable/", None),
    "python": ("https://docs.python.org/3", None),
}

highlight_language = "python3"
master_doc = "index"
pygments_style = "friendly"
source_suffix = ".rst"
