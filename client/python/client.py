import os
import json
import threading
import requests
import queue
import logging
logging.basicConfig(level=logging.DEBUG)

from flask_openapi3 import OpenAPI, Info
from argparse import ArgumentParser
from kazoo.client import KazooClient
from pydantic import BaseModel

from pydantic_classes import DeleteQuery, PutQuery, GetQuery, CodeResponse, GetResponse

DEFAULT_PORT = 5000
LOAD_FROM = 'env'
MODE = 'args'

ZK_ROOT_NAME = 'root'
ZK_CHILD_NAME = 'child'

ZK_IP = 'zk_ip'
PORT = 'port'
NODE_IP = 'node_ip'
ROOT = 'root'

INFO = Info(title='KIV/DS', version='1.0.0')

key_value_storage = {}
app = OpenAPI(__name__, info=INFO)

zk_info_dict = {}

log_file = open('log.txt', 'w+', encoding='utf-8').close()


def log_message(message: str):
    f = open('log.txt', 'a', encoding='utf-8')
    print(f'[{config[NODE_IP]}:{config[PORT]}] {message}', file=f, flush=True)


# ---------------------------------------------------------------------------------------------------- ZOOKEEPER


def boolean_string(string: str):
    if isinstance(string, bool):
        return string
    elif string.lower() in ('True', 'true'):
        return True
    elif string.lower() in ('False', 'false'):
        return False


def load_config(where_from: str):
    d = {}
    if where_from == 'env':
        d[ZK_IP] = os.environ['ZOOKEEPER_IP']
        d[PORT] = int(os.environ['PORT']) if 'PORT' in os.environ.keys() else DEFAULT_PORT
        d[NODE_IP] = os.environ['NODE_IP']
        d[ROOT] = boolean_string(os.environ['IS_ROOT'])
    elif where_from == 'args':
        parser = ArgumentParser()
        parser.add_argument(f'--{ZK_IP}', required=True, type=str)
        parser.add_argument(f'--{PORT}', required=False, type=int, default=DEFAULT_PORT)
        parser.add_argument(f'--{NODE_IP}', required=True, type=str)
        parser.add_argument(f'--{ROOT}', required=True, type=boolean_string)
        d = vars(parser.parse_args())

    return d


def register_with_zk(zk: KazooClient, args: dict):
    if args[ROOT]:
        zk.create(path=ZK_ROOT_NAME, value=f'{args[NODE_IP]}:{args[PORT]}'.encode('utf-8'), makepath=True)
        zk_info_dict['zk_node_path'] = ZK_ROOT_NAME
        log_message('registered with ZooKeeper as root')
    else:
        # start at root, then find a node which has only one successor and create a new node
        # we will rely on the automatic sequence numbering to avoid name conflicts
        # since the graph is a tree, we don't need to mark any nodes
        q = queue.Queue()
        q.put(ZK_ROOT_NAME)
        while not q.empty():
            node = q.get()

            children = zk.get_children(node)
            # ZK does not guarantee any order, so for this to work
            # we need to sort the children in order for the tree
            # to be balanced
            children.sort()

            if len(children) < 2:
                # if there is a space, we insert
                zk_info_dict['zk_node_path'] = \
                    zk.create(path=f'{node}/{ZK_CHILD_NAME}', value=f'{config[NODE_IP]}:{config[PORT]}'.encode('utf-8'),
                              makepath=True, sequence=True)
                log_message(f'registered with ZooKeeper as {zk_info_dict["zk_node_path"]}')
                break
            else:
                # otherwise continue
                for child in children:
                    q.put(f'{node}/{child}')


def setup_zk(args: dict) -> KazooClient:
    zk = KazooClient(hosts=f'{args[ZK_IP]}:2181')
    zk.start()

    register_with_zk(zk, args)
    return zk


def get_parent_ip(zk: KazooClient) -> str:
    path = zk_info_dict['zk_node_path'].split('/')
    parent_path = '/'.join(path[:-1])
    ip = zk.get(path=parent_path)[0]
    address = f'http://{ip.decode("utf-8")}/key'
    return address


config = load_config(LOAD_FROM)
log_message(f'loaded config:\n{config}')
zk_client = setup_zk(config)
log_message(f'finished ZooKeeper setup')


# ---------------------------------------------------------------------------------------------------- ZOOKEEPER END

# ---------------------------------------------------------------------------------------------------- API

def send_request(method: str, params: BaseModel, ip: str) -> dict:
    params_dict = params.dict()
    log_message(f'sending parameters {params_dict}')
    method_l = method.lower()
    if method_l == 'delete':
        response = requests.delete(ip, params=params_dict)
    elif method_l == 'get':
        response = requests.get(ip, params=params_dict)
    else:
        response = requests.put(ip, params=params_dict)

    return response.json()


def send_request_async(method: str, params: BaseModel, ip: str) -> None:
    thr = threading.Thread(target=send_request, args=[method, params, ip])
    thr.start()


@app.get('/key', responses={"200": GetResponse, "404": CodeResponse})
def get_key(query: GetQuery):
    """
    Returns the value for a given key if it exists, otherwise returns error 404
    :param query: query
    :return: 200 and value if OK else 404
    """
    if query.key in key_value_storage.keys():
        # if we have it
        log_message(f'GET {query.key}, present on node, result 200')
        return GetResponse(key=query.key, value=key_value_storage[query.key], code=200).json()
    else:
        if config[ROOT]:
            log_message(f'GET {query.key}, not found on root, result 404')
            # if we don't and we are root, just send 404
            return CodeResponse(code=404).json()
        else:
            # if we are not root, ask above
            log_message(f'GET {query.key}, asking {get_parent_ip(zk_client)}')
            response = send_request('get', query, get_parent_ip(zk_client))
            if response['code'] == 404:
                log_message(f'GET {query.key}, not found in parent, result 404')
                return CodeResponse(code=404).json()
            else:
                log_message(f'GET {query.key}, found in parent, caching, result 200')
                key_value_storage[response['key']] = response['value']
                return GetResponse(key=response['key'], value=response['value'], code=200).json()


@app.put('/key', responses={"200": CodeResponse, "201": CodeResponse})
def put_key(query: PutQuery):
    """
    Saves the key-value pair. Rewrites the value if the key exists.
    :param query: query
    :return: 200 if no such key existed, 201 if it was overwritten
    """
    if query.key in key_value_storage.keys():
        log_message(f'PUT {query.key}, result 201')
        code = 201
    else:
        log_message(f'PUT {query.key}, result 200')
        code = 200

    key_value_storage[query.key] = query.value

    # update parent if we are not root
    if not config[ROOT]:
        log_message(f'PUT {query.key}, updating {get_parent_ip(zk_client)}')
        send_request_async('put', query, get_parent_ip(zk_client))

    return CodeResponse(code=code).json()


@app.delete('/key', responses={"201": CodeResponse, "200": CodeResponse})
def delete_key(query: DeleteQuery):
    """
    Deletes the key-value pair.
    :param query:
    :return: 200 if OK, 404 if key dost not exist
    """
    if query.key not in key_value_storage.keys():
        log_message(f'DELETE {query.key}, not found')
        code = 201
    else:
        key_value_storage.pop(query.key)
        log_message(f'DELETE {query.key}, found')
        code = 200

    # if we are not root, update parent
    if not config[ROOT]:
        log_message(f'DELETE {query.key}, propagating to {get_parent_ip(zk_client)}')
        send_request_async('delete', query, get_parent_ip(zk_client))

    return CodeResponse(code=code).json()

# ---------------------------------------------------------------------------------------------------- API END


if config[ROOT]:
    key_value_storage = {'A': 1, 'B': 2}

log_message('starting REST API')
app.run(host='localhost' if MODE == 'local' else '0.0.0.0', port=config[PORT])
