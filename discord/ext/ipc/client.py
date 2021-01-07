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
import websockets

class Client:
    def __init__(self, host: str = "localhost", port: int = 10000, loop = None):
        self.loop = loop or asyncio.get_event_loop()

        self.host = host
        self.port = port

        self.uri = "ws://{}:{}".format(self.host, self.port)

        self.ws = None

        self.loop.create_task(self.connect_ws())

    async def connect_ws(self):
        """Connect to the Websocket"""
        self.ws = await websockets.connect(self.uri)

    async def send(self, data):
        """Send data over the websocket"""
        if not self.ws:
            await self.connect_ws()

        await self.ws.send(data)

        response = await self.wait_response()

        return response

    async def request(self, endpoint, **kwargs):
        """Make a request to the IPC server"""
        fmt = {"endpoint": endpoint, "data": kwargs}

        return await self.send(json.dumps(fmt))

    async def wait_response(self):
        """Await a response from the Websocket server"""
        data = await self.ws.recv()

        try:
            data = json.loads(data)
        except TypeError:
            pass

        return data
