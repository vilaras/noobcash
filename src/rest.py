import requests
import json
from flask import Flask, jsonify, request, render_template
from flask_cors import CORS

from node import Node
import time

import sys
#import block
#import blockchain
#import wallet
#import transaction


NUMBER_OF_NODES = 3
BOOTSTRAP = {
    'ip': '127.0.0.1',
    'port': '5000'
}

base_url = "http://"
headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}

app = Flask(__name__)
CORS(app)

this_node = Node()
#blockchain = Blockchain()
    

def im_bootstrap(my_ip, my_port):
    return my_ip == BOOTSTRAP["ip"] and my_port == BOOTSTRAP["port"]
#.......................................................................................


# get all transactions in the blockchain

@app.route('/view_transactions', methods=['GET'])
def view_transactions():
    transactions = blockchain.transactions

    response = {'transactions': transactions}
    return jsonify(response), 200


@app.route('/get_nodes', methods=['POST'])
def get_nodes():
    data = request.get_json()
    ring = data["ring"]

    # print(ring)

    return jsonify("Thanks for your cooperation"), 200 


# TODO: Fix post for many nodes
@app.route('/connect', methods=['POST'])
def connect():
    if im_bootstrap(my_ip, port):
        if this_node.current_id_count <= NUMBER_OF_NODES - 1:
            data = request.get_json()
            public_key = data['public_key']
            remote_port = data['remote_port']
            
            this_node.register_node_to_ring(public_key, request.remote_addr, remote_port)
            
            if this_node.current_id_count == NUMBER_OF_NODES - 1:
                for id, node in this_node.ring.items(): 
                    response = json.dumps({'ring': this_node.ring, "id": id})   
                    url = base_url + node["ip"] + ":" + node["port"] + "/get_nodes" 

                    try:
                        response = requests.post(url, data=response, headers=headers) 
                    except requests.exceptions.ConnectionError:
                        print("something happened")
                
            return jsonify("Welcome to our noobcash network!"), 200

        else:  
            return jsonify("ciao Italia!"), 200
        


# TODO Make it work for public IPs
# TODO Send message to last node and make bootstrap connect
if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000, type=int, help='port to listen on')
    args = parser.parse_args()
    port = str(args.port)
    my_ip = '127.0.0.1'

    #Connect with the rest of the network
    url = base_url + BOOTSTRAP["ip"] + ":" + BOOTSTRAP["port"] + "/connect"
    data = json.dumps({
        "public_key": str(this_node.wallet.public_key.exportKey('PEM')),
        "remote_port": port
    })

    if not im_bootstrap(my_ip, port):
        response = requests.post(url, data=data, headers=headers)
        print(response.json())
    
    app.run(host=my_ip, port=port)