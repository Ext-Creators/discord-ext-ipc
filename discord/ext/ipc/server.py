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
import websockets

from .errors import *

ROUTES = {}


def route(name=None):
    """Used to register a coroutine as an endpoint"""
    def decorator(func):
        if not name:
            ROUTES[func.__name__] = func
        else:
            ROUTES[name] = func

    return decorator


class IpcServerResponse:
    """Format the json data parsed into a nice object"""

    def __init__(self, data):
        self._json = data
        self.length = len(data)
        
        self.endpoint = data["endpoint"]

        for key, value in data["data"].items():
            setattr(self, key, value)
    
    def to_json(self):
        """Convert object to json"""
        return self._json
    
    def __repr__(self):
        return "<IpcServerResponse length={0.length}>".format(self)

    def __str__(self):
        return self.__repr__()


class Server:
    def __init__(self, bot, host: str = "localhost", port: int = 10000, secret_key: str = None):
        self.bot = bot
        self.loop = bot.loop

        self.host = host
        self.port = port

        self._server_coro = None

        self.endpoints = {}

        self.bot.dispatch("ipc_ready")

    def route(self, name=None):
        """Used to register a coroutine as an endpoint"""
        def decorator(func):
            if not name:
                self.endpoints[func.__name__] = func
            else:
                self.endpoints[name] = func

        return decorator

    def update_endpoints(self):
        self.endpoints = {
            **self.endpoints,
            **ROUTES
        }

        ROUTES = {}

    async def handle_accept(self, websocket, _):
        async for message in websocket:
            request = json.loads(message)
            endpoint = request.get("endpoint")

            if not endpoint or endpoint not in self.endpoints:
                response = {"error": "Invalid or no endpoint given.", "code": 400}
            else:
                server_response = IpcServerResponse(request)
                attempted_cls = self.bot.cogs.get(self.endpoints[endpoint].__qualname__.split(".")[0])

                if attempted_cls:
                    arguments = (attempted_cls, server_response)
                else:
                    arguments = (server_response,)

                try:
                    ret = await self.endpoints[endpoint](*arguments)
                    response = ret
                except Exception as error:
                    self.bot.dispatch("ipc_error", error)

                    response = {"error": "IPC route raised error of type {}".format(type(error).__name__), "code": 500}

            try:
                await websocket.send(json.dumps(response))
            except TypeError as error:
                if str(error).startswith("Object of type") and str(error).endswith("is not JSON serializable"):
                    error_response = "IPC route returned values which are not able to be sent over sockets." \
                                     " If you are trying to send a discord.py object," \
                                     " please only send the data you need."

                    response = {
                        "error": error_response,
                        "code": 500
                    }

                    await websocket.send(json.dumps(response))

                    raise JSONEncodeError(error_response)

    def start(self):
        """Start teh IPC server"""
        self._server_coro = websockets.serve(self.handle_accept, self.host, self.port)

        self.loop.run_until_complete(self._server_coro)
