from setuptools import setup
import re

with open("README.md", "r") as ld:
    long_description = ld.read()

version = ""
with open("discord/ext/ipc/__init__.py") as f:
    version = re.search(r"^__version__\s*=\s*[\'\"]([^\'\"]*)[\'\"]", f.read(), re.MULTILINE).group(1)
    
setup(
    name="discord-ext-ipc",
    author="lganwebb",
    url="https://github.com/lganWebb/discord-ext-ipc",
    version="1.0",
    packages=["discord.ext.ipc"],
    license="MIT",
    description="An IPC extension allowing for the communication between a discord.py bot and an asynchronous web-framework (i.e. Quart or aiohttp.web)",
    install_requires=["discord.py>=1.4.1"],
    python_requires=">=3.6"
)