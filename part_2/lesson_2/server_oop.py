from socket import socket, AF_INET, SOCK_STREAM
import sys, json, select, time
from additionals.settings import DEFAULT_PORT, DEFAULT_IP, MAX_CONNECTIONS, \
    RESPONSE_200, RESPONSE_400, ACTION, ACCOUNT_NAME, TIME, PRESENCE, USER, MESSAGE, MESSAGE_TXT, SENDER, ERROR, TO, EXIT
from additionals.utils import send_msg, receive_msg
from additionals.errors import IncorrectData
from logging import getLogger
from log.config import server_log_config
from decos import log, Log
from collections import deque
import argparse, dis
from additionals.server_descriptor import PortVerifier, HostVerifier


@Log()
def arg_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', default=DEFAULT_IP, nargs='?', help='ip address')
    parser.add_argument('-p', default=DEFAULT_PORT, type=int, nargs='?', help=':port')
    namespace = parser.parse_args(sys.argv[1:])
    addr = namespace.a
    port = namespace.p
    return addr, port


class ServerVerifier(type):
    def __init__(self, name, bases, dict):

        methods_lst = []
        func_lst = []
        for el in dict:
            try:
                instruction_bytes = dis.get_instructions(dict[el])
            except TypeError:
                pass
            else:
                for value in instruction_bytes:
                    if value.opname == 'LOAD_METHOD':
                        if value.argval not in methods_lst:
                            methods_lst.append(value.argval)

                    if value.opname == 'LOAD_GLOBAL':
                        if value.argval not in func_lst:
                            func_lst.append(value.argval)

        if 'connect' in methods_lst:
            raise TypeError('error method in client class')

        if not ('AF_INET' in methods_lst and 'SOCK_STREAM' in methods_lst):
            pass
        else:
            raise TypeError('incorrect initialisation of socket')

        super().__init__(name, bases, dict)


class Server(metaclass=ServerVerifier):
    # __slots__ = ('logger', 'ip', 'ip_port', 'sock', 'messages_count', 'client', 'addr', 'message', 'response',
    #              'connected_clients', 'r_clients', 'w_clients', 'e_clients', 'messages_lst', 'names')

    port = PortVerifier()
    ip = HostVerifier()

    def __init__(self, ip_addr, ip_port):
        self.logger = getLogger('app.server')
        self.ip = ip_addr
        self.port = ip_port
        self.logger.warning(f'server starts with {ip_addr}:{ip_port}')
        self.sock = socket(AF_INET, SOCK_STREAM)
        self.logger.debug(f'server successfully started socket {self.sock}')
        self.sock.bind((self.ip, self.port))
        self.logger.debug('server successfully got socket')
        self.connected_clients = deque()
        self.messages_lst = []
        self.r_clients = deque()
        self.w_clients = deque()
        self.e_clients = deque()
        self.message = {}
        self.names = {}
        self.sock.listen(MAX_CONNECTIONS)
        self.sock.settimeout(1)
        self.logger.debug('server started to listen socket')

    def start(self):

        try:
            while True:

                try:
                    self.client, self.addr = self.sock.accept()
                    self.logger.debug(f'clients connected {self.client}')
                except OSError:
                    pass

                else:
                    self.connected_clients.append(self.client)

                try:
                    if self.connected_clients:
                        self.r_clients, self.w_clients, self.e_clients = select.select(self.connected_clients,
                                                                                       self.connected_clients,
                                                                                       [], 0)

                except OSError:
                    pass

                if self.r_clients:
                    self.parse_r_clients()

                if self.messages_lst and self.w_clients:
                    self.parse_w_clients()

        except KeyboardInterrupt:
            self.logger.warning(f'server stopped by user')
            self.sock.close()

    @Log()
    def message_handler(self, message, client):

        if ACTION in message and message[ACTION] == PRESENCE and TIME in message \
                and USER in message:
            if not message[USER][ACCOUNT_NAME] in self.names.keys():
                self.names[message[USER][ACCOUNT_NAME]] = client
                print('200')
                self.send(client, RESPONSE_200)
                return
            else:
                response = RESPONSE_400
                response[ERROR] = f'client with name "{message[USER][ACCOUNT_NAME]}" is in chat already'
                self.send(client, response)
                self.connected_clients.remove(client)
                client.close()
                return

        elif ACTION in message and message[ACTION] == MESSAGE and TIME in message \
                and MESSAGE_TXT in message and SENDER in message and TO in message:
            self.messages_lst.append(message)
            return

        elif ACTION in message and message[ACTION] == EXIT and TIME in message \
                and MESSAGE_TXT in message and SENDER in message:

            self.connected_clients.remove(client)
            self.names.pop(message[SENDER])
            client.close()
            return

        self.logger.error(f'created answer to client - {RESPONSE_400}')
        self.send(client, RESPONSE_400)
        return

    @Log()
    def parse_r_clients(self):
        for client_to_receive in self.r_clients:
            try:
                self.message_handler(receive_msg(client_to_receive), client_to_receive)

            except:
                pass
                # self.r_clients.remove(client_to_receive)

    @Log()
    def parse_w_clients(self):
        for message in self.messages_lst:
            if message[TO] in self.names.keys() and self.names[message[TO]] in self.connected_clients:

                self.message = {
                    ACTION: MESSAGE,
                    SENDER: message[SENDER],
                    TIME: time.time(),
                    MESSAGE_TXT: message[MESSAGE_TXT]
                }

                self.messages_lst.remove(message)
                self.send(self.names[message[TO]], self.message)

    @Log()
    def send(self, *args):
        send_msg(*args)

    def __str__(self):
        return {'Server.app'}


if __name__ == '__main__':

    ip_addr, ip_port = arg_parser()
    app = Server(ip_addr, ip_port)
    app.start()

