from argparse import ArgumentParser
from kivds_client import Client
from kivds_client.api.default.get_key import sync as get_key_sync
from kivds_client.api.default.put_key import sync as put_key_sync
from kivds_client.api.default.delete_key import sync as delete_key_sync


def get_key(args: list):
    if len(args) != 1:
        print("get requires one argument - key")
        return
    response = get_key_sync(client=api_client, key=args[0])
    if response.code == 200:
        print(f'key: {response.key}\t value: {response.value}')
    elif response.code == 404:
        print(f'key {args[0]} was not found')
    else:
        print(f'an error occured: {response.code}')


def put_key(args: list):
    if len(args) != 2:
        print("put requires two arguments - key and value")
        return
    response = put_key_sync(client=api_client, key=args[0], value=args[1])
    if response.code == 200:
        print(f'key {args[0]} was set to {args[1]}')
    elif response.code == 201:
        print(f'key {args[0]} was overwritten to {args[1]}')
    else:
        print(f'an error occured: {response.code}')


def delete_key(args: list):
    if len(args) != 1:
        print("delete requires one argument - key")
        return
    response = delete_key_sync(client=api_client, key=args[0])
    if response.code == 200:
        print(f'key: {args[0]} was deleted')
    elif response.code == 201:
        print(f'key {args[0]} was not found')
    else:
        print(f'an error occured: {response.code}')


command_method_dict = {
    'get': get_key,
    'put': put_key,
    'delete': delete_key
}


def main():
    while True:
        print('> ', end='')
        inp = input()
        split = inp.split()

        command = split[0].lower()
        if command not in command_method_dict.keys():
            if command == 'exit':
                break
            print('Unknown command')
            continue

        method = command_method_dict[command]
        args = [] if len(split) < 2 else split[1:]
        method(args)


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--server_ip', required=True, type=str)
    config = vars(parser.parse_args())
    api_client = Client(base_url=config['server_ip'], timeout=5, verify_ssl=False)
    main()