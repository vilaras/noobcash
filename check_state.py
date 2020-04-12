from src.broadcast import Broadcast
from src.config import *

import jsonpickle
import asyncio
import requests

from argparse import ArgumentParser

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

responses = asyncio.run(b.broadcast('get_pending_lengths', {}, 'GET'))
pending_lengths = map(jsonpickle.decode, responses)

print("Pending lengths:\n")
for tx in pending_lengths:
    print (f'{tx["host"]} -> {tx["data"]}')

responses = asyncio.run(b.broadcast('get_orphan_lengths', {}, 'GET'))
orphan_lengths = map(jsonpickle.decode, responses)

print("\nOrphan_lengths:\n")
for tx in orphan_lengths:
    print (f'{tx["host"]} -> {tx["data"]}')

responses = asyncio.run(b.broadcast('get_blockchain_length', {}, 'GET'))
blockchain_lengths = map(jsonpickle.decode, responses)

print("\n\nBlockchain lengths:\n")
for tx in blockchain_lengths:
    print (f'{tx["host"]} -> {tx["data"]}')

