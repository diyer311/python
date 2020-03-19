#!/usr/bin/env python

"""
__version__ = '3.0.0'
__date__ = '2020-03-07'
__author__ = 'Ding Yi, <dingyi@dingyix.com>'
"""

import json
import hashlib
import requests
from datetime import datetime
from urllib.parse import urlparse
from wtforms import Form
from wtforms import validators
from wtforms import widgets
from wtforms.fields import simple


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
            'manner': kwargs['manner'],
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
        host_port = parsed_url.netloc
        self.nodes.append(host_port)
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


class ChainInfo(Form):
    name = simple.StringField(
        label='人员',
        validators=[
            validators.DataRequired()
        ],
        widget=widgets.TextInput(),
        render_kw={'class': 'form-control', 'placeholder': '例如：张三', 'style': 'width: 250px'}
        )

    manner = simple.StringField(
        label='支持类型',
        validators=[
            validators.DataRequired()
        ],
        widget=widgets.TextInput(),
        render_kw={'class': 'form-control', 'placeholder': '例如：远程支持', 'style': 'width: 250px'}
        )

    scope = simple.StringField(
        label='技术范畴',
        validators=[
            validators.DataRequired()
        ],
        widget=widgets.TextInput(),
        render_kw={'class': 'form-control', 'placeholder': '例如：数据库', 'style': 'width: 250px'}
        )

    detail = simple.StringField(
        label='支持详情',
        validators=[
            validators.DataRequired()
        ],
        widget=widgets.TextInput(),
        render_kw={'class': 'form-control', 'placeholder': '例如：解决数据库启动异常问题', 'style': 'width: 250px'}
        )

    region = simple.StringField(
        label='地区',
        validators=[
            validators.DataRequired()
        ],
        widget=widgets.TextInput(),
        render_kw={'class': 'form-control', 'placeholder': '例如：北京', 'style': 'width: 250px'}
        )

    tag = simple.StringField(
        label='标签',
        validators=[
            validators.DataRequired()
        ],
        widget=widgets.TextInput(),
        render_kw={'class': 'form-control', 'placeholder': '例如：MySQL', 'style': 'width: 250px'}
        )

    time = simple.StringField(
        label='开始时间',
        validators=[
            validators.DataRequired()
        ],
        widget=widgets.TextInput(),
        render_kw={'class': 'form-control', 'placeholder': '例如：2020-01-01', 'style': 'width: 250px'}
        )

    duration = simple.StringField(
        label='时长',
        validators=[
            validators.DataRequired()
        ],
        widget=widgets.TextInput(),
        render_kw={'class': 'form-control', 'placeholder': '例如：1H', 'style': 'width: 250px'}
        )

    product = simple.StringField(
        label='产品',
        validators=[
            validators.DataRequired()
        ],
        widget=widgets.TextInput(),
        render_kw={'class': 'form-control', 'placeholder': '例如：不动产一窗', 'style': 'width: 250px'}
        )

    department = simple.StringField(
        label='部门',
        validators=[
            validators.DataRequired()
        ],
        widget=widgets.TextInput(),
        render_kw={'class': 'form-control', 'placeholder': '例如：不动产研发中心-研发二部', 'style': 'width: 250px'}
        )

    contact = simple.StringField(
        label='联系人',
        validators=[
            validators.DataRequired()
        ],
        widget=widgets.TextInput(),
        render_kw={'class': 'form-control', 'placeholder': '例如：李四', 'style': 'width: 250px'}
        )


class NodesInfo(Form):
    host = simple.StringField(
        label='地址',
        validators=[
            validators.DataRequired()
        ],
        widget=widgets.TextInput(),
        render_kw={'class': 'form-control', 'placeholder': '例如：192.168.0.1', 'style': 'width: 250px'}
        )

    port = simple.StringField(
        label='端口',
        validators=[
            validators.DataRequired()
        ],
        widget=widgets.TextInput(),
        render_kw={'class': 'form-control', 'placeholder': '例如：5000', 'style': 'width: 250px'}
        )
