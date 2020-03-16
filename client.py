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
        print("There are six available actions listed below")
        print("\t1.'connect' in order to initialize your wallet and conenct to the network\n")
        print("After you have connected you can:")
        print("\t2.'show participants' in order to see the other users in the network along with their public keys")
        print("\t3.'t <recipient_id> <amount>' in order to create a new transaction.")
        print("\t4.'view' in order to view all transactions contained in the last validated block.")
        print("\t5.'show balance' in order to view your account balance.")
        print("\t6.'Ctrl + C' in order to exit .")

    elif action == 'connect':
        try:
            url = f'{base_url}/register_client'
            response = requests.post(url)

            print("You have connected successfully!")

        except requests.exceptions.Timeout:
            print(f'something went wrong, please try again')


    elif action == "show participants":
        try:
            url = base_url + '/show_participants'
            response = requests.get(url)

            if response.status_code != 200:
                print(f'Something went wrong with {url} request')

            else:
                print()
                print(response.json())

        except requests.exceptions.Timeout:
            print(f'Request "{url}" timed out'), 408

    elif action == 'view' or action == 'v':
        try:
            url = base_url + "/view_transactions"
            print("Printing the transactions from the last validated block in the blockchain")
            response = requests.get(url)

            if response.status_code != 200:
                print(f'Something went wrong with {url} request')

            else:
                for i in response.json():
                    print(i)

        except requests.exceptions.Timeout:
            print(f'Request "{url}" timed out'), 408


    elif action == 'show balance' or action == 's' or action == 'balance':
        try:
            url = base_url + "/show_balance"
            response = requests.get(url)
            print("Your current balance is " + str(response.json()['Balance']) + " coins !")

            if response.status_code != 200:
                print(f'Something went wrong with {url} request')

            else:
                for i in response.json():
                    print(i)

        except requests.exceptions.Timeout:
            print(f'Request "{url}" timed out'), 408

    elif action[0] == 't':
        try:
            url = base_url + "/create_transaction"
            inputs = action.split()
            payload = {'id':inputs[1][-1], 'amount':inputs[2]}
            payload = json.dumps(payload)
            response = requests.post(url, data=payload, headers=headers)

            if response.status_code != 200:
                print(f'Something went wrong with {url} request')

            else:
                print(response.json())

        except requests.exceptions.Timeout:
            print(f'Request "{url}" timed out'), 408

            # if response.json()['message'] != 'Not enough':
            #     print(response.json()['message'])

            # else:
            #     print("It seems like you are broke..You should consider clicking --> https://www.youtube.com/watch?v=TeT0vNbjs5w")
    