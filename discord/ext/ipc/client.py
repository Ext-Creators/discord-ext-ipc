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

import asyncio
import json
import typing
import aiohttp

from errors import *


class Client:
    def __init__(self, host: str = "localhost", port: int = None, secret_key: typing.Union[str, bytes] = None):
        self.loop = asyncio.get_event_loop() or asyncio.new_event_loop()

        self.secret_key = secret_key

        self.host = host
        self.port = port

        self.session = None

        self.websocket = None
        self.multicast = None

        self.loop.run_until_complete(self.init_sock())

        self.reconnect_interval = 5

    async def init_sock(self):
        """Initialise the WebSocket"""
        self.session = aiohttp.ClientSession()

        if not self.port:
            self.multicast = await self.session.ws_connect(f"ws://{self.host}:20000", autoping=False)
            await self.multicast.send_str(json.dumps({"connect": True, "headers": {"Authorization": self.secret_key}}))
            recv = await self.multicast.receive()

            if recv.type in (aiohttp.WSMsgType.CLOSE, aiohttp.WSMsgType.CLOSED):
                raise NotConnected("Multicast server connection failed.")

            port_data = json.loads(recv.data)
            self.port = port_data["port"]

        self.websocket = await self.session.ws_connect(f"ws://{self.host}:{self.port}", autoping=False)
        print(f"Client connected to ws://{self.host}:{self.port}")

    async def request(self, endpoint: str, **kwargs):
        """Send a request to the server"""
        fmt = {"endpoint": endpoint, "data": kwargs, "headers": {"Authorization": self.secret_key}}

        await self.websocket.send_str(json.dumps(fmt))
        recv = await self.websocket.receive()

        if recv.type == aiohttp.WSMsgType.CLOSED:
            return {"error": "IPC Server Unreachable, restart client process.", "code": 500}

        return json.loads(recv.data)
