import hashlib
import json
import random
import socket
import string
import subprocess
from base64 import urlsafe_b64encode
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

import click
import requests
from clinlog import get_logger

from .Config import Config

AUTH_REDIRECT_URL = '{uri}?response_type={response_type}&client_id={client_id}&state={state}&redirect_uri={redirect_uri}&scope={scope}&code_challenge={code_challenge}&code_challenge_method=S256&nonce={nonce}'
LOG = get_logger()

def get_rand_string() -> str:
    return ''.join(random.choice(string.ascii_lowercase + '1234567890') for i in range(48))


def get_code_challenge(code_verify:str) -> str:
    return urlsafe_b64encode(hashlib.sha256(code_verify.encode('ascii'))
                             .digest()).decode('utf-8').rstrip('=')


def get_tokens_request(url, grant_type:str, client_id:str, redirect_uri:str,
                       code:str, code_verifier:str) -> dict:
    data = {
        'client_id': client_id,
        'grant_type': grant_type,
        'code': code,
        'redirect_uri': redirect_uri,
        'code_verifier': code_verifier
    }

    res = requests.post(url, data)

    return res.json()


def listen_and_wait() -> str:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(('', 55145))
        sock.listen()
        conn, addr = sock.accept()
        conn_data = b''
        with conn:
            LOG.debug('Connection from {}', addr)
            while True:
                conn_data += conn.recv(1024)
                if conn_data.endswith(b'\r\n\r\n'): break # Http message end
            conn.sendall(b'HTTP/1.1 200 OK\r\n\r\n')

            LOG.debug('Connection closed')

        LOG.debug('Received data: \n{}', conn_data)

    return parse_http_and_get_code(conn_data)


def parse_http_and_get_code(http_req:bytes) -> str:
    req_sections = http_req.decode('utf-8').split('\r\n')
    req_line = req_sections[0].split(' ')
    url = req_line[1]

    params = parse_qs(urlsplit(url).query)

    return params['code'][0]

def browser_additional_params(browser_name):
    browser_param_map = {
        'firefox': '--new-window',
        'chrome': '--new-window',
        'chromium': '--new-window'
    }

    return browser_param_map.get(browser_name, '')

def get_redirect_uri(port, protocol='http'):
    return '{}://localhost:{}'.format(protocol, port)

def create_logger():
    logger = get_logger()
    logger.info_tag = ''
    logger.confirm_tag = ''

    global LOG
    LOG = logger


@click.command()
@click.option('--config', '-c', 'config_path', default='', help='Config file. Defaults to ~/.openid-cmd/config.yml')
def login(config_path):
    create_logger()

    # Load config
    if config_path:
        config_path = Path(config_path)

    config = Config(config_path)
    if not config.config_file_exists():
        LOG.warning('Config file does not exists. Creating default...')
        config.create_default_config()

    config.load_config()

    # Generate and open auth url
    state = get_rand_string()
    code_verify = get_rand_string()
    code_challenge = get_code_challenge(code_verify)
    AUTH_REDIRECT_URL = '{uri}?response_type={response_type}&client_id={client_id}&state={state}&redirect_uri={redirect_uri}&scope={scope}&code_challenge={code_challenge}&code_challenge_method=S256&nonce={nonce}'
    auth_url = AUTH_REDIRECT_URL.format(uri=config.openid_client['auth_redirect_url'],
                                        response_type=config.openid_client['response_type'],
                                        client_id=config.openid_client['client_id'],
                                        redirect_uri=get_redirect_uri(config.openid_client['redirect_port']),
                                        scope=config.openid_client['scope'],
                                        state=state,
                                        code_challenge=code_challenge,
                                        nonce=state)

    LOG.info('Opening auth url on browser...')
    LOG.info(auth_url, highlight=True)

    browser = config.browser['cmd']
    browser_proc = subprocess.Popen([browser, browser_additional_params(browser), auth_url],
                                    stderr=subprocess.DEVNULL)
    code = listen_and_wait()
    browser_proc.kill()
    LOG.print('\nCode extracted from auth server request: {}', code)

    # Get token request
    LOG.print('Request to token url ({})', config.openid_client['token_url'])
    token_res = get_tokens_request(config.openid_client['token_url'],
                                   config.openid_client['grant_type'],
                                   config.openid_client['client_id'],
                                   get_redirect_uri(config.openid_client['redirect_port']),
                                   code, 
                                   code_verify)

    LOG.debug('Tokens: \n{}', json.dumps(token_res, indent=4))

    # Print response outputs
    LOG.confirm('Tokens accquired. Output:')
    missing_outs = []
    for out_field in config.output:
        if out_field in token_res:
            LOG.confirm('{}: {}', out_field, token_res[out_field], highlight=True)
        else:
            missing_outs.append(out_field)
            
    for miss_out in missing_outs:
        LOG.warning("Output '{}' not found in token response", miss_out)

def main():
    login()

if __name__ == '__main__':
    main()
