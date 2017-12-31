#! usr/bin/env python3

from flask import Flask, jsonify, request
from uuid import uuid4
from textwrap import dedent

from blockchain import Blockchain

# Intantiate Node
app = Flask(__name__)

# Generate unique id
node_identifier = str(uuid4()).replace('-', '')

# Instantiate the Blockchain
blockchain = Blockchain()

@app.route('/mine', methods = ['GET'])
def mine():
    # We run the PoW algo to get the next proof
    last_block = blockchain.last_block
    prev_proof = last_block['proofOfWork']
    proof = blockchain.proof_of_work(prev_proof)

    # Reward for finding proof
    # Sender is 0, idicating new coin mined by this node
    blockchain.new_transaction(
        sender = '0',
        recipient = node_identifier,
        amount = 1
    )

    # Adding block to the chain
    prev_hash = blockchain.hash(last_block)
    block = blockchain.new_block(proof, prev_hash)

    response = {
        'message': 'New Block Forged',
        'index': block['index'],
        'transactions': block['transactions'],
        'proof': block['proofOfWork'],
        'previous_hash': block['previous_hash']
    }
    return jsonify(response)

@app.route('/transactions/new', methods = ['POST'])
def new_transaction():
    values = request.get_json()

    if values:
        
        # Check integrity of incoming data
        required = ['sender', 'recipient', 'amount']
        if not all(keys in values for keys in required):
            return 'Values are missing', 400

        # Create new transcation
        index = blockchain.new_transaction(values['sender'], values['recipient'], values['amount'])

        response = {'message': f'Transaction will be added to the next mined block {index}'}
        return jsonify(response), 201
    else:
        return 'values is empty'

@app.route('/chain', methods = ['GET'])
def full_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain)
    }
    return jsonify(response), 200

@app.route('/nodes/register', methods = ['POST'])
def register_nodes():
    values = request.get_json()

    nodes = values.get('nodes')

    if nodes is None:
        return 'Supply a valid set of nodes', 400

    for node in nodes:
        blockchain.register_node(node)

    response = {
        'message' : 'New nodes have been added',
        'total_nodes': list(blockchain.nodes)
    }
    return jsonify(response), 201

@app.route('/nodes/consensus', methods = ['GET'])
def consensus():
    replaced = blockchain.resolve_conlicts()

    if replaced:
        response = {
            'message': 'Blockchain replaced',
            'new_chain': blockchain.chain
        }
    else:
        response = {
            'message': 'Blockchain is good, no replacements found',
            'new_chain': blockchain.chain
        }
    return jsonify(response), 200

if __name__ == '__main__':
    app.run()