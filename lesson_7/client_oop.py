import argparse
from socket import socket, AF_INET, SOCK_STREAM
from additionals.settings import DEFAULT_PORT, DEFAULT_IP, ACTION, PRESENCE, TIME, USER, ACCOUNT_NAME, \
    RESPONSE, ERROR, MESSAGE, MESSAGE_TXT, SENDER
from additionals.utils import send_msg, receive_msg
from additionals.errors import IncorrectData
from logging import getLogger
from log.config import client_log_config
import time, json, sys
from decos import log, Log


class Client:
    __slots__ = 'parser', 'namespace', 'connection_addr', 'connection_port', 'mode', 'logger', 'name', 'message', \
                'message_to_server', 'presence', 'sock', 'response'

    def __init__(self):
        self.parser = argparse.ArgumentParser()
        self.parser.add_argument('addr', default=DEFAULT_IP, nargs='?')
        self.parser.add_argument('port', default=DEFAULT_PORT, nargs='?')
        self.parser.add_argument('-m', '--mode', default='listener', nargs='?')
        self.namespace = self.parser.parse_args(sys.argv[1:])
        self.connection_addr = self.namespace.addr
        self.connection_port = self.namespace.port
        self.mode = self.namespace.mode
        self.logger = getLogger('app.client')
        self.name = "Guest"
        self.message = ''
        self.message_to_server = {}

        try:

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

    @Log()
    @log
    def client_presence(self):
        self.presence = {
            ACTION: PRESENCE,
            TIME: time.time(),
            USER: {
                ACCOUNT_NAME: self.name
            }
        }
        self.logger.debug(f'client created presence: {self.presence}')
        return self.presence

    @Log()
    @log
    def presence_response(self, message):
        try:
            if RESPONSE in message:
                if message[RESPONSE] == 200:
                    return '200 : OK'
                return f'400 : {message[ERROR]}'
            raise IncorrectData

        except IncorrectData:
            self.logger.error(f'received incorrect data')

    @Log()
    @log
    def message_from_server(self, message):

        if ACTION in message and message[ACTION] == MESSAGE and SENDER in message and MESSAGE_TXT in message:
            print(f'{time.ctime()}  message from:  '
                  f'{message[SENDER]}\n'
                  f'{message[MESSAGE_TXT]}')
        else:
            print('error data')

    @Log()
    @log
    def create_message(self):
        self.message = input('type your message here: ')
        self.message_to_server = {
            ACTION: MESSAGE,
            TIME: time.time(),
            ACCOUNT_NAME: self.name,
            MESSAGE_TXT: self.message
        }

        return self.message_to_server

    @Log()
    @log
    def send_mode(self):
        try:
            send_msg(self.sock, self.create_message())

        except (ConnectionRefusedError, ConnectionAbortedError, ConnectionError):
            print('connection interrupted')
            self.logger.error('connection interrupted')
            sys.exit(1)

    @Log()
    @log
    def listen_mode(self):
        try:
            self.message_from_server(receive_msg(self.sock))
        except (ConnectionRefusedError, ConnectionAbortedError, ConnectionError):
            print('connection interrupted')
            self.logger.error('connection interrupted')
            sys.exit(1)

    def start(self):

        try:
            self.sock = socket(AF_INET, SOCK_STREAM)
            self.logger.warning(f'client successfully started socket {self.sock}')
            self.sock.connect((self.connection_addr, self.connection_port))
            self.logger.debug(f'client successfully connected to {self.connection_addr}:{self.connection_port}')
            send_msg(self.sock, self.client_presence())
            self.logger.debug(f'client sent message to {self.sock} with {self.client_presence()}')

        except ConnectionRefusedError:
            self.logger.critical(f'error - connection refused')
            sys.exit(1)

        try:
            self.response = self.presence_response(receive_msg(self.sock))
            self.logger.info(f'client got response - {self.response}')

        except (ValueError, json.JSONDecodeError):
            self.logger.error(f'JSONDecodeError, can not to encode message')

        else:
            if self.mode == 'sender':
                print('sender mode')
            else:
                print('listener mode')
            while True:
                if self.mode == 'sender':
                    self.send_mode()

                if self.mode == 'listener':
                    self.listen_mode()


if __name__ == '__main__':

    try:
        client = Client()
        client.start()

    except SystemError:
        sys.exit(1)