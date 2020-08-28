import asyncio
import json

import socket

class Client:
    def __init__(self, host, port, secret_key):
        self.host = host
        self.port = port
        
        self.secret_key = secret_key
        
        self.multicast_group = (socket.gethostbyname(socket.gethostname()), 20000)
    
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
