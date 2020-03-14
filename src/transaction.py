# Cryptographic imports
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5

# Util imports
import json
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
        self.hash = self.__hash__()
        self.transaction_id = self.hash.hexdigest()

    def __hash__(self):
        self.hash = SHA256.new(
            json.dumps(
                dict(
                    sender_address = self.sender_address,
                    receiver_address = self.receiver_address,
                    amount = self.amount,
                    transactions_in_count = len(self.transaction_inputs),
                    transaction_inputs = self.transaction_inputs,
                    transactions_out_count = len(self.transaction_outputs),
                    transaction_outputs = [tx.__dict__ for tx in self.transaction_outputs]
                )
            ).encode()
        )

        return self.hash
        
    def __str__(self):
        return f'sender_address: {self.sender_address} \nreceiver_address: {self.receiver_address} \namount: {self.amount} \ntransaction_inputs: {self.transaction_inputs} \ntransaction_outputs: {self.transaction_outputs} \ntransaction_id: {self.transaction_id} \nsignature: {self.signature}'
    
    def set_transaction_outputs(self, transaction_outputs):
        self.transaction_outputs = transaction_outputs

    """
    Sign transaction with private key
    """
    def sign_transaction(self, private_key):
        h = self.hash

        private_key = RSA.importKey(private_key)
        signer = PKCS1_v1_5.new(private_key)

        self.signature = signer.sign(h)


