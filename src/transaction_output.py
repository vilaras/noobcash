# Cryptographic imports
from Crypto.Hash import SHA256

# Util imports
import json

'''
Attributes:
    transaction_input_id: A unique number identifying the transaction output
        Type <int>
    receiver_address: Receiver's public key
        Type <str>. 
    amount: The amount of NBC coins to be transfered
        Type <int>.
'''
class Transaction_Output:
    def __init__(self, receiver_address, amount, previous_transaction_id):
        self.receiver_address = receiver_address
        self.amount = amount
        self.previous_transaction_id = previous_transaction_id
        self.transaction_id = self.__hash__()
    
    def __hash__(self):
        return SHA256.new(
            json.dumps(
                dict(
                    receiver_address = self.receiver_address,
                    amount = self.amount,
                    previous_transaction_id = self.previous_transaction_id
                )
            ).encode()
        ).hexdigest()

    def __str__(self):
        return f'receiver_address: {self.receiver_address}\namount: {self.amount}\nprevious_transaction_id: {self.previous_transaction_id}\ntransaction_id: {self.transaction_id}'
