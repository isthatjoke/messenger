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


class Server:
    __slots__ = ('logger', 'ip', 'port', 'sock', 'messages_count', 'client', 'addr', 'message', 'response',
                 'connected_clients', 'r_clients', 'w_clients', 'e_clients', 'messages_lst', 'names')

    def __init__(self, ip_addr, ip_port):
        self.logger = getLogger('app.server')
        self.ip = ip_addr
        self.port = ip_port
        self.client, self.addr = ('', '')
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
                    print(self.r_clients)
                    print(self.w_clients)
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
    @log
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
            client.close()
            return

        self.logger.error(f'created answer to client - {RESPONSE_400}')
        self.send(client, RESPONSE_400)
        return

    @Log()
    @log
    def parse_r_clients(self):
        for client_to_receive in self.r_clients:
            try:
                self.message_handler(receive_msg(client_to_receive), client_to_receive)

            except:
                pass
                # self.r_clients.remove(client_to_receive)

    @Log()
    @log
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
    @log
    def send(self, *args):
        send_msg(*args)

    def __str__(self):
        return {'Server.app'}


if __name__ == '__main__':

    try:
        app = Server(DEFAULT_IP, DEFAULT_PORT)
        app.start()

    except KeyboardInterrupt:
        sys.exit(1)
