#! usr/bin/env python3

from time import time
import json
import hashlib
from urllib.parse import urlparse
import requests

""" 
Core Concepts:
    chain: each block contains the hash of the previous block
    block: each block has an index, timestamp(UNIX), transaction list, proofOfWork(PoW Algo), prev_hash
    genesis block: seed block, no preceding blocks, the start of the chain
    PoW Algo: How new blocks are created or mined
              Find a number such that it is easily verifiable but difficult to find
              Difficulty depends on what to find
    Consensus Algo: Replace chain with the longest chain in the network
"""

class Blockchain(object):
    def __init__(self):
        """ 
        Constructor: chain - holds the blockchain
                     current_transactions - holds transactions
        """
        self.chain = []
        self.current_transactions = []
        self.nodes = set()

        # Genesis block
        self.new_block(previous_hash = 1, proofOfWork = 100)

    def register_node(self, address):
        """
        Update node registry

        :param address: <str> Address of node, a url
        :return: None
        """

        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)
    
    def new_block(self, proofOfWork, previous_hash=None):
        # Note to self: default arguments should be last or 
        # an error is raised -> SyntaxError: non-default argument follows default argument
        """
        Creates a new block and adds (appends) to chain
        
        :param previous_hash: <str> (Optional) Hash of prev block
        :param proofOfWork: <int> result of PoW algo
        :return: <dict> New Block
        """
        
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.current_transactions,
            'proofOfWork': proofOfWork,
            'previous_hash': previous_hash or self.hash(self.chain[-1])
        }

        # Reset the current list of transactions
        self.current_transactions = []

        # Add new block to the chain
        self.chain.append(block)

        return block

    def new_transaction(self, sender, recipient, amount):
        """ 
        Creates a new transaction to add to the next mined block

        :param sender: <str> Sender Address
        :param recipient: <str> Recipient Address
        :param amount: <int> Amount
        :return: <int> index of the block that the transaction gets added to
        """

        self.current_transactions.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amount
        })
        
        return self.last_block['index'] + 1
    

    @property
    def last_block(self):
        # Returns the last block in the chain (@index -1)
        return self.chain[-1]
   
    @staticmethod
    def hash(block):
        """
        Hashing function SHA-256
        
        :param block: <dict> Block
        :return proof: <str>
        """
        
        # since Python dicts have arbitrary ordering ans need to be ordered else incorrect hashing
        block_string = json.dumps(block, sort_keys = True).encode()

        return hashlib.sha256(block_string).hexdigest()

    def proof_of_work(self, previous_proof):
        """ 
        Simple PoW Algo
            Find a number n such that the hash of n & n_prev has 4 leading 0's

            :param previous_proof: <int>
            :return: <int>
        """

        proof = 0
        while self.valid_proof(previous_proof, proof) is False:
            proof = proof + 1

        return proof

    @staticmethod
    def valid_proof(prev_proof, proof):
        """ 
        Validates proof

        :param prev_proof: <int> Previous Proof
        :param proof: <int> Current Proof
        :return: <bool> True or False
        """


        guess = f'{prev_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()

        return guess_hash[:4] == '0000'

    def valid_chain(self, chain):
        """
        
        Validate blockchain

        :param chain: <list> A blockchain
        :return: <bool> True or False
        """

        last_block = chain[0]
        current_index = 1

        while current_index < len(chain):
            block = chain[current_index]
            print(f'{last_block}')
            print(f'{block}')
            print('\n--------\n')

            # Check PoW is correct
            if not self.valid_proof(last_block['proofOfWork'], block['proofOfWork']):
                return False
            
            last_block = block
            current_index = current_index + 1
        return True

    def resolve_conlicts(self):
        """ 
        Consensus Algo

        :return: <bool> True of False
        """

        neighbors = self.nodes
        new_chain = None

        # We only want chains that are longer than ours
        max_length = len(self.chain)

        # Verify all chains from all nodes
        for node in neighbors:
            response = requests.get(f'http://{node}/chain')

            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']

                # length and chain validity
                if length > max_length and self.valid_proof(chain):
                    max_length = length
                    new_chain = chain
        
        # Replace our chain with the better one found if any
        if new_chain:
            self.chain = new_chain
            return True
        return False