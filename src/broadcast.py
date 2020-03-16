import requests
import jsonpickle
import json 

class Broadcast:
    def __init__(self, host, base_url = "http://", headers =  {'Content-type': 'application/json', 'Accept': 'text/plain'}):
        self.host = host
        self.base_url = base_url
        self.headers = headers
        self.peers = []


    def broadcast(self, endpoint, payload):
        for host in self.peers:
            if host != self.host: 
                try:
                    url = f'{self.base_url}{host}/{endpoint}'
                    response = requests.post(url, data=jsonpickle.encode({"data": payload}), headers=self.headers)
            
                    if response.status_code != 200:
                        print(f'Something went wrong with {url} request')

                except requests.exceptions.Timeout:
                    print(f'broadcast: Request timed out')

    def add_peer(self, host):
        self.peers.append(host)