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
import socket

from .errors import *


class Node:
    def __init__(self, client, data):
        self.client = client
        self._json = data
        
        self.ip = data.get("multicast_grp")
        self.port = data.get("port")
        self.endpoints = data.get("endpoints")
    
    def get_json(self):
        """Convert object to json"""
        return self._json

    async def request(self, endpoint, **kwargs):
        if endpoint not in self.endpoints.keys():
            raise NoEndpointFoundError("Endpoint \"{}\" not found".format(endpoint))
        
        return await self.client.request(endpoint, self.port, **kwargs)
    
    def __str__(self):
        return str(self.get_json())

class Client:
    """Main client class, used for delivering data from the web server to the bot"""

    def __init__(self, *, host="localhost", secret_key=None):
        self.host = host
        self.secret_key = secret_key
        
        self.nodes = {}
    
    async def discover(self):
        """Get the first node found on your network"""

        response = await self.request(None, 20000, multicast=True)
        
        if not response:
            print("No node")
            return None

        node = Node(self, response)
        self.nodes[node.port] = node

        return node
        
    async def request(self, endpoint, port, **kwargs):
        """Make a request to the IPC server"""
        try:
            reader, writer = await asyncio.open_connection(self.host, port)

            if kwargs.get("multicast") and kwargs.get("multicast") is True:
                data = {"multicast": True, "data": {"ping": 1}, "headers": {"Authentication": self.secret_key}}
            else:
                data = {"endpoint": endpoint, "data": kwargs, "headers": {"Authentication": self.secret_key}}

            writer.write(json.dumps(data).encode("utf-8"))
            
            await writer.drain()
            
            while True:
                data = await reader.read(1024)

                if not data:
                    writer.close()
                    return await writer.wait_closed()
                
                break
            
            to_ret = json.loads(data.decode("utf-8"))
            
            if to_ret == "null":
                return None
            
            writer.close()
            await writer.wait_closed()

            return to_ret
        except ConnectionRefusedError:
            raise ServerConnectionRefusedError("No server found for ({}, {}), or server isn't accepting connections.".format(self.host, port))
