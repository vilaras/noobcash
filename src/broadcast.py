# Util imports
import jsonpickle
import asyncio
import aiohttp
from aiohttp import ClientSession

class Broadcast:
    def __init__(self, host):
        self.host = host
        self.base_url = "http://"
        self.headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        self.peers = []

    def add_peer(self, host):
        self.peers.append(host)

    # Perform asyncronous HTTP post request to every node in the network
    async def broadcast(self, endpoint, payload):
        tasks = []
        async with ClientSession() as session:
            for host in self.peers:
                if host != self.host: 
                    try:
                        url = f'{self.base_url}{host}/{endpoint}'
                        tasks.append(self.post(url, session, payload))
                    
                    except (aiohttp.ClientError, aiohttp.http_exceptions.HttpProcessingError,) as e:
                        print(f'aiohttp exception for {url} [{e.status}]: {e.message}')

                    # Catch non aiohttp related exceptions
                    except:
                        print("Non-aiohttp exception occured")


            await asyncio.gather(*tasks)
            
    async def post(self, url, session, payload):
        payload = jsonpickle.encode({"data": payload})
        async with session.post(url, data=payload, headers=self.headers) as resp:
            assert resp.status == 200
            return resp
