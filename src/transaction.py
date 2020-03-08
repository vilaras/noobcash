from collections import OrderedDict

import binascii

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
        receiver_address: To public key του wallet στο οποίο θα καταλήξουν τα χρήματα
        amount: το ποσό που θα μεταφερθεί
        transaction_id: το hash του transaction
        transaction_inputs: λίστα από Transaction Input 
        transaction_outputs: λίστα από Transaction Output 
        Signature: Υπογραφή του transaction
    '''
    def __init__(self, sender_address, sender_private_key, receiver_address, amount, transaction_inputs, transaction_outputs):

        self.sender_address = sender_address
        self.receiver_address = receiver_address
        self.amount = amount
        self.transaction_id = self.__hash__()
        self.transaction_inputs = transaction_inputs
        self.transaction_outputs = []
    
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

    def sign_transaction(self):
        """
        Sign transaction with private key
        """
        private_key = RSA.importKey(binascii.unhexlify(sender_private_key))
        signer = PKCS1_v1_5.new(private_key)
        """
        mydict = OrderedDict({
            'sender_address': self.sender_address,
            'receiver_address': self.receiver_address,
            'value': self.value,
            'transaction_id': self.transaction_id,
            'transaction_inputs' : self.transaction_inputs,
            'transaction_outputs': self.transaction_outputs
        })
        """
        mydict = self.to_dict2()
        h = SHA.new(str(mydict).encode('utf8'))
        return binascii.hexlify(signer.sign(h)).decode('ascii')


t = Transaction(1, 2, 1, 1)
print(t.transaction_id)