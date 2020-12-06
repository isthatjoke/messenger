from socket import socket, AF_INET, SOCK_STREAM
from additionals.settings import DEFAULT_PORT, PACK_CAPACITY, DEFAULT_IP
from additionals.utils import send_msg, receive_msg
import time, json, sys


def client_presence(name='Guest'):

    presence = {
        'action': 'presence',
        'time': time.time(),
        'user': {
            'account_name': name
        }
    }

    return presence


def presence_response(message):
    if 'response' in message:
        if message['response'] == 200:
            return '200 : OK'
        return f'400 : {message["ERROR"]}'
    raise ValueError


def main():
    try:
        connection_addr = sys.argv[1]
        connection_port = int(sys.argv[2])
        if 65535 < connection_port < 1024:
            raise ValueError
    except IndexError:
        connection_port = DEFAULT_PORT
        connection_addr = DEFAULT_IP
    except ValueError:
        print('port must be in range 1024 - 65535')
        sys.exit(1)

    sock = socket(AF_INET, SOCK_STREAM)
    sock.connect((connection_addr, connection_port))
    presence_msg = client_presence()
    send_msg(sock, presence_msg)
    try:
        response = presence_response(receive_msg(sock))
        print(response)
    except (ValueError, json.JSONDecodeError):
        print('decode fault')


if __name__ == '__main__':
    main()
