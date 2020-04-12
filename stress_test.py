from src.broadcast import Broadcast
from src.config import *

from argparse import ArgumentParser
import requests
import asyncio
import jsonpickle

parser = ArgumentParser()
parser.add_argument('-n', '--nodes', default=5, type=int, help='number of nodes running')
args = parser.parse_args()
n = args.nodes

url = f'http://{BOOTSTRAP}/get_nodes'
headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
response = requests.get(url, headers)

hosts = jsonpickle.decode(response.json())['data']

b = Broadcast('test')
for host in hosts:
    b.add_peer(host)

print("Starting the stress test...")
responses = asyncio.run(b.broadcast('stress_test', n, 'POST'))
