from collections import OrderedDict

import binascii
import base64

import Crypto
import Crypto.Random
from Crypto.Hash import SHA
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5

import requests
from flask import Flask, jsonify, request, render_template


class Transaction:

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
        transaction_inputs: λίστα από Transaction Input 
            Type <list(Transaction)>
        transaction_outputs: λίστα από Transaction Output 
            Type <list(Transaction)>
        signature: Υπογραφή του transaction
            Type <???>
    '''
    def __init__(self, sender_address, receiver_address, amount, transaction_inputs):

        self.sender_address = sender_address
        self.receiver_address = receiver_address
        self.amount = amount
        self.transaction_id = self.__hash__()
        self.transaction_inputs = transaction_inputs
    

    def __str__(self):
        return str(self.__dict__)

    # def hash(self):
    #     transaction = { 
    #         'sender' : self.sender_address,
    #         'receiver': self.receiver_address,
    #         'value': self.amount, 
    #         'inputs': self.transaction_inputs
    #     }
    #     string = json.dumps(transaction, sort_keys=True).encode()
    #     return hashlib.sha224(string).hexdigest()

    def set_transaction_outputs(self, transaction_outputs):
        self.transaction_outputs = transaction_outputs


    # def sign(privatekey,data):
    #     return base64.b64encode(str((privatekey.sign(data,''))[0]).encode())

    # def verify(publickey,data,sign):
    #     return publickey.verify(data,(int(base64.b64decode(sign)),))    

    """
    Sign transaction with private key
    """
    def sign_transaction(self, private_key):
        self.signature = base64.b64encode(str((private_key.sign(self,''))[0]).encode())
        print(self.signature)
