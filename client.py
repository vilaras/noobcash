import sys
import json
import requests
import signal
import socket

#Graceful exit
def signal_handler(sig, frame):
    print('\n\nBye Bye !')
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

# user should provide rest api's ports
if len(sys.argv) != 2:
    print("Usage is 'python3 cli.py PORT'")
    sys.exit(0)

port = sys.argv[1]
base_url = f'http://127.0.0.1:{port}'
headers = {'Content-type': 'application/json', 'Accept': 'text/pl11ain'}

print("Hello, I am the blockchain cli.How can I help?")

while True:
    print('Please select an action..press help for available actions!')
    action = input()
   
    if action == 'help':    
        print("There are five available actions listed below")
        print("\t1.'connect' in order to initialize your wallet and conenct to the network\n")
        print("After you have connected you can:")
        print("\t2.'t <recipient_address> <amount>' in order to create a new transaction.")
        print("\t3.'view' in order to view all transactions contained in the last validated block.")
        print("\t4.'show balance' in order to view your account balance.")
        print("\t5.'Ctrl + C' in order to exit .")

    elif action == 'connect':
        try:
            url = f'{base_url}/register_client'
            response = requests.post(url)

            print("You have connected successfully!")

        except requests.exceptions.Timeout:
            print(f'something went wrong, please try again')


    elif action == 'view' or action == 'v':
        url = base_url + "view_transactions"
        print("Printing the transactions from the last validated block in the blockchain")
        response = requests.get(url)
        for i in response.json():
            print(i)

    elif action == 'show balance' or action == 's' or action == 'balance':
        url = base_url + "show_balance"
        response = requests.get(url)
        print("Your current balance is " + str(response.json()['Balance']) + " coins !")

    elif action[0] == 't':
        url = base_url + "create_transaction"
        inputs = action.split()
        payload = {'addr':inputs[1], 'amount':inputs[2]}
        payload = json.dumps(payload)
        response = requests.post(url, data=payload, headers=headers)

        if response.json()['message'] != 'Not enough':
            print(response.json()['message'])

        else:
            print("It seems like you are broke..You should consider clicking --> https://www.youtube.com/watch?v=TeT0vNbjs5w")