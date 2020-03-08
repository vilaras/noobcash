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
        Signature
    '''
    def __init__(self, sender_address, sender_private_key, receiver_address, amount):

        self.sender_address = sender_address
        self.receiver_address = receiver_address
        self.amount = amount
        # self.transaction_id = transaction_id
        # self.transaction_inputs = transaction_inputs
        # self.transaction_outputs = transaction_outputs
    

    # def sign_transaction(self):
    #     """
    #     Sign transaction with private key
    #     """
