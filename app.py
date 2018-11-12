#!/usr/bin/python3
import json
from flask import Flask, jsonify, request, abort, send_from_directory
from flask_cors import CORS
from cert_core import Chain
from subprocess import call
import os
import logging 

import subprocess
import shlex

import cert_issuer
from cert_issuer.blockchain_handlers import ethereum
from cert_issuer.issuer import Issuer

here = os.path.abspath(os.path.dirname(__file__))

BLOCKCERTS_FOLDER = os.path.join(here, 'data/blockchain_certificates')
UNSIGNED_CERTS_FOLDER = os.path.join(here, 'data/unsigned_certificates')

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
CORS(app)
app.config['BLOCKCERTS_FOLDER'] = BLOCKCERTS_FOLDER

# @app.route('/cert_issuer/api/v1.0/issue', methods=['POST'])
# def issue():
#     config = get_config()
#     certificate_batch_handler, transaction_handler, connector = \
#             bitcoin.instantiate_blockchain_handlers(config, False)
#     certificate_batch_handler.set_certificates_in_batch(request.json)
#     cert_issuer.issue_certificates.issue(config, certificate_batch_handler, transaction_handler)
#     return json.dumps(certificate_batch_handler.proof)
# def main(app_config):
#     chain = app_config.chain
#     if chain == Chain.ethereum_mainnet or chain == Chain.ethereum_ropsten:
#         from cert_issuer.blockchain_handlers import ethereum
#         certificate_batch_handler, transaction_handler, connector = ethereum.instantiate_blockchain_handlers(app_config)
#     else:
#         from cert_issuer.blockchain_handlers import bitcoin
#         certificate_batch_handler, transaction_handler, connector = bitcoin.instantiate_blockchain_handlers(app_config)
#     return issue(app_config, certificate_batch_handler, transaction_handler)

# def issue(app_config, certificate_batch_handler, transaction_handler):
#     certificate_batch_handler.pre_batch_actions(app_config)

#     transaction_handler.ensure_balance()

#     issuer = Issuer(
#         certificate_batch_handler=certificate_batch_handler,
#         transaction_handler=transaction_handler,
#         max_retry=app_config.max_retry)
#     tx_id = issuer.issue(app_config.chain)

#     certificate_batch_handler.post_batch_actions(app_config)
#     return tx_id

def run_command(command):
    process = subprocess.Popen(shlex.split(command), stdout=subprocess.PIPE)
    while process.poll() is None:
        output = process.stdout.readline()
        if output:
            print(output.strip())                       
    rc = process.returncode
    return rc

# def run_command(command):
#     process = subprocess.Popen(shlex.split(command), stdout=subprocess.PIPE)
#     while True:
#         line = process.stdout.readline().rstrip()
#         if not line:
#             break
#         yield line

@app.route('/issue-blockcerts', methods=['POST'])
def panacert_issue():
    unsignedCertificates = request.json['unsignedCertificates']

    # delete files in UNSIGNED_CERTS_FOLDER
    file_list = os.listdir(UNSIGNED_CERTS_FOLDER)
    for file_name in file_list:
        os.remove(os.path.join(UNSIGNED_CERTS_FOLDER, file_name))
    # add new files to UNSIGNED_CERTS_FOLDER
    for cert in unsignedCertificates:
        wf = open(os.path.join(UNSIGNED_CERTS_FOLDER, cert['id'].split('urn:uuid:', 1)[1] + '.json'), 'w')
        json.dump(cert, wf)
        wf.close()
        
    rc = run_command('cert-issuer')
    if rc == 0:
        return jsonify({'success': True})
    else:
        return jsonify({'success': False})

@app.route('/blockcerts/<filename>')
def blockcert(filename):
    return send_from_directory(app.config['BLOCKCERTS_FOLDER'], filename)

@app.route('/')
def hello():
    return 'Hello World!'

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=5000)
