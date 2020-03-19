#!/usr/bin/env python

"""
__version__ = '1.0.0'
__date__ = '2020-01-01'
__author__ = 'Ding Yi, <dingyi@dingyix.com>'
"""

import json
import requests
from pathlib import Path
from flask import Flask, jsonify, request, flash, render_template
from modules.main import Blockchain
from modules.main import ChainInfo
from modules.main import NodesInfo
from modules import config

host = config.get_value_str('blockchain', 'host')
port = config.get_value_int('blockchain', 'port')
data_file = Path(Path(__file__).parent.parent, config.get_value_str('blockchain', 'data_path'))
node_file = Path(Path(__file__).parent.parent, config.get_value_str('blockchain', 'node_path'))

app = Flask(__name__, template_folder='../templates', static_folder='../static')
app.config['SECRET_KEY'] = '1234567'
blockchain = Blockchain()

data_exist = Path(data_file).exists()
if not data_exist:
    blockchain.new_block(previous_hash=1, proof=100)
    with open(data_file, 'w') as f:
        json.dump(blockchain.chain, f, ensure_ascii=False)
else:
    with open(data_file, 'r') as f:
        blockchain.chain = json.load(f)

node_exist = Path(node_file).exists()
if not node_exist:
    Path(node_file).touch()
else:
    if Path(node_file).stat().st_size != 0:
        with open(node_file, 'r') as f:
            blockchain.nodes = json.load(f)


@app.route('/', methods=['GET', 'POST'])
def web_chain():
    if request.method == 'POST':
        table = ChainInfo(formdata=request.form)
        if table.validate():
            name = table.data['name']
            manner = table.data['manner']
            scope = table.data['scope']
            detail = table.data['detail']
            region = table.data['region']
            tag = table.data['tag']
            time = table.data['time']
            duration = table.data['duration']
            product = table.data['product']
            department = table.data['department']
            contact = table.data['contact']

            url = f"http://{host}:{port}/record/new"
            headers = {"Content-Type": "application/json"}
            data = json.dumps(
                {"name": name,
                 "manner": manner,
                 "scope": scope,
                 "detail": detail,
                 "region": region,
                 "tag": tag,
                 "time": time,
                 "duration": duration,
                 "product": product,
                 "department": department,
                 "contact": contact})
            response = requests.post(url, headers=headers, data=data)

            if response.status_code == 201:
                flash('记录成功', 'success')
                return render_template('index.html', form=ChainInfo())
            else:
                flash('记录失败', 'danger')
                return render_template('index.html', form=ChainInfo())
        else:
            print(table.errors)
        return render_template('index.html', form=table)
    else:
        table = ChainInfo()
        return render_template('index.html', form=table)


@app.route('/hosts', methods=['GET', 'POST'])
def web_hosts():
    if request.method == 'POST':
        table = NodesInfo(formdata=request.form)
        if table.validate():
            node_new = []
            host_new = table.data['host']
            port_new = table.data['port']
            node_new.append("http://"+host_new+":"+port_new)

            url = f"http://{host}:{port}/nodes/register"
            headers = {"Content-Type": "application/json"}
            data = json.dumps(
                {"nodes": node_new})
            response = requests.post(url, headers=headers, data=data)

            if response.status_code == 201:
                flash('添加成功', 'success')
                return render_template('hosts.html', form=NodesInfo())
            else:
                flash('添加失败', 'danger')
                return render_template('hosts.html', form=NodesInfo())
        else:
            print(table.errors)
        return render_template('hosts.html', form=table)
    else:
        table = NodesInfo()
        return render_template('hosts.html', form=table)


@app.route('/record/new', methods=['POST'])
def new_records():
    for node in blockchain.nodes:
        if Path(node_file).stat().st_size == 0:
            pass
        else:
            requests.get(f'http://{node}/chain')
    else:
        values = request.get_json()
        required = ['name', 'manner', 'scope', 'detail', 'region', 'tag', 'time',
                    'duration', 'product', 'department', 'contact']
        if not all(k in values for k in required):
            return 'Missing values', 400

        index = blockchain.new_record(
            name=values['name'], manner=values['manner'], scope=values['scope'],
            detail=values['detail'], region=values['region'], tag=values['tag'],
            time=values['time'], duration=values['duration'], product=values['product'],
            department=values['department'], contact=values['contact'])

        latest_block = blockchain.last_block
        latest_proof = latest_block['proof']
        proof = blockchain.proof_of_work(latest_proof)
        blockchain.new_block(proof)

        with open(data_file, 'w') as file:
            json.dump(blockchain.chain, file, ensure_ascii=False)

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
                         "manner": values['manner'],
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
def view_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain)
    }

    return jsonify(response), 200


@app.route('/nodes', methods=['GET'])
def view_nodes():
    response = {
        'total_nodes': blockchain.nodes
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

    with open(node_file, 'w') as file:
        json.dump(blockchain.nodes, file)

    update = blockchain.resolve_conflicts()

    if update:
        with open(data_file, 'w') as file:
            json.dump(blockchain.chain, file, ensure_ascii=False)
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
            'message': 'Our chain was replaced'
        }
    else:
        response = {
            'message': 'Our chain is authoritative'
        }

    return jsonify(response), 200
