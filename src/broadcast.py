import requests
import jsonpickle
import json 

class Broadcast:
    def __init__(self, my_ip, my_port, base_url = "http://", headers =  {'Content-type': 'application/json', 'Accept': 'text/plain'}):
        self.my_ip = my_ip
        self.my_port = my_port
        self.base_url = base_url
        self.headers = headers
        self.peers = []


    def broadcast(self, endpoint, payload):
        for ip, port in self.peers:
            # if ip != self.my_ip or port != self.my_port: 
            try:
                # print(jsonpickle.encode(payload), type(jsonpickle.encode(payload)))
                url = f'{self.base_url}{ip}:{port}/{endpoint}'
                response = requests.post(url, data=jsonpickle.encode({"data": payload}), headers=self.headers)
            
            except requests.exceptions.Timeout:
                print(f'broadcast: Request timed out')

    def add_peer(self, ip, port):
        self.peers.append((ip, port))