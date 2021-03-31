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

import logging
from typing import Union

import aiohttp.web
from discord.ext.ipc.errors import *

log = logging.getLogger(__name__)


def route(name: str = None):
    """
    Used to register a coroutine as an endpoint when you don't have
    access to an instance of :class:`.Server`

    .. deprecated:: 2.1.0

    Parameters
    ----------
    name: str
        The endpoint name. If not provided the method name will be
        used.
    """

    def decorator(func):
        cog_name = func.__qualname__.split(".")[0]

        if not name:
            Server.ROUTES[func.__name__] = func
        else:
            Server.ROUTES[name] = func

        setattr(func, "__ipc_cog_ref__", cog_name)

        return func

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
    """The IPC server. Usually used on the bot process for receiving
    requests from the client.

    Attributes
    ----------
    bot: :class:`~discord.ext.commands.Bot`
        Your bot instance
    host: str
        The host to run the IPC Server on. Defaults to localhost.
    port: int
        The port to run the IPC Server on. Defaults to 8765.
    secret_key: str
        A secret key. Used for authentication and should be the same as
        your client's secret key.
    do_multicast: bool
        Turn multicasting on/off. Defaults to True
    multicast_port: int
        The port to run the multicasting server on. Defaults to 20000
    pass_kwargs: bool
        Whether to use kwargs for ipc routes instead of the IpcServerResponse object. Defaults to False
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
        pass_kwargs: bool = False,
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

        self.pass_kwargs = pass_kwargs

        self.endpoints = {}

    def add_cog(self, cog):
        """Register a cog which has IPC listeners within it.

        .. versionadded:: 2.1.0

        Parameters
        ----------
        cog: :class:`~discord.ext.commands.Cog`
            The cog to register.
        """
        self.bot.add_cog(cog)

        for method in dir(cog):
            method = getattr(cog, method)

            if hasattr(method, "__ipc_route_name__"):
                self.endpoints[method.__ipc_route_name__] = method

    def route(self, name: str = None):
        """Used to register a coroutine as an endpoint when you have
        access to an instance of :class:`.Server`.

        Parameters
        ----------
        name: str
            The endpoint name. If not provided the method name will be used.
        """

        def decorator(func):
            if not name:
                self.endpoints[func.__name__] = func
            else:
                self.endpoints[name] = func

            return func

        return decorator

    @staticmethod
    def listener(name: str = None):
        """Used to register a coroutine as an endpoint when you
        do not have access to an instance of :class:`.Server`.

        .. versionadded:: 2.1.0

        Parameters
        ----------
        name: str
            The endpoint name. If not provided the method name will be used.
        """

        def decorator(func):
            setattr(func, "__ipc_route_name__", name or func.__name__)

            return func

        return decorator

    def update_endpoints(self):
        """Called internally to update the server's endpoints for cog routes.

        .. deprecated:: 2.1.0
        """
        self.endpoints = {**self.endpoints, **self.ROUTES}

        self.ROUTES = {}

    @staticmethod
    async def __handle_route(method: callable, data: Union[IpcServerResponse, dict], cog = None):
        args = []

        if cog:
            args.append(cog)

        if isinstance(data, IpcServerResponse):
            result = await method(*args, data)
        else:
            result = await method(*args, **data)

        return result

    async def handle_accept(self, request: aiohttp.web.Request):
        """Handles websocket requests from the client process.

        Parameters
        ----------
        request: :class:`~aiohttp.web.Request`
            The request made by the client, parsed by aiohttp.
        """
        log.info("Incoming request to IPC Server.")

        self.update_endpoints()

        websocket = aiohttp.web.WebSocketResponse()
        await websocket.prepare(request)

        async for message in websocket:
            request = message.json()

            log.debug("IPC Server < %r", request)

            endpoint = request.get("endpoint")

            headers = request.get("headers")

            if not headers or headers.get("Authorization") != self.secret_key:
                log.info(
                    "Received unauthorized request (Invalid or no token provided)."
                )
                response = {"error": "Invalid or no token provided.", "code": 403}
            else:
                if not endpoint or endpoint not in self.endpoints:
                    log.info("Received invalid request (Invalid or no endpoint given).")
                    response = {"error": "Invalid or no endpoint given.", "code": 400}
                else:
                    if self.pass_kwargs:
                        server_response = request["data"]
                    else:
                        server_response = IpcServerResponse(request)

                    try:
                        endpoint_meth = self.endpoints[endpoint]

                        if hasattr(endpoint_meth, "__ipc_cog_ref__"):
                            cog = self.bot.get_cog(endpoint_meth.__ipc_cog_ref__)

                            response = await self.__handle_route(endpoint_meth, server_response, cog)
                        else:
                            response = await self.__handle_route(endpoint_meth, server_response)

                    except Exception as error:
                        log.error(
                            "Received error while executing %r with %r",
                            endpoint,
                            request,
                        )
                        self.bot.dispatch("ipc_error", endpoint, error)

                        response = {
                            "error": "IPC route raised error of type {}".format(
                                type(error).__name__
                            ),
                            "code": 500,
                        }

            try:
                await websocket.send_json(response)
                log.debug("IPC Server > %r", response)
            except TypeError as error:
                if str(error).startswith("Object of type") and str(error).endswith(
                    "is not JSON serializable"
                ):
                    error_response = (
                        "IPC route returned values which are not able to be sent over sockets."
                        " If you are trying to send a discord.py object,"
                        " please only send the data you need."
                    )
                    log.error(error_response)

                    response = {"error": error_response, "code": 500}

                    await websocket.send_json(response)
                    log.debug("IPC Server > %r", response)

                    raise JSONEncodeError(error_response)

    async def handle_multicast(self, request: aiohttp.web.Request):
        """Handles multicasting websocket requests from the client.

        Parameters
        ----------
        request: :class:`~aiohttp.web.Request`
            The request made by the client, parsed by aiohttp.
        """
        log.info("Incoming request to Multicast Server.")
        websocket = aiohttp.web.WebSocketResponse()
        await websocket.prepare(request)

        async for message in websocket:
            request = message.json()

            log.debug("Multicast Server < %r", request)

            headers = request.get("headers")

            if not headers or headers.get("Authorization") != self.secret_key:
                response = {"error": "Invalid or no token provided.", "code": 403}
            else:
                response = {
                    "message": "Connection success",
                    "port": self.port,
                    "code": 200,
                }

            log.debug("Multicast Server > %r", response)

            await websocket.send_json(response)

    async def __start(self, application, port):
        """Start both servers"""
        runner = aiohttp.web.AppRunner(application)
        await runner.setup()

        site = aiohttp.web.TCPSite(runner, self.host, port)
        await site.start()

    def start(self):
        """Starts the IPC server."""
        self.bot.dispatch("ipc_ready")

        self._server = aiohttp.web.Application()
        self._server.router.add_route("GET", "/", self.handle_accept)

        if self.do_multicast:
            self._multicast_server = aiohttp.web.Application()
            self._multicast_server.router.add_route("GET", "/", self.handle_multicast)

            self.loop.run_until_complete(
                self.__start(self._multicast_server, self.multicast_port)
            )

        self.loop.run_until_complete(self.__start(self._server, self.port))
