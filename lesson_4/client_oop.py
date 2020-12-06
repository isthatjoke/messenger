from socket import socket, AF_INET, SOCK_STREAM
from additionals.settings import DEFAULT_PORT, PACK_CAPACITY, DEFAULT_IP
from additionals.utils import send_msg, receive_msg
import time, json, sys


class Client:

    def __init__(self):
        try:
            self.connection_addr = sys.argv[1]
            self.connection_port = int(sys.argv[2])
            if 65535 < self.connection_port < 1024:
                raise ValueError
        except IndexError:
            self.connection_port = DEFAULT_PORT
            self.connection_addr = DEFAULT_IP
        except ValueError:
            print('port must be in range 1024 - 65535')
            sys.exit(1)

    def client_presence(self, name='Guest'):

        self.presence = {
            'action': 'presence',
            'time': time.time(),
            'user': {
                'account_name': name
            }
        }

        return self.presence

    def presence_response(self, message):
        if 'response' in message:
            if message['response'] == 200:
                return '200 : OK'
            return f'400 : {message["ERROR"]}'
        raise ValueError

    def start(self):
        self.sock = socket(AF_INET, SOCK_STREAM)
        self.sock.connect((self.connection_addr, self.connection_port))
        self.presence_msg = self.client_presence()
        send_msg(self.sock, self.presence_msg)
        try:
            self.response = self.presence_response(receive_msg(self.sock))
            print(self.response)
        except (ValueError, json.JSONDecodeError):
            print('decode fault')


if __name__ == '__main__':
    client = Client()
    client.start()
