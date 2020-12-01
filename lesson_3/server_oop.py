from socket import socket, AF_INET, SOCK_STREAM, SHUT_RDWR
import sys, json
from additionals.settings import DEFAULT_PORT, DEFAULT_IP, ENCODING, MAX_CONNECTIONS, PACK_CAPACITY
from additionals.utils import send_msg, receive_msg
import time


class Server:

    def __init__(self, ip_addr, ip_port):
        self.ip = ip_addr
        self.port = ip_port
        self.sock = socket(AF_INET, SOCK_STREAM)
        self.sock.bind((self.ip, self.port))
        self.messages = 0

    def start(self):
        self.sock.listen(MAX_CONNECTIONS)
        print(f' server started at {time.ctime()}')
        try:
            while True:
                self.client, self.addr = self.sock.accept()
                self.message = receive_msg(self.client)
                if self.message:
                    self.messages += 1
                    print(f'server received {self.messages} messages')
                self.response = self.check_presence(self.message)
                self.send()
        except KeyboardInterrupt:
            print(f'\n server was closed at {time.ctime()}')
            self.sock.close()

    def check_presence(self, message):
        if 'action' in message and message['action'] == 'presence' and 'time' in message \
                and 'user' in message and message['user']['account_name'] == 'Guest':
            return {'response': 200}
        return {'response': 400, 'ERROR': 'Bad Request'}

    def send(self):
        send_msg(self.client, self.response)
        self.client.close()


if __name__ == '__main__':
    try:
        app = Server('', DEFAULT_PORT)
        app.start()

    except KeyboardInterrupt:
        sys.exit(1)

