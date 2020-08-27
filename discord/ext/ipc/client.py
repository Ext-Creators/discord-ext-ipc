import asyncio
import json
            
class Client:
    def __init__(self, host, port, secret_key):
        self.host = host
        self.port = port
        
        self.secret_key = secret_key
    
    async def request(self, endpoint, **kwargs):
        reader, writer = await asyncio.open_connection(self.host, self.port)
        
        data = {"endpoint": endpoint, "data": kwargs, "headers": {"Authentication": self.secret_key}}
        writer.write(json.dumps(data).encode("utf-8"))
        
        await writer.drain()
        
        while True:
            data = await reader.read(1024)
            
            if not data:
                return await writer.close()
            
            return data.decode("utf-8")