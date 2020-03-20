# Util imports
import jsonpickle
import asyncio
import aiohttp
from aiohttp import ClientSession

class Broadcast:
    def __init__(self, host, base_url = "http://", headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}):
        self.host = host
        self.base_url = base_url
        self.headers = headers
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
                # except:
                #     print(f'Request "{url}" failed')

                # finally:
                #     for response in rs: 
                #         if response.status_code != 200:
                #             print(f'Something went wrong with {response.url} request')

                #     #Reset the session
                #     self.session = AsyncSession(n=len(self.peers))

    async def post(self, url, session, payload):
        json_payoad = jsonpickle.encode({"data": payload})
        async with session.post(url, data=json_payoad, headers=self.headers) as resp:
            if resp.status != 200:
                print(f'Something went wrong with {url} request')

            return resp
