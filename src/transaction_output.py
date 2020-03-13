import json
from Crypto.Hash import SHA256

'''
    Params:
        transaction_input_id: το id του transaction από το οποίο προέρχεται
        receiver_address: τον recipient του transaction
        amount: το ποσό που μεταφέρθηκε
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
                self.__dict__
            ).encode()
        ).hexdigest()

    def __str__(self):
        return f'receiver_address: {self.receiver_address}\namount: {self.amount}\nprevious_transaction_id: {self.previous_transaction_id}\ntransaction_id: {self.transaction_id}'
