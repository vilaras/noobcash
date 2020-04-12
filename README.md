# Noobcash
A simple blockchain system for validating transactions using Proof of work. Created as a project for NTUA ECE Distributed Systems 2019-2020 course.

## Installation

Install requires packages:

	$ sudo apt-get install python3 python3-pip python3-requests python3-virtualenv

## Setup

	$ tar xvfz noobcash.tar.gz
    $ cd noobcash
    $ virtualenv .venv
    $ source .venv/bin/activate
    $ pip3 install -r requirements.txt

## Parameters

You can configure the parameters in noobcash/src/config.py:

* NUMBER_OF_NODES
* BOOTSTRAP
* BLOCK_CAPACITY 
* MINING_DIFFICULTY
* STARTING NBC

## Usage

First of all start a server for each participant:

    $ cd noobcash
    $ source .venv/bin/activate
    $ cd src
    $ python3 rest.py -i [IP] -p [PORT]

Then in a separate terminal start a client for each participant:

    $ cd noobcash
    $ source .venv/bin/activate
    $ python3 client.py [IP] [PORT]

## Commands

From the client you can give the following commands:

* `t [recipient_id] [amount]` 
* `balance`                   
* `view`                      
* `view all`                  
* `exit`                      

## Testing

You can perform a stress test in the system using the test transactions in `noobcash/5nodes/` or `noobcash/10nodes/`:

    $ python3 stress_test.py -n [NUMBER_OF_NODES]

While the system is running, you can check the state of each node running:

    $ python3 check_state.py -n [NUMBER_OF_NODES]
    $ python3 check_blockchain.py -n [NUMBER_OF_NDOES] -v [VERBOSE]
