import requests
import json 

class Broadcast:
    def __init__(self, base_url = "http://", headers =  {'Content-type': 'application/json', 'Accept': 'text/plain'}):
        self.base_url = base_url
        self.headers = headers
        self.peers = []


    def broadcast(self, endpoint, payload):
        for ip, port in self.peers:
            try:
                url = f'{self.base_url}{ip}:{port}/{endpoint}'
                response = requests.post(url, data=json.dumps(payload), headers=self.headers)
            
            except requests.exceptions.Timeout:
                print(f'broadcast: Request "{ulr}" timed out')

    def add_peer(self, ip, port):
        self.peers.append((ip, port))