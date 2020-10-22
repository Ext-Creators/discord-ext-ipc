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
import asyncio

import socket
import inspect

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
    """Main server class"""

    def __init__(self, bot, host, port, secret_key):
        self.bot = bot
        self.loop = bot.loop

        self.port = port
        self.host = host
        
        self.clients = {}
        self.endpoints = {}
        
        self.secret_key = secret_key
        
        self.multicast_grp = socket.gethostbyname(socket.gethostname())

        self.main_server = None
        self.multicast_server = None
    
    def route(self, name=None):
        """Used to register a coroutine as an endpoint"""
        def decorator(func):
            if not name:
                self.endpoints[func.__name__] = func
            else:
                self.endpoints[name] = func
        
        return decorator
        
    def client_connection_callback(self, cli_reader, cli_writer):
        """Callback for client connections"""
        client_id = cli_writer.get_extra_info("peername")

        def client_cleanup(future):
            try:
                future.result()
            except Exception:
                pass
        
            del self.clients[client_id]
        
        task = asyncio.ensure_future(self.client_task(cli_reader, cli_writer))
        task.add_done_callback(client_cleanup)
        
        self.clients[client_id] = task
    
    async def client_task(self, reader, writer):
        """Processes the client request"""
        while True:
            data = await reader.read(1024)
            
            if data == b"":
                return

            data = data.decode()
            parsed_json = json.loads(data)
            
            headers = parsed_json.get("headers")
            
            if not headers or not headers.get("Authentication"):
                response = {"error": "No authentication provided.", "status": 403}
            
            token = headers.get("Authentication")
            
            if token != self.secret_key:
                response = {"error": "Invalid authorization token provided.", "status": 403}
            else:
                if parsed_json.get("multicast") and parsed_json.get("multicast") is True:
                    endpoints = {}
                    for name, func in self.endpoints.items():
                        endpoints[name] = {"func_name": func.__name__}

                    response = {"multicast_grp": self.multicast_grp, "port": self.port, "endpoints": endpoints}
                else:
                    endpoint = parsed_json.get("endpoint")
                    
                    if not endpoint or not self.endpoints.get(endpoint):
                        response = {"error": 'No endpoint matching {} was found.'.format(endpoint), "status": 404}
                    else:
                        server_response = IpcServerResponse(parsed_json)
                        response = await self.endpoints[endpoint](server_response)
            
            writer.write(json.dumps(response).encode("utf-8"))
            await writer.drain()
            
            break
    
    def start(self, multicast=False):
        """Start the IPC server"""
        host = self.host if not multicast else self.multicast_grp
        server_coro = asyncio.start_server(self.client_connection_callback, host, self.port, loop=self.loop)

        self.bot.dispatch("ipc_ready")
        self.main_server = self.loop.create_task(server_coro)
        
        multicast_server = asyncio.start_server(self.client_connection_callback, host, 20000, loop=self.loop)
        self.multicast_server = self.loop.create_task(multicast_server)

    def stop(self):
        """Stop the IPC server"""
        self.main_server.cancel()
        self.multicast_server.cancel()
