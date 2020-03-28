from src.broadcast import Broadcast

import jsonpickle
import asyncio

from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument('-n', '--nodes', default=5, type=int, help='number of nodes running')
args = parser.parse_args()
n = args.nodes
 
b = Broadcast('test')
for i in range(n):
    b.add_peer(f'127.0.0.1:500{i}')


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

