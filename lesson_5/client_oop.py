from socket import socket, AF_INET, SOCK_STREAM
from additionals.settings import DEFAULT_PORT, DEFAULT_IP, ACTION, PRESENCE, TIME, USER, ACCOUNT_NAME, RESPONSE, ERROR
from additionals.utils import send_msg, receive_msg
from logging import getLogger
from log.config import client_log_config
import time, json, sys


class Client:

    def __init__(self):
        self.logger = getLogger('app.client')
        try:
            self.connection_addr = sys.argv[1]
            self.connection_port = int(sys.argv[2])
            self.logger.debug(f'clients starts with {self.connection_addr}:{self.connection_port}')
            if 65535 < self.connection_port < 1024:
                raise ValueError
        except IndexError:
            self.connection_port = DEFAULT_PORT
            self.connection_addr = DEFAULT_IP
            self.logger.debug(f'clients starts without additional arguments '
                              f'with default settings - {DEFAULT_IP}:{DEFAULT_PORT}')
        except ValueError:
            self.logger.critical(f'port is out off range 1024 - 65535')
            sys.exit(1)

    def client_presence(self, name='Guest'):
        self.presence = {
            ACTION: PRESENCE,
            TIME: time.time(),
            USER: {
                ACCOUNT_NAME: name
            }
        }
        self.logger.debug(f"client created presence: {self.presence}")
        return self.presence

    def presence_response(self, message):
        if RESPONSE in message:
            if message[RESPONSE] == 200:
                return '200 : OK'
            return f'400 : {message[ERROR]}'
        raise ValueError

    def start(self):
        try:
            self.sock = socket(AF_INET, SOCK_STREAM)
            self.logger.warning(f'client successfully started socket {self.sock}')
            self.sock.connect((self.connection_addr, self.connection_port))
            self.logger.debug(f'client successfully connected to {self.connection_addr}:{self.connection_port}')
            self.presence_msg = self.client_presence()
            send_msg(self.sock, self.presence_msg)
            self.logger.debug(f'client sent message to {self.sock} with {self.presence_msg}')

        except ConnectionRefusedError:
            self.logger.critical(f'error - connection refused')
            sys.exit(1)

        try:
            self.response = self.presence_response(receive_msg(self.sock))
            self.logger.info(f'client got response - {self.response}')
            print(self.response)

        except (ValueError, json.JSONDecodeError):
            self.logger.error(f'JSONDecodeError, can not to encode message')

        finally:
            self.logger.warning(f'clients stops')
            sys.exit(0)


if __name__ == '__main__':
    try:
        client = Client()
        client.start()
    except SystemError:
        sys.exit(1)