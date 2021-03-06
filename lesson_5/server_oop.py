from socket import socket, AF_INET, SOCK_STREAM
import sys
from additionals.settings import DEFAULT_PORT, DEFAULT_IP, MAX_CONNECTIONS,\
    RESPONSE_200, RESPONSE_400, ACTION, ACCOUNT_NAME, TIME, PRESENCE, USER
from additionals.utils import send_msg, receive_msg
from logging import getLogger
from log.config import server_log_config


class Server:

    def __init__(self, ip_addr, ip_port):
        self.logger = getLogger('app.server')
        self.ip = ip_addr
        self.port = ip_port
        self.logger.warning(f'server starts with {ip_addr}:{ip_port}')
        self.sock = socket(AF_INET, SOCK_STREAM)
        self.logger.debug(f'server successfully started socket {self.sock}')
        self.sock.bind((self.ip, self.port))
        self.logger.debug('server successfully got socket')
        self.messages = 0

    def start(self):
        self.sock.listen(MAX_CONNECTIONS)
        self.logger.debug('server started to listen socket')
        try:
            while True:
                self.client, self.addr = self.sock.accept()
                self.message = receive_msg(self.client)
                self.logger.debug(f'server got message from {self.client}')
                if self.message:
                    self.messages += 1
                    self.logger.info(f'server got {self.messages} messages since has been started')
                self.response = self.check_presence(self.message)
                self.send()
                self.logger.debug(f'message sent to {self.client}')
        except KeyboardInterrupt:
            self.logger.warning(f'server stopped')
            self.sock.close()

    def check_presence(self, message):
        self.logger.debug(f'Checking presence from {self.client}: {message}')
        if ACTION in message and message[ACTION] == PRESENCE and TIME in message \
                and USER in message and message[USER][ACCOUNT_NAME] == 'Guest':
            self.logger.info(f'created answer to client - {RESPONSE_200}')
            return RESPONSE_200
        self.logger.error(f'created answer to client - {RESPONSE_400}')
        return RESPONSE_400

    def send(self):
        send_msg(self.client, self.response)
        self.logger.debug(f'message sent to {self.client} with {self.response}')
        self.logger.debug(f'connection closed to {self.client}')
        self.client.close()


if __name__ == '__main__':
    try:
        app = Server(DEFAULT_IP, DEFAULT_PORT)
        app.start()

    except KeyboardInterrupt:
        sys.exit(1)
