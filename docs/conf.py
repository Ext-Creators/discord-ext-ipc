import os
import sys

sys.path.insert(0, os.path.abspath(".."))

from discord.ext.ipc import __version__ as release


project = "discord-ext-ipc"
copyright = "2021, Ext-Creators"
author = "Ext-Creators"


extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.intersphinx",
    "sphinx_rtd_theme",
    "sphinxcontrib_trio",
]


html_theme = "sphinx_rtd_theme"

autodoc_typehints = "none"
intersphinx_mapping = {
    "aiohttp": ("https://docs.aiohttp.org/en/stable/", None),
    "python": ("https://docs.python.org/3", None),
    "discord": ("https://discordpy.readthedocs.io/en/latest", None),
}

highlight_language = "python3"
master_doc = "index"
pygments_style = "friendly"
source_suffix = ".rst"
