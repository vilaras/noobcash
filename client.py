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

help_message = '''
Usage: 

$ python3 client.py IP PORT             Start your client 
$ python3 rest.py IP PORT               Start your server

Available commands:
    * 'connect'                         Initialize your wallet and conenct to the network

After you have connected you can:
    * `balance`                         Show the IDs of every user along with their balance
    * `t <recipient_id> <amount>`       Send `amount` NBC to `recepient_id`
    * `view`                            in order to view all transactions contained in the last validated block 
    * `Ctrl + C`                        in order to exit
'''

print("Hello, I am the blockchain cli. How can I help?")

while True:
    # print('Please select an action. Press help for available actions!')
    action = input("> ")
   
    if action == 'help':    
        print(help_message)

    elif action == 'connect':
        try:
            url = f'{base_url}/register_client'
            response = requests.post(url)

            print(response.json())


        except requests.exceptions.Timeout:
            print(f'something went wrong, please try again')


    elif action == "balance":
        try:
            url = base_url + '/balance'
            response = requests.get(url)

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
    
    else:
        print(f'{action}: Unknown command. See `help`')
