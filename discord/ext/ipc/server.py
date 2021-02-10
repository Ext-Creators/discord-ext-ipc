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

import json
import aiohttp.web

from discord.ext.ipc.errors import *


def route(name: str = None):
    """Used to register a coroutine as an endpoint when you don't have access to an instance of :class:`~discord.ext.ipc.Server`.

    Parameters
    ----------
    name: string
        The endpoint name. If not provided the method name will be used.
    """

    def decorator(func):
        if not name:
            Server.ROUTES[func.__name__] = func
        else:
            Server.ROUTES[name] = func

    return decorator


class IpcServerResponse:
    def __init__(self, data: dict):
        self._json = data
        self.length = len(data)

        self.endpoint = data["endpoint"]

        for key, value in data["data"].items():
            setattr(self, key, value)

    def to_json(self):
        return self._json

    def __repr__(self):
        return "<IpcServerResponse length={0.length}>".format(self)

    def __str__(self):
        return self.__repr__()


class Server:
    """The IPC server. Usually used on the bot process for receiving requests from the client.

    Attributes
    ----------
    bot: :class:`~discord.ext.commands.Bot`
        Your bot instance
    host: str
        The host to run the IPC Server on. Defaults to localhost.
    port: int
        The port to run the IPC Server on. Defaults to 8765.
    secret_key: str
        A secret key. Used for authentication and should be the same as your client's secret key.
    do_multicast: bool
        Turn multicasting on/off. Defaults to True
    multicast_port: int
        The port to run the multicasting server on. Defaults to 20000
    """

    ROUTES = {}

    def __init__(
        self,
        bot,
        host: str = "localhost",
        port: int = 8765,
        secret_key: str = None,
        do_multicast: bool = True,
        multicast_port: int = 20000,
    ):
        self.bot = bot
        self.loop = bot.loop

        self.secret_key = secret_key

        self.host = host
        self.port = port

        self._server = None
        self._multicast_server = None

        self.do_multicast = do_multicast
        self.multicast_port = multicast_port

        self.endpoints = {}

    def route(self, name: str = None):
        """Used to register a coroutine as an endpoint when you have access to an instance of :class:`~discord.ext.ipc.Server`.

        Parameters
        ----------
        name: string
            The endpoint name. If not provided the method name will be used.
        """

        def decorator(func):
            if not name:
                self.endpoints[func.__name__] = func
            else:
                self.endpoints[name] = func

        return decorator

    def update_endpoints(self):
        """Called internally to update the server's endpoints for cog routes."""
        self.endpoints = {**self.endpoints, **self.ROUTES}

        self.ROUTES = {}

    async def handle_accept(self, request: aiohttp.web.Reqeust):
        """Handles websocket requests from the client process.

        Parameters
        ----------
        request: :class:`~aiohttp.web.Request`
            The request made by the client, parsed by aiohttp.
        """
        self.update_endpoints()

        websocket = aiohttp.web.WebSocketResponse()
        await websocket.prepare(request)

        async for message in websocket:
            request = json.loads(message.data)
            endpoint = request.get("endpoint")

            headers = request.get("headers")

            if not headers or headers.get("Authorization") != self.secret_key:
                response = {"error": "Invalid or no token provided.", "code": 403}
            else:
                if not endpoint or endpoint not in self.endpoints:
                    response = {"error": "Invalid or no endpoint given.", "code": 400}
                else:
                    server_response = IpcServerResponse(request)
                    attempted_cls = self.bot.cogs.get(
                        self.endpoints[endpoint].__qualname__.split(".")[0]
                    )

                    if attempted_cls:
                        arguments = (attempted_cls, server_response)
                    else:
                        arguments = (server_response,)

                    try:
                        ret = await self.endpoints[endpoint](*arguments)
                        response = ret
                    except Exception as error:
                        self.bot.dispatch("ipc_error", endpoint, error)

                        response = {
                            "error": "IPC route raised error of type {}".format(
                                type(error).__name__
                            ),
                            "code": 500,
                        }

            try:
                await websocket.send_str(json.dumps(response))
            except TypeError as error:
                if str(error).startswith("Object of type") and str(error).endswith(
                    "is not JSON serializable"
                ):
                    error_response = (
                        "IPC route returned values which are not able to be sent over sockets."
                        " If you are trying to send a discord.py object,"
                        " please only send the data you need."
                    )

                    response = {"error": error_response, "code": 500}

                    await websocket.send_str(json.dumps(response))

                    raise JSONEncodeError(error_response)

    async def handle_multicast(self, request: aiohttp.web.Request):
        """Handles multicasting websocket requests from the client.

        Parameters
        ----------
        request: :class:`~aiohttp.web.Request`
            The request made by the client, parsed by aiohttp.
        """
        websocket = aiohttp.web.WebSocketResponse()
        await websocket.prepare(request)

        async for message in websocket:
            request = json.loads(message.data)

            headers = request.get("headers")

            if not headers or headers.get("Authorization") != self.secret_key:
                response = {"error": "Invalid or no token provided.", "code": 403}
            else:
                response = {
                    "message": "Connection success",
                    "port": self.port,
                    "code": 200,
                }

            await websocket.send_str(json.dumps(response))

    async def __start(self, application, port):
        """Start both servers"""
        runner = aiohttp.web.AppRunner(application)
        await runner.setup()

        site = aiohttp.web.TCPSite(runner, self.host, port)
        await site.start()

    def start(self):
        """Starts the IPC server."""
        self.bot.dispatch("ipc_ready")

        self._server = aiohttp.web.Application(loop=self.loop)
        self._server.router.add_route("GET", "/", self.handle_accept)

        if self.do_multicast:
            self._multicast_server = aiohttp.web.Application(loop=self.loop)
            self._multicast_server.router.add_route("GET", "/", self.handle_multicast)

            self.loop.run_until_complete(
                self.__start(self._multicast_server, self.multicast_port)
            )

        self.loop.run_until_complete(self.__start(self._server, self.port))
