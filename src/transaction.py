from collections import OrderedDict

import binascii
import base64

import Crypto
import Crypto.Random
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5

import requests
import json
from flask import Flask, jsonify, request, render_template

'''
Params:
    sender_address: To public key του wallet από το οποίο προέρχονται τα χρήματα
        Type <string>. Example "id0"
    receiver_address: To public key του wallet στο οποίο θα καταλήξουν τα χρήματα
        Type <string>. Example "id0"
    amount: το ποσό που θα μεταφερθεί
        Type <int>. Example 100
    transaction_id: το hash του transaction
        Type <string>
    transaction_inputs: list of input transaction IDs 
        Type <list int>
    transaction_outputs: list of Transaction Outputs
        Type <list Transaction_Output>
    signature: Υπογραφή του transaction
        Type <bytes>
'''
class Transaction:
    def __init__(self, sender_address, receiver_address, amount, transaction_inputs):
        self.sender_address = sender_address
        self.receiver_address = receiver_address
        self.amount = amount
        self.transaction_inputs = transaction_inputs
        self.transaction_outputs = []
        self.transaction_id = self.__hash__() 

    def __hash__(self):
        return SHA256.new(
            json.dumps(
                dict(
                    transactions_in_count = len(self.transaction_inputs),
                    transaction_inputs = self.transaction_inputs,
                    transactions_out_count = len(self.transaction_outputs),
                    transaction_outputs = [tx.__dict__ for tx in self.transaction_outputs]
                )
            ).encode()
        ).hexdigest()
        
    def set_transaction_outputs(self, transaction_outputs):
        self.transaction_outputs = transaction_outputs


    """
    Sign transaction with private key
    """
    def sign_transaction(self, private_key):
        h = SHA256.new(
            json.dumps(
                dict(
                    sender_address = self.sender_address,
                    receiver_address = self.receiver_address,
                    amount = self.amount,
                    transaction_inputs = self.transaction_inputs,
                    transaction_outputs = [tx.__dict__ for tx in self.transaction_outputs],
                    transaction_id = self.__hash__()
                )
            ).encode()
        ) 

        signer = PKCS1_v1_5.new(private_key)
        self.signature = signer.sign(h)

    def __str__(self):
        return f'sender_address: {self.sender_address} \nreceiver_address: {self.receiver_address} \namount: {self.amount} \ntransaction_inputs: {self.transaction_inputs} \ntransaction_outputs: {self.transaction_outputs} \ntransaction_id: {self.transaction_id} \nsignature: {self.signature}'


# random_gen = Crypto.Random.new().read
# priv = RSA.generate(1024, random_gen)

# t = Transaction(1, 1, 1, [])
# t.sign_transaction(priv)
 
# print(t.__hash__())
