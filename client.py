# Util imports
import sys
import json
import requests
import signal

#Graceful exit
def signal_handler(sig, frame):
    print('\nBye Bye!')
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

help_message = '''Usage: 

$ python3 client.py IP PORT             Start your client  

Available commands:
    * `t <recipient_id> <amount>`       Send `amount` NBC to `recepient_id`
    * `balance`                         View the IDs of every user along with their balance
    * `view`                            View all transactions contained in the last validated block 
    * `view all`                        View all the validated transactions in the network
    * `exit`                            Exit the client
'''

# Initialize the node and connect to the network
try:
    url = f'{base_url}/register_client'
    response = requests.post(url)

    print(response.json())

except Exception as e:
    print(f'Exception in "{url}" request \n{e.__class__.__name__}: {e}\n')
    sys.exit(0)


print("Hello, I am the blockchain cli. How can I help?")

while True:
    action = input("> ").strip()
   
    if action == "balance":
        try:
            url = f'{base_url}/balance'
            response = requests.get(url)

            print(response.json())

        except Exception as e:
            print(f'Exception in "{url}" request \n{e.__class__.__name__}: {e}\n')

    elif action == 'view':
        try:
            url = f'{base_url}/view_transactions'
            response = requests.get(url)

            print(response.json())

        except Exception as e:
            print(f'Exception in "{url}" request \n{e.__class__.__name__}: {e}\n')

    elif action == 'view all':
        try:
            url = f'{base_url}/view_all_transactions'
            response = requests.get(url)

            print(response.json())

        except Exception as e:
            print(f'Exception in "{url}" request \n{e.__class__.__name__}: {e}\n')

    elif action.startswith('t'):
        try:
            url = f'{base_url}/create_transaction'
            inputs = action.split()
            id_num = inputs[1].split('id')[-1]
            payload = json.dumps({'id':id_num, 'amount':inputs[2]})
            response = requests.post(url, data=payload, headers=headers)

            print(response.json())

        except Exception as e:
            print(f'Exception in "{url}" request \n{e.__class__.__name__}: {e}\n')

    elif action == 'help':    
        print(help_message)

    elif action == 'exit':
        print('\nBye Bye!')
        sys.exit(0)

    else:
        print(f'{action}: Unknown command. See `help`\n')
