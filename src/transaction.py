# Cryptographic imports
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5

# Util imports
import json
import jsonpickle
import binascii

'''
Attributes:
    sender_address: Sender's public key
        Type <str>. 
    receiver_address: Receiver's public key
        Type <str>. 
    amount: The amount of NBC coins to be transfered
        Type <int>. 
    transaction_id: A unique number identifying the transaction
        Type <int>
    transaction_inputs: List of input transaction IDs 
        Type <list int>
    transaction_outputs: list of Transaction Outputs
        Type <list Transaction_Output>
    signature: A Signature verifying the transactions authenticity
        Type <bytes>
'''
class Transaction:
    def __init__(self, sender_address, receiver_address, amount, transaction_inputs):
        self.sender_address = sender_address
        self.receiver_address = receiver_address
        self.amount = amount
        self.transaction_inputs = transaction_inputs
        self.transaction_outputs = []
        self.signature = 42
        self.transaction_id = self.__hash__().hexdigest()

    def __hash__(self):
        # In order to not include the signature in hash calculation
        # Please find a better way to do this
        temp = self.signature
        self.signature = 42
        h = SHA256.new(jsonpickle.encode(self).encode())
        self.signature = temp

        return h

    def __eq__(self, other):
        return self.transaction_id == other.transaction_id

    def __str__(self):
        return f'sender_address: {self.sender_address} \nreceiver_address: {self.receiver_address} \namount: {self.amount} \ntransaction_inputs: {self.transaction_inputs} \ntransaction_outputs: {self.transaction_outputs} \ntransaction_id: {self.transaction_id} \nsignature: {self.signature}'

    def set_transaction_outputs(self, transaction_outputs):
        self.transaction_outputs = transaction_outputs

    """
    Sign transaction with private key
    """
    def sign_transaction(self, private_key):
        h = self.__hash__()

        private_key = RSA.importKey(private_key)
        signer = PKCS1_v1_5.new(private_key)

        self.signature = signer.sign(h)
