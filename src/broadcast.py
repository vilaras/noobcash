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
    async def broadcast(self, endpoint, payload, method):
        tasks = []
        async with ClientSession() as session:
            for host in self.peers:
                if host != self.host: 
                    try:
                        url = f'{self.base_url}{host}/{endpoint}'
                        if method == 'POST':
                            tasks.append(self.post(url, session, payload))
                    
                        elif method == 'GET':
                            tasks.append(self.get(url, session))

                    except (aiohttp.ClientError, aiohttp.http_exceptions.HttpProcessingError,) as e:
                        print(f'aiohttp exception for {url} {e.__class__.__name__}: {e}')

                    # Catch non aiohttp related exceptions
                    except Exception as e:
                        print(f'non-aiohttp exception for {url} {e.__class__.__name__}: {e}')


            await asyncio.gather(*tasks)
            return tasks


    async def post(self, url, session, payload):
        payload = jsonpickle.encode({"data": payload})
        async with session.post(url, data=payload, headers=self.headers) as resp:
            if resp.status != 200:
                raise Exception(f'Expected status code 200, but got {resp.status_code}')
            
            return resp


    async def get(self, url, session):
        async with session.get(url, headers=self.headers) as resp:
            if resp.status != 200:
                raise Exception(f'Expected status code 200, but got {resp.status_code}')
            
            return json.dumps(json.loads(resp)['data'])
