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
import logging
import typing
import uuid
import weakref

import aiohttp
from discord.ext.ipc.errors import *

log = logging.getLogger(__name__)


class Client:
    """
    Handles webserver side requests to the bot process.

    Parameters
    ----------
    host: str
        The IP or host of the IPC server, defaults to localhost
    port: int
        The port of the IPC server. If not supplied the port will be found automatically, defaults to None
    secret_key: Union[str, bytes]
        The secret key for your IPC server. Must match the server secret_key or requests will not go ahead, defaults to None
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

        self._requests = weakref.WeakValueDictionary()
        self._queue = asyncio.Queue()
        self._worker = None
        self._sender = None

    @property
    def url(self):
        return "ws://{0.host}:{1}".format(
            self, self.port if self.multicast else self.multicast_port
        )

    async def init_sock(self):
        """Attempts to connect to the server

        Returns
        -------
        :class:`~aiohttp.ClientWebSocketResponse`
            The websocket connection to the server
        """
        log.info("Initiating WebSocket connection.")
        self.session = aiohttp.ClientSession()

        if not self.port:
            log.debug(
                "No port was provided - initiating multicast connection at %s.",
                self.url,
            )
            self.multicast = await self.session.ws_connect(self.url, autoping=False)

            payload = {"connect": True, "headers": {"Authorization": self.secret_key}}
            log.debug("Multicast Server < %r", payload)

            await self.multicast.send_json(payload)
            recv = await self.multicast.receive()

            log.debug("Multicast Server > %r", recv)

            if recv.type in (aiohttp.WSMsgType.CLOSE, aiohttp.WSMsgType.CLOSED):
                log.error(
                    "WebSocket connection unexpectedly closed. Multicast Server is unreachable."
                )
                raise NotConnected("Multicast server connection failed.")

            port_data = recv.json()
            self.port = port_data["port"]

        self.websocket = await self.session.ws_connect(
            self.url, autoping=False, autoclose=False
        )
        log.info("Client connected to %s", self.url)

        if self._worker is None:
            self._worker = self.loop.create_task(self._receive_requests())
        if self._sender is None:
            self._sender = self.loop.create_task(self._send_requests())

        return self.websocket

    async def request(self, endpoint: str, timeout: float = None, **kwargs):
        """Make a request to the IPC server process.

        Parameters
        ----------
        endpoint: str
            The endpoint to request on the server
        timeout: float
            The number of seconds to wait for a response from the server
            before timing out and raising :exc:`asyncio.TimeoutError`.
            By default this is ``None`` and waits forever.
        **kwargs
            The data to send to the endpoint

        Raises
        -------
        asyncio.TimeoutError
            If a timeout is provided and it was reached.
        """
        log.info("Requesting IPC Server for %r with %r", endpoint, kwargs)
        if not self.session:
            await self.init_sock()

        nonce = os.urandom(16).hex()

        payload = {
            "endpoint": endpoint,
            "data": kwargs,
            "headers": {"Authorization": self.secret_key},
            "nonce": nonce,
        }

        self._queue.put_nowait(payload)
        self._requests[nonce] = future = asyncio.create_future()
        return await asyncio.wait_for(future, timeout)

    async def _send_requests(self):
        while True:
            payload = await self._queue.get()
            await self.websocket.send_json(payload)
            log.debug("Client > %r", payload)

    async def _receive_requests(self):
        while True:
            recv = await self.websocket.receive()
            log.debug("Client < %r", recv)

            if recv.type == aiohttp.WSMsgType.PING:
                log.info("Received request to PING")
                await self.websocket.ping()

            elif recv.type == aiohttp.WSMsgType.PONG:
                log.info("Received PONG")

            elif recv.type == aiohttp.WSMsgType.CLOSED:
                log.error(
                    "WebSocket connection unexpectedly closed. IPC Server is unreachable. Attempting reconnection in 5 seconds."
                )

                await self.session.close()

                await asyncio.sleep(5)

                await self.init_sock()
            else:
                response = recv.json()
                nonce = response["nonce"]

                try:
                    future = self._requests[nonce]
                except KeyError:
                    log.error("Received unknown request: %r", response)
                else:
                    ret = response.get("response", response)
                    future.set_result(ret)

    async def close(self):
        """Close the connection to the websocket."""
        await self.session.close()

        if self._worker is not None:
            self._worker.cancel()
            self._worker = None
        if self._sender is not None:
            self._sender.cancel()
            self._sender = None
