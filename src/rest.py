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
bootstrap_url = f'{base_url}{BOOTSTRAP_IP}:{BOOTSTRAP_PORT}'
headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}

app = Flask(__name__)
CORS(app)

# User Node 
node = None

'''
Params:
    ip <int>: User ip
    port <int>: User port
Returns <bool>: 
    Returns if user is the bootstrap node
'''
def im_bootstrap(ip, my_port):
    return f'{base_url}{ip}:{port}' == bootstrap_url


# Send data
#.......................................................................................

@app.route('/create_transaction', methods=['POST'])
def create_transaction():
    data = request.get_json()
    address = data["addr"]
    amount = data["amount"]

    try:
        t = node.create_transaction(address, amount)
        return jsonify("Transaction accepted!"), 200   

    except:
        return jsonify("Transaction declined"), 403


# Receive data
#.......................................................................................

@app.route('/receive_transaction', methods=['POST'])
def receive_transaction():
    print("TO TRANSACTIOOOOOOOOOOOOOOON")
    data = request.get_json()
    transaction = data["data"]

    print(jsonpickle.decode(json.dumps(transaction)))

    return jsonify("yagagro")
    # data = request.get_json()
    # transaction = data["transaction"]

    # if node.validate_transaction(transaction):
    #     node.commit_transaction(transaction)
    #     node.add_transaction_to_block(transaction)

    #     return jsonify("Transaction accepted!"), 200

    # else:
    #     return jsonify("Transaction declined"), 403

@app.route('/receive_block', methods=['POST'])
def receive_block():
    print("TO BLOOOOOOOOOOOOCK")
    data = request.get_json()
    block = data["data"]

    print(jsonpickle.decode(json.dumps(block)))

    return jsonify("yagrgaasgasegasego")
    # data = request.get_json()
    # transaction = data["transaction"]

    # if node.validate_transaction(transaction):
    #     node.commit_transaction(transaction)
    #     node.add_transaction_to_block(transaction)

    #     return jsonify("Transaction accepted!"), 200

    # else:
    #     return jsonify("Transaction declined"), 403

# Connect
#.......................................................................................

@app.route('/client_accepted', methods=['POST'])
def client_accepted():
    data = request.get_json()
    ring = data["data"]

    node.ring = jsonpickle.decode(json.dumps(ring))

    return jsonify("Thanks bootstrap!"), 200 


@app.route('/register_client', methods=['POST'])
def register_client():
    global node

    if node == None:
        # Initialize node 
        node = Node(ip, port)

        #Connect with the rest of the network
        try: 
            data = json.dumps({
                "public_key": node.wallet.public_key,
                "remote_port": port
            })

            response = requests.post(f'{bootstrap_url}/client_connect', data=data, headers=headers)

        except requests.exceptions.Timeout:
            return jsonify(f'connect_client: Request "{bootstrap_url}/connect_client" timed out'), 408


        return jsonify("You have connected successfully!"), 200

    else: 
        # Bad request
        return jsonify("You have already connected!"), 400


@app.route('/client_connect', methods=['POST'])
def client_connect():
    if im_bootstrap(ip, port):
        if node.current_id_count <= NUMBER_OF_NODES:
            data = request.get_json()
            public_key = data['public_key']
            remote_ip = request.remote_addr
            remote_port = data['remote_port']
            
            node.register_node_to_ring(public_key, remote_ip, remote_port) 
            
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
