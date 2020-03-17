# Flask imports
from flask import Flask, jsonify, request, render_template
from flask_cors import CORS

# Util imports
import requests
import json
import jsonpickle
import sys

# Class imports
from node import Node

# Configuration parameters
from config import *

base_url = "http://"
bootstrap_url = f'{base_url}{BOOTSTRAP}'
headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}

app = Flask(__name__)
CORS(app)

# User Node 
node = None

'''
Params:
    host <str>: User url
Returns <bool>: 
    Returns if user is the bootstrap node
'''
def im_bootstrap(host):
    return f'{base_url}{host}' == bootstrap_url


# Send data
#.......................................................................................

@app.route('/create_transaction', methods=['POST'])
def create_transaction():
    data = request.get_json()
    id = int(data["id"])
    amount = int(data["amount"])

    for ring_node in node.ring.values():
        if ring_node.id == id:
            address = ring_node.public_key

    try:
        t = node.create_transaction(address, amount)
        return jsonify("Transaction accepted!"), 200   

    except:
        return jsonify(f'Something went wrong with your transaction'), 403


@app.route('/balance', methods=['GET'])
def show_participants():
    # Return a list [id: public_key] for the user to see
    ring = node.ring
    data = [f'id{ring_node.id}: {ring_node.balance} NBC\n' for public_key, ring_node in ring.items()]
    reply = json.dumps(''.join(data))

    return reply
    

# Receive data
#.......................................................................................

@app.route('/receive_genesis_block', methods=['POST'])
def receive_genesis_block():
    data = request.get_json()
    block = jsonpickle.decode(json.dumps(data["data"]))

    node.add_block_to_chain(block)
    node.commit_genesis_transaction(block.transactions[0])

    return jsonify("Got it"), 200


@app.route('/receive_block', methods=['POST'])
def receive_block():
    data = request.get_json()
    block = jsonpickle.decode(json.dumps(data["data"]))

    if node.validate_block(block):
        node.add_block_to_chain(block)

        return jsonify("Block accepted!"), 200

    else: 
        return jsonify("Block declined"), 403 


@app.route('/receive_transaction', methods=['POST'])
def receive_transaction():
    data = request.get_json()
    transaction = jsonpickle.decode(json.dumps(data["data"]))

    if node.validate_transaction(transaction):
        node.commit_transaction(transaction)
        node.add_transaction_to_block(transaction)

        print(len(node.current_block.transactions))

        return jsonify("Transaction accepted!"), 200

    else: 
        return jsonify("Transaction declined"), 403



# Connect
#.......................................................................................

@app.route('/client_accepted', methods=['POST'])
def client_accepted():
    data = request.get_json()
    ring = jsonpickle.decode(json.dumps(data["data"]))

    for public_key, ring_node in ring.items():
        node.register_node_to_ring(public_key, ring_node.host, ring_node.id)

    return jsonify("Thanks bootstrap!"), 200 


@app.route('/register_client', methods=['POST'])
def register_client():
    global node

    if node == None:
        # Initialize node 
        node = Node(f'{ip}:{port}')

        #Connect with the rest of the network
        try: 
            data = json.dumps({
                "public_key": node.wallet.public_key,
                "host": f'{ip}:{port}'
            })

            url = f'{bootstrap_url}/client_connect'
            response = requests.post(url, data=data, headers=headers)

            if response.status_code != 200:
                print(f'Something went wrong with {url} request')


        except requests.exceptions.Timeout:
            return jsonify(f'connect_client: Request "{bootstrap_url}/connect_client" timed out'), 408


        return jsonify("You have connected successfully!"), 200

    else: 
        # Bad request
        return jsonify("You have already connected!"), 400


@app.route('/client_connect', methods=['POST'])
def client_connect():
    if im_bootstrap(f'{ip}:{port}'):
        if node.current_id_count <= NUMBER_OF_NODES:
            data = request.get_json()
            public_key = data['public_key']
            remote_host = data['host']
            
            node.register_node_to_ring(public_key, remote_host) 
            
            if node.current_id_count == NUMBER_OF_NODES:
                node.broadcast.broadcast("client_accepted", node.ring)
                node.initialize_network()


            return jsonify("Welcome to our noobcash network!"), 200

        else:  
            # Forbidden action
            return jsonify("Sorry, we are full..."), 403

        

# TODO Make it work for public IPs
if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000, type=int, help='port to listen on')
    args = parser.parse_args()
    port = str(args.port)
    ip = '127.0.0.1'
    
    app.run(host=ip, port=port)
