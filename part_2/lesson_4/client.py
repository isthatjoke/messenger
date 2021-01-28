import argparse
import json
import sys
import time
from logging import getLogger
from socket import socket, AF_INET, SOCK_STREAM
import threading
from additionals.client_descriptor import PortVerifier, HostVerifier
from additionals.errors import IncorrectData, ClientError
from additionals.settings import DEFAULT_PORT, DEFAULT_IP, ACTION, PRESENCE, TIME, USER, ACCOUNT_NAME, \
    RESPONSE, ERROR, MESSAGE, MESSAGE_TXT, SENDER, TO, EXIT, RESPONSE_OK, ADD_CONTACT, USERS_REQUEST, GET_CONTACTS
from additionals.utils import send_msg, receive_msg
from decos import Log
from client_database import ClientDB
from Client_Meta import ClientVerifier

sock_lock = threading.Lock()
database_lock = threading.Lock()


@Log()
def arg_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', default=DEFAULT_IP, nargs='?', help='ip address')
    parser.add_argument('-p', default=DEFAULT_PORT, type=int, nargs='?', help=':port')
    parser.add_argument('-n', default='Guest', nargs='?', help='your nick name')
    namespace = parser.parse_args(sys.argv[1:])
    addr = namespace.a
    port = namespace.p
    name = namespace.n
    return addr, port, name


class Client(threading.Thread, metaclass=ClientVerifier):
    # __slots__ = ('parser', 'namespace', 'connection_addr', 'connection_port', 'mode', 'logger', 'name', 'message',
    #              'message_to_server', 'presence', 'sock', 'response', 'daemon', 'send_thread', 'listen_thread',
    #              'buddy_name', 'command')

    ip = HostVerifier()
    port = PortVerifier()

    def __init__(self, ip, port, name):
        super().__init__()
        self.daemon = True
        self.ip = ip
        self.port = port
        self.name = name
        self.logger = getLogger('app.client')
        self.message_to_server = {}
        self.database = ClientDB(self.name)

    @Log()
    def socket_load(self):
        try:
            self.sock = socket(AF_INET, SOCK_STREAM)
            self.logger.warning(f'client successfully started socket {self.sock}')
            self.sock.connect((self.ip, self.port))
            self.logger.debug(f'client successfully connected to {self.ip}:{self.port}')

        except ConnectionRefusedError:
            self.logger.critical(f'error - connection refused')
            sys.exit(1)

        except KeyboardInterrupt:
            print('client exited')
            sys.exit(1)


    @Log()
    def database_load(self):

        try:
            self.users_list = self.users_list_request()
        except ClientError:
            self.logger.error('error with users list request from server')
        else:
            self.database.add_users(self.users_list)
            self.logger.debug('users list was added to database')
        try:
            self.contacts_list = self.contacts_list_request()
        except ClientError:
            self.logger.error('error with contacts list request from server')
        else:
            for contact in self.contacts_list:
                self.database.add_contact(contact)
            self.logger.debug('contacts list was added to database')

    def start(self):
        self.socket_load()
        send_msg(self.sock, self.client_presence())
        self.presence_response(receive_msg(self.sock))
        self.database_load()
        self.logger.debug(f'client sent message to {self.sock} with {self.client_presence()}')
        self.logger.debug(f'database loaded successfully')
        try:

            self.send_thread = threading.Thread(target=self.send_mode)
            self.listen_thread = threading.Thread(target=self.listen_mode)

            for thread_ in [self.send_thread, self.listen_thread]:
                thread_.start()
                self.logger.debug('thread started successfully')
            self.listen_thread.join()
            self.logger.debug('listen thread joined')

        except ConnectionRefusedError:
            self.logger.critical(f'error - connection refused')
            self.send_thread.do_run = False
            self.listen_thread.do_run = False
            sys.exit(1)

        except KeyboardInterrupt:
            print('client exited')
            self.logger.warning('ctrl+c on starting threads')
            sys.exit(1)

        try:

            self.response = self.presence_response(receive_msg(self.sock))
            print(self.response)
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
            self.logger.info(f'connected to chat with nick - {self.name}')
        while True:
            time.sleep(1)
            if self.send_thread.is_alive() and self.listen_thread.is_alive():
                continue
            break

    def users_list_request(self):
        self.logger.debug(f'making users_client_request {self.name}')
        self.request = {
            ACTION: USERS_REQUEST,
            TIME: time.time(),
            SENDER: self.name
        }
        self.logger.debug(f'users_client_request formed by {self.request}')
        send_msg(self.sock, self.request)
        self.logger.debug('users_client_request has been sent')
        self.users_list = receive_msg(self.sock)
        self.logger.debug(f'users_client_request has been received {self.users_list}')
        return self.users_list[USERS_REQUEST]

    def contacts_list_request(self):
        self.logger.debug(f'making contacts_client_request {self.name}')
        self.request = {
            ACTION: GET_CONTACTS,
            TIME: time.time(),
            SENDER: self.name
        }
        self.logger.debug(f'contacts_client_request formed by {self.request}')
        send_msg(self.sock, self.request)
        self.logger.debug('contacts_client_request has been sent')
        self.contacts_list = receive_msg(self.sock)
        self.logger.debug(f'contacts_client_request has been received {self.contacts_list}')
        return self.contacts_list[GET_CONTACTS]

    @Log()
    def client_presence(self):
        self.logger.debug(f'{self.name} started creating presence to server')
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
        self.logger.debug(f'client received presence response from server {message}')
        try:
            if RESPONSE in message:
                if message[RESPONSE] == 200:
                    return RESPONSE_OK
                return f'400 : {message[ERROR]}'
            raise IncorrectData

        except IncorrectData:
            self.logger.error(f'received incorrect data {message}')

    @Log()
    def message_from_server(self, message):
        self.logger.debug(f'client received message from server {message}')
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

            elif RESPONSE in message and USERS_REQUEST in message:
                if message[RESPONSE] == 202:
                    self.database.add_users(message[USERS_REQUEST])
                    return

            elif RESPONSE in message and GET_CONTACTS in message:
                if message[RESPONSE] == 203:
                    self.database.add_contact(message[GET_CONTACTS])
                    return

            else:
                print('error data')

        except json.JSONDecodeError:
            self.logger.error(f'received incorrect data')

    @Log()
    def create_message(self):
        self.logger.debug('client creating a message')
        self.message_to_server = {
            ACTION: MESSAGE,
            TIME: time.time(),
            TO: self.buddy_name,
            SENDER: self.name,
            MESSAGE_TXT: self.message
        }
        self.logger.debug(f'client created a message {self.message_to_server}')
        return self.message_to_server

    @Log()
    def exit_message(self):
        self.logger.debug('client creating exit message')
        self.message_to_server = {
            ACTION: EXIT,
            TIME: time.time(),
            SENDER: self.name,
        }
        self.logger.debug(f'client created exit message {self.message_to_server}')
        return self.message_to_server

    @Log()
    def get_history(self):
        ask = input('Show only incoming messages - "in", outgoing - "out", all messages - just push Enter: ')
        with database_lock:
            if ask == 'in':
                history_list = self.database.get_history(to_=self.name)
                for message in history_list:
                    print(f'\nMessage from user: {message[0]} at {message[3]}:\n{message[2]}')
            elif ask == 'out':
                history_list = self.database.get_history(from_=self.name)
                for message in history_list:
                    print(f'\nMessage to user: {message[1]} at {message[3]}:\n{message[2]}')
            else:
                history_list = self.database.get_history()
                for message in history_list:
                    print(
                        f'\nMessage from user: {message[0]}, to user {message[1]} at {message[3]}:\n{message[2]}')

    @Log()
    def edit_contacts(self):
        ans = input('Remove contact - "del", Add contact - "add": ')
        if ans == 'del':
            edit = input('Type contact username: ')
            with database_lock:
                if self.database.check_contact(edit):
                    self.database.del_contact(edit)
                else:
                    self.logger.error('Client tried to remove unknown user')
                with sock_lock:
                    try:
                        return self.remove_contact(edit)
                    except ClientError:
                        self.logger.error('Unable to send request to server')
        elif ans == 'add':
            edit = input('Type contact username: ')
            if self.database.check_user(edit):
                with database_lock:
                    self.database.add_contact(edit)
                with sock_lock:
                    try:
                        return self.add_contact(edit)
                    except ClientError:
                        self.logger.error('Unable to send request to server')

    @Log()
    def add_contact(self, contact):
        self.logger.debug(f'Creating new contact {contact}')
        self.request = {
            ACTION: ADD_CONTACT,
            TIME: time.time(),
            SENDER: self.name,
            ACCOUNT_NAME: contact
        }
        return self.request

    @Log()
    def remove_contact(self, contact):
        self.logger.debug(f'Removing contact {contact}')
        self.request = {
            ACTION: ADD_CONTACT,
            TIME: time.time(),
            SENDER: self.name,
            ACCOUNT_NAME: contact
        }
        return self.request

    @Log()
    def client_handler(self):
        print('FAQ:\n'
              'type "message" to init messaging \n'
              'type "exit" to close chat \n'
              'type "contacts" to get contact list \n'
              'type "history" to get message history \n'
              'type "edit" to manage your friend list \n')

        self.command = input('type your choice: ')

        if self.command == 'message':
            self.buddy_name = input('send message to: ')
            with database_lock:
                if not self.database.check_user(self.buddy_name):
                    self.logger.error(
                        f'Client tried to send message to unknown user: {self.buddy_name}')
                    return
            self.message = input('type your message: ')
            with database_lock:
                self.database.save_new_message(self.name, self.buddy_name, self.message)
            return self.create_message()

        elif self.command == 'contacts':
            with database_lock:
                contacts_list = self.database.get_contacts()
            for contact in contacts_list:
                print(contact)
            return

        elif self.command == 'edit':
            return self.edit_contacts()

        elif self.command == 'history':
            self.get_history()
            return

        elif self.command == 'exit':
            try:
                print('connection refused')
                send_msg(self.sock, self.exit_message())
                self.send_thread.do_run = False
                self.listen_thread.do_run = False
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
                self.answer = self.client_handler()
                if self.answer == None or self.answer == '':
                    pass
                else:
                    send_msg(self.sock, self.answer)

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


def main():
    ip, port, name = arg_parser()
    app = Client(ip, port, name)
    app.start()


if __name__ == '__main__':
    main()
