from socket import socket, AF_INET, SOCK_STREAM
import sys, json, select, time
from additionals.settings import DEFAULT_PORT, DEFAULT_IP, MAX_CONNECTIONS, \
    RESPONSE_200, RESPONSE_400, ACTION, ACCOUNT_NAME, TIME, PRESENCE, USER, MESSAGE, MESSAGE_TXT, SENDER
from additionals.utils import send_msg, receive_msg
from additionals.errors import IncorrectData
from logging import getLogger
from log.config import server_log_config
from decos import log, Log
from collections import deque


class Server:
    __slots__ = ('logger', 'ip', 'port', 'sock', 'messages_count', 'client', 'addr', 'message', 'response',
                 'connected_clients', 'r_clients', 'w_clients', 'e_clients', 'messages_lst')

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
        self.messages_lst = deque()
        self.r_clients = deque()
        self.w_clients = deque()
        self.e_clients = deque()
        self.message = {}
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
    @log
    def message_handler(self, message, client):

        if ACTION in message and message[ACTION] == PRESENCE and TIME in message \
                and USER in message and message[USER][ACCOUNT_NAME] == 'Guest':
            self.logger.info(f'created answer to client - {RESPONSE_200}')
            self.send(client, RESPONSE_200)
            return
        elif ACTION in message and message[ACTION] == MESSAGE and TIME in message \
                and MESSAGE_TXT in message:
            self.messages_lst.append((message[ACCOUNT_NAME], message[MESSAGE_TXT]))
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
        self.message = {
            ACTION: MESSAGE,
            SENDER: self.messages_lst[0][0],
            TIME: time.time(),
            MESSAGE_TXT: self.messages_lst[0][1]
        }

        self.messages_lst.popleft()

        for client_to_send in self.w_clients:
            try:
                self.send(client_to_send, self.message)

            except:
                pass
                # self.connected_clients.remove(client_to_send)

    @Log()
    @log
    def send(self, *args):
        send_msg(*args)
        self.logger.debug(f'message sent to {self.client} with {self.response}')

    def __str__(self):
        return {'Server.app'}


if __name__ == '__main__':

    try:
        app = Server(DEFAULT_IP, DEFAULT_PORT)
        app.start()

    except KeyboardInterrupt:
        sys.exit(1)
