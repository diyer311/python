#!/usr/bin/env python

"""
__version__ = '1.0.0'
__date__ = '2019-12-25'
__author__ = 'Ding Yi, <dingyi@dingyix.com>'
"""

import json
import hashlib
import requests
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse
from flask import Flask, jsonify, request

data_file = Path(__file__).parent.joinpath('data.json')
node_file = Path(__file__).parent.joinpath('node.json')


class Blockchain(object):
    """docstring for Blockchain"""
    def __init__(self):
        self.chain = []
        self.current_record = []
        self.nodes = []

    def new_block(self, proof, previous_hash=None):
        """
        :param proof: <int> The proof given by the Proof of Work algorithm
        :param previous_hash: (Optional) <str> Hash of previous Block
        :return: <dict> New Block
        """

        block = {
            'index': len(self.chain) + 1,
            'datetime': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'record': self.current_record,
            'proof': proof,
            'previous_hash': previous_hash or self.compute_hash(self.chain[-1])
        }

        self.current_record = []

        self.chain.append(block)
        return block

    def new_record(self, **kwargs):
        """
        :param kwargs: <dict> Info of the record
        :return: <int> The index of the Block that will hold this transaction
        """

        self.current_record.append({
            'name': kwargs['name'],
            'type': kwargs['type'],
            'scope': kwargs['scope'],
            'detail': kwargs['detail'],
            'region': kwargs['region'],
            'tag': kwargs['tag'],
            'time': kwargs['time'],
            'duration': kwargs['duration'],
            'product': kwargs['product'],
            'department': kwargs['department'],
            'contact': kwargs['contact']
            })

        return self.last_block['index'] + 1

    def proof_of_work(self, last_proof):
        """
        :param last_proof: <int>
        :return: <int>
        """

        proof = 0
        while self.valid_proof(last_proof, proof) is False:
            proof += 1

        return proof

    @staticmethod
    def valid_proof(last_proof, proof):
        """
        :param last_proof: <int> Previous Proof
        :param proof: <int> Current Proof
        :return: <bool> True if correct, False if not.
        """

        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()

        return guess_hash[:4] == '0000'

    @staticmethod
    def compute_hash(block):
        """
        :param block: <dict> Block
        :return: <str>
        """

        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    @property
    def last_block(self):
        """
        :return: <dict> The last block of current chain
        """
        return self.chain[-1]

    def register_node(self, address):
        """
        :param address: <str> Address of node. Eg. 'http://192.168.0.5:5000'
        :return: None
        """

        parsed_url = urlparse(address)
        host = parsed_url.netloc
        self.nodes.append(host)
        self.nodes = list(set(self.nodes))

    def valid_chain(self, chain):
        """
        :param chain: <list> A blockchain
        :return: <bool> True if valid, False if not
        """

        previous_block = chain[0]
        current_index = 1

        while current_index < len(chain):
            block = chain[current_index]
            print(f'{previous_block}')
            print(f'{block}')
            print('\n-------------\n')

            if block['previous_hash'] != self.compute_hash(previous_block):
                return False

            if not self.valid_proof(previous_block['proof'], block['proof']):
                return False

            previous_block = block
            current_index += 1

        return True

    def resolve_conflicts(self):
        """
        :return: <bool> True if block has been replaced, then False
        """

        neighbours = self.nodes
        new_chain = None

        max_length = len(self.chain)

        for node in neighbours:
            response = requests.get(f'http://{node}/chain')

            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']

                if length > max_length and self.valid_chain(chain):
                    max_length = length
                    new_chain = chain

        if new_chain:
            self.chain = new_chain
            return True

        return False


app = Flask(__name__)

blockchain = Blockchain()


@app.route('/record/new', methods=['POST'])
def new_transact():
    for node in blockchain.nodes:
        if Path(node_file).stat().st_size == 0:
            pass
        else:
            requests.get(f'http://{node}/chain')
    else:
        values = request.get_json()
        required = ['name', 'type', 'scope', 'detail', 'region', 'tag', 'time', 
                    'duration', 'product', 'department', 'contact']
        if not all(k in values for k in required):
            return 'Missing values', 400

        index = blockchain.new_record(
            name=values['name'], type=values['type'], scope=values['scope'], 
            detail=values['detail'], region=values['region'], tag=values['tag'], 
            time=values['time'], duration=values['duration'], product=values['product'], 
            department=values['department'], contact=values['contact'])

        latest_block = blockchain.last_block
        latest_proof = latest_block['proof']
        proof = blockchain.proof_of_work(latest_proof)
        block = blockchain.new_block(proof)

        with open(data_file, 'w') as f:
            json.dump(blockchain.chain, f, ensure_ascii=False)

        local_length = len(blockchain.chain)
        if Path(node_file).stat().st_size != 0:
            for node in blockchain.nodes:
                response = requests.get(f'http://{node}/chain')
                node_length = response.json()['length']
                if node_length != local_length:
                    url = f"http://{node}/record/new"
                    headers = {"Content-Type": "application/json"}
                    data = json.dumps(
                        {"name": values['name'],
                         "type": values['type'],
                         "scope": values['scope'],
                         "detail": values['detail'],
                         "region": values['region'],
                         "tag": values['tag'],
                         "time": values['time'],
                         "duration": values['duration'],
                         "product": values['product'],
                         "department": values['department'],
                         "contact": values['contact']})
                    requests.post(url, headers=headers, data=data)

        response = {'message': f'Transaction was added to block {index}'}

        return jsonify(response), 201

@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain)
    }

    return jsonify(response), 200

@app.route('/nodes/register', methods=['POST'])
def register_nodes():
    values = request.get_json()
    nodes = values.get('nodes')

    if nodes is None:
        return 'Error: Please supply a valid list of nodes', 400

    for node in nodes:
        check = requests.get(f'{node}/chain')
        if check.status_code == 200:
            blockchain.register_node(node)

    with open(node_file, 'w') as f:
        json.dump(blockchain.nodes, f)

    update = blockchain.resolve_conflicts()

    if update:
        with open(data_file, 'w') as f:
            json.dump(blockchain.chain, f, ensure_ascii=False)
        response = {
            'message': 'New nodes have been added and our chain was replaced',
            'total_nodes': blockchain.nodes
        }
    else:
        response = {
            'message': 'New nodes have been added and our chain is authoritative',
            'total_nodes': blockchain.nodes
        }

    return jsonify(response), 201

@app.route('/nodes/resolve', methods=['GET'])
def consensus_check():
    replaced = blockchain.resolve_conflicts()

    if replaced:
        response = {
            'message': 'Our chain was replaced',
            'new_chain': blockchain.chain
        }
    else:
        response = {
            'message': 'Our chain is authoritative',
            'chain': blockchain.chain
        }

    return jsonify(response), 200


if __name__ == '__main__':
    data_exist = data_file.exists()
    if not data_exist:
        blockchain.new_block(previous_hash=1, proof=100)
        with open(data_file, 'w') as f:
            json.dump(blockchain.chain, f, ensure_ascii=False)
    else:
        with open(data_file, 'r') as f:
            blockchain.chain = json.load(f)

    node_exist = node_file.exists()
    if not node_exist:
        Path(node_file).touch()
    else:
        if Path(node_file).stat().st_size != 0:
            with open(node_file, 'r') as f:
                blockchain.nodes = json.load(f)

    app.run(host='0.0.0.0', port=5000)
