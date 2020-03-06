import sys
import json
import requests
import signal

def signal_handler(sig, frame):
    print()
    print('Bye Bye !')
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

# user should provide rest api's ports
if(len(sys.argv)==1):
    print("Usage is 'python3 cli.py PORT'")
    sys.exit(0)
port = sys.argv[1]
base_url = "http://0.0.0.0:"+port+"/"
headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}

print("Hello, I am the blockchain cli.How can I help?")

while(1):
    print('Please select an action..press help for available actions!')
    action = input()
   
    if(action == 'help'):    
        print("There are six available actions listed below")
        print("1.'t <recipient_address> <amount>' in order to create a new transaction.")
        print("2.'view' in order to view all transactions contained in the last validated block.")
        print("3.'show balance' in order to view your account balance.")
        print("4.'Ctrl + C' in order to exit .")
    elif(action=='view' or action=='v'):
        url = base_url+"view_transactions"
        print("Printing the transactions from the last validated block in the blockchain")
        response = requests.get(url)
        for i in response.json():
            print(i)
    elif(action=='show balance' or action=='s' or action=='balance'):
        url = base_url+"show_balance"
        response = requests.get(url)
        print("Your current balance is "+str(response.json()['Balance'])+ " coins !")
    elif(action[0]=='t'):
        url = base_url+"create_transaction"
        inputs = action.split()
        payload = {'addr':inputs[1],'amount':inputs[2]}
        payload = json.dumps(payload)
        response = requests.post(url,data=payload,headers=headers)
        if((response.json()['message'])!='Not enough'):
            print(response.json()['message'])
        else:
            print("It seems like you are broke..You should consider clicking --> https://www.youtube.com/watch?v=TeT0vNbjs5w")