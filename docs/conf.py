import re

project = "discord-ext-ipc"
copyright = "2021, Ext-Creators"
author = "Ext-Creators"

with open("../discord/ext/ipc/__init__.py") as stream:
    release = version = re.search(
        r"^__version__\s*=\s*[\'\"]([^\'\"]*)[\'\"]", stream.read(), re.MULTILINE
    ).group(1)


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
