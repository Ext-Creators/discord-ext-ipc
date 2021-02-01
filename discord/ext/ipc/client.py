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

import asyncio
import json
import typing
import aiohttp

from discord.ext.ipc.errors import *


class Client:
    """Handles webserver side requests to the bot process.

    :param host: The IP or host of the IPC server, defaults to localhost
    :type host: ``str``, optional
    :param port: The port of the IPC server. If not supplied the port will be found automatically, defaults to None
    :type port: ``int``, optional
    :param secret_key: The secret key for your IPC server. Must match the server secret_key or requests will not go ahead, defaults to None
    :type secret_key: ``Union[str, bytes]``, optional
    """

    def __init__(
        self,
        host: str = "localhost",
        port: int = None,
        multicast_port: int = 20000,
        secret_key: typing.Union[str, bytes] = None,
    ):
        """Constructor"""
        self.loop = asyncio.get_event_loop()

        self.secret_key = secret_key

        self.host = host
        self.port = port

        self.session = None

        self.websocket = None
        self.multicast = None

        self.multicast_port = multicast_port

    async def init_sock(self):
        """Attempts to connect to the server

        :return: The websocket connection to the server
        :rtype: ``Websocket``
        """
        self.session = aiohttp.ClientSession()

        if not self.port:
            self.multicast = await self.session.ws_connect(
                f"ws://{self.host}:{self.multicast_port}", autoping=False
            )
            await self.multicast.send_str(
                json.dumps(
                    {"connect": True, "headers": {"Authorization": self.secret_key}}
                )
            )
            recv = await self.multicast.receive()

            if recv.type in (aiohttp.WSMsgType.CLOSE, aiohttp.WSMsgType.CLOSED):
                raise NotConnected("Multicast server connection failed.")

            port_data = json.loads(recv.data)
            self.port = port_data["port"]

        self.websocket = await self.session.ws_connect(
            f"ws://{self.host}:{self.port}", autoping=False, autoclose=False
        )
        print(f"Client connected to ws://{self.host}:{self.port}")

        return self.websocket

    async def request(self, endpoint: str, **kwargs):
        """Make a request to the IPC server process.

        :param endpoint: The endpoint to request on the server
        :type endpoint: str
        :param **kwargs: The data to send to the endpoint
        :type **kwargs: ``Any``, optional"""
        if not self.session:
            await self.init_sock()

        fmt = {
            "endpoint": endpoint,
            "data": kwargs,
            "headers": {"Authorization": self.secret_key},
        }

        await self.websocket.send_str(json.dumps(fmt))
        recv = await self.websocket.receive()

        if recv.type == aiohttp.WSMsgType.PING:
            await websocket.ping()

            return await self.request(endpoint, **kwargs)

        if recv.type == aiohttp.WSMsgType.PONG:
            return await self.request(endpoint, **kwargs)

        if recv.type == aiohttp.WSMsgType.CLOSED:
            return {
                "error": "IPC Server Unreachable, restart client process.",
                "code": 500,
            }

        return json.loads(recv.data)
