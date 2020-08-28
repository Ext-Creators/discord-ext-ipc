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

class Client:
    def __init__(self, *, host="localhost", port=8765, secret_key=None):
        self.host = host
        self.port = port
        
        self.secret_key = secret_key
    
    async def discover(self):
        reader, writer = await asyncio.open_connection(self.host, self.port)
        
        data = {"multicast": True, "headers": {"Authentication": self.secret_key}}
        
        writer.write(json.dumps(data).encode("utf-8"))
        
        await writer.drain()
        
        while True:
            data = await reader.read(1024)
            
            if not data:
                return await writer.close()
            
            return data.decode("utf-8")
        
    async def request(self, endpoint, **kwargs):
        """Make a request to the IPC server"""
        reader, writer = await asyncio.open_connection(self.host, self.port)
        
        data = {"endpoint": endpoint, "data": kwargs, "headers": {"Authentication": self.secret_key}}
        writer.write(json.dumps(data).encode("utf-8"))
        
        await writer.drain()
        
        while True:
            data = await reader.read(1024)
            
            if not data:
                return await writer.close()
            
            return data.decode("utf-8")
