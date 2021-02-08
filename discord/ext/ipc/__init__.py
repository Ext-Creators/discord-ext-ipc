"""
    Copyright 2021 Ext-Creators
    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at
        http://www.apache.org/licenses/LICENSE-2.0
    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
"""

from collections import namedtuple

from discord.ext.ipc.client import Client
from discord.ext.ipc.server import Server
from discord.ext.ipc.errors import *

__version__ = "2.0.0"

_VersionInfo = namedtuple("_VersionInfo", "major minor micro releaselevel serial")
version_info = _VersionInfo(major=2, minor=0, micro=0, releaselevel="final", serial=0)
