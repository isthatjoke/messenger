from threading import Thread
from socket import socket, AF_INET, SOCK_STREAM
from additionals.settings import DEFAULT_PORT, DEFAULT_IP, ACTION, PRESENCE, TIME, USER, ACCOUNT_NAME, \
    RESPONSE, ERROR, MESSAGE, MESSAGE_TXT, SENDER, TO, EXIT, RESPONSE_OK
from additionals.utils import send_msg, receive_msg
from additionals.errors import IncorrectData
from logging import getLogger
from log.config import client_log_config
import time, json, sys, argparse, dis
from decos import log, Log
from additionals.client_descriptor import PortVerifier, HostVerifier


@Log()
def arg_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', default=DEFAULT_IP, nargs='?', help='ip address')
    parser.add_argument('-p', default=DEFAULT_PORT, type=int, nargs='?', help=':port')
    parser.add_argument('-n', default='Guest', nargs='?', help='your nick name')
    #parser.add_argument('-m', '--mode', default='listener', nargs='?')
    namespace = parser.parse_args(sys.argv[1:])
    addr = namespace.a
    port = namespace.p
    name = namespace.n
    return addr, port, name


class ClientVerifier(type):
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

        for method in ('accept', 'listen', 'socket'):
            if method in methods_lst:
                raise TypeError('error method in client class')

        if 'seng_msg' in func_lst or 'receive_msg' in func_lst:
            pass
        else:
            raise TypeError("there's no socket functions in class")

        super().__init__(name, bases, dict)


class Client(Thread, metaclass=ClientVerifier):
    # __slots__ = ('parser', 'namespace', 'connection_addr', 'connection_port', 'mode', 'logger', 'name', 'message',
    #              'message_to_server', 'presence', 'sock', 'response', 'daemon', 'send_thread', 'listen_thread',
    #              'buddy_name', 'command')

    connection_port = PortVerifier()
    connection_addr = HostVerifier()

    def __init__(self, addr, port, name):
        super().__init__()
        self.connection_addr = addr
        self.connection_port = port
        self.name = name
        self.logger = getLogger('app.client')
        self.message_to_server = {}
        self.daemon = True

        

    @Log()
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
    def presence_response(self, message):
        try:
            if RESPONSE in message:
                if message[RESPONSE] == 200:
                    return RESPONSE_OK
                return f'400 : {message[ERROR]}'
            raise IncorrectData

        except IncorrectData:
            self.logger.error(f'received incorrect data')

    @Log()
    def message_from_server(self, message):
        try:
            if RESPONSE in message:
                if message[RESPONSE] == 200:
                    print('200 : OK')
                    return
                print(f'400 : {message[ERROR]}')
                return

            elif ACTION in message and message[ACTION] == MESSAGE and SENDER in message and MESSAGE_TXT in message:
                print(f'\n{time.ctime()}  message from:  '
                      f'{message[SENDER]}\n'
                      f'{message[MESSAGE_TXT]}')
            else:
                print('error data')

        except json.JSONDecodeError:
            self.logger.error(f'received incorrect data')

    @Log()
    def create_message(self):

        self.message_to_server = {
            ACTION: MESSAGE,
            TIME: time.time(),
            TO: self.buddy_name,
            SENDER: self.name,
            MESSAGE_TXT: self.message
        }

        return self.message_to_server

    @Log()
    def exit_message(self):

        self.message_to_server = {
            ACTION: EXIT,
            TIME: time.time(),
            SENDER: self.name,
            MESSAGE_TXT: EXIT
        }

        return self.message_to_server

    @Log()
    def client_handler(self):
        print('FAQ:\n'
              'type "message" to init messaging \n'
              'type "exit" to close chat \n')
        self.command = input('type your choice: ')

        if self.command == 'message':
            self.buddy_name = input('send message to: ')
            self.message = input('type your message here: ')
            self.create_message()
            return self.message_to_server

        elif self.command == 'exit':
            try:
                self.exit_message()
                print('connection refused')
                send_msg(self.sock, self.exit_message())
                sys.exit(1)
            finally:
                sys.exit(1)
        else:
            print('incorrect command')

    @Log()
    def send_mode(self):
        print(f'connected to chat with nick - {self.name}')
        while True:
            try:
                send_msg(self.sock, self.client_handler())

            except json.JSONDecodeError:
                sys.exit()

            except (ConnectionRefusedError, ConnectionAbortedError, ConnectionError):
                print('connection interrupted')
                self.logger.error('connection interrupted')
                sys.exit(1)

    @Log()
    def listen_mode(self):
        while True:
            try:
                self.message_from_server(receive_msg(self.sock))

            except json.JSONDecodeError:
                sys.exit()

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
            self.send_thread = Thread(target=self.send_mode)
            self.listen_thread = Thread(target=self.listen_mode)
            self.send_thread.start()
            self.listen_thread.start()
            self.send_thread.join()
            self.listen_thread.join()

        except ConnectionRefusedError:
            self.logger.critical(f'error - connection refused')
            sys.exit(1)

        except KeyboardInterrupt:
            print('client exited')
            sys.exit(1)

        try:

            self.response = self.presence_response(receive_msg(self.sock))
            if self.response == RESPONSE_OK:
                self.logger.info(f'client got response - {self.response}')
            else:
                self.logger.error(f'client got response - {self.response}')
                sys.exit(1)

        except (ValueError, json.JSONDecodeError):
            self.logger.error(f'JSONDecodeError, can not to encode message')

        else:

            self.send_mode()
            self.listen_mode()
            print(f'connected to chat with nick - {self.name}')
        while True:
            time.sleep(1)
            if self.send_thread.is_alive() and self.listen_thread.is_alive():
                continue
            break


if __name__ == '__main__':
    addr, port, name = arg_parser()
    client = Client(addr, port, name)
    client.start()
