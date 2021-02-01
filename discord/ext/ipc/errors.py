"""
    Copyright 2020 Ext-Creators
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


class IPCError(Exception):
    """Base IPC exception class"""

    pass


class NoEndpointFoundError(IPCError):
    """Raised upon requesting an invalid endpoint"""

    pass


class ServerConnectionRefusedError(IPCError):
    """Raised upon a server refusing to connect / not being found"""

    pass


class JSONEncodeError(IPCError):
    """Raise upon un-serializable objects are given to the IPC"""

    pass


class NotConnected(IPCError):
    """Raised upon websocket not connected"""

    pass
