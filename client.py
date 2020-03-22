# Util imports
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
if len(sys.argv) != 3:
    print("Usage is 'python3 cli.py IP PORT'")
    sys.exit(0)


ip = sys.argv[1]
port = sys.argv[2]
base_url = f'http://{ip}:{port}'
headers = {'Content-type': 'application/json', 'Accept': 'text/pl11ain'}

help_message = '''
Usage: 

$ python3 rest.py -i IP -p PORT         Start your server
$ python3 client.py IP PORT             Start your client 

Available commands:
    * 'connect'                         Initialize your wallet and conenct to the network

After you have connected you can:
    * `t <recipient_id> <amount>`       Send `amount` NBC to `recepient_id`
    * `balance`                         Show the IDs of every user along with their balance
    * `view`                            View all transactions contained in the last validated block 
    * `exit`                            Exit the client
'''

print("Hello, I am the blockchain cli. How can I help?")

while True:
    action = input("> ").strip()
   
    if action == 'help':    
        print(help_message)

    elif action == 'exit':
        print('\nBye Bye !')
        sys.exit(0)

    elif action == 'connect':
        try:
            url = f'{base_url}/register_client'
            response = requests.post(url)

            print(response.json())

        except:
            print(f'Something went wrong in "{url}" request')

    elif action == "balance":
        try:
            url = f'{base_url}/balance'
            response = requests.get(url)

            if response.status_code != 200:
                print(f'Something went wrong with {url} request')

            else:
                print(response.json())

        except:
            print(f'Something went wrong in "{url}" request')

    elif action == 'view':
        try:
            url = f'{base_url}/view_transactions'
            response = requests.get(url)

            if response.status_code != 200:
                print(f'Something went wrong with {url} request')

            else:
                print(response.json())

        except:
            print(f'Something went wrong in "{url}" request')

    elif action.startswith('t'):
        try:
            url = f'{base_url}/create_transaction'
            inputs = action.split()
            payload = json.dumps({'id':inputs[1][-1], 'amount':inputs[2]})
            response = requests.post(url, data=payload, headers=headers)

            if response.status_code != 200:
                print(f'Something went wrong with {url} request')

            else:
                print(response.json())

        except:
            print(f'Something went wrong in "{url}" request')

    else:
        print(f'{action}: Unknown command. See `help`')
