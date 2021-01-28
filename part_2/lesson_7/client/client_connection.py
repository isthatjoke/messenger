import hmac
import json
import sys
import time
import threading
from logging import getLogger
from socket import socket, AF_INET, SOCK_STREAM
from PyQt5.QtCore import QObject, pyqtSignal
from additionals.client_descriptor import PortVerifier, HostVerifier
from additionals.errors import IncorrectData, ClientError
from additionals.settings import ACTION, PRESENCE, TIME, USER, ACCOUNT_NAME, \
    RESPONSE, ERROR, MESSAGE, MESSAGE_TXT, SENDER, TO, EXIT, RESPONSE_OK, ADD_CONTACT, USERS_REQUEST, GET_CONTACTS, \
    REMOVE_CONTACT, PASSWORD, REGISTER, SECRET, PUB_KEY, PUBLIC_KEY_REQUEST, DATA
from additionals.utils import send_msg, receive_msg
from additionals.decos import Log


sock_lock = threading.Lock()


class Client(threading.Thread, QObject):
    """
    main client_ class
    """
    ip = HostVerifier()
    port = PortVerifier()
    new_message = pyqtSignal(dict)
    connection_lost = pyqtSignal()

    def __init__(self, ip, port, name, password, database, keys, to_register=False):
        """
        initialization of client_ class
        @param ip: ip address
        @param port: ip port
        @param name: username
        @param password: user password
        @param database: connected database
        @param to_register: register flag
        @param keys: keys to decrypt messages
        """
        threading.Thread.__init__(self)
        QObject.__init__(self)
        self.ip = ip
        self.port = port
        self.name = name
        self.keys = keys
        self.wrong_password = False
        self.password = str(password)
        self.to_register = to_register
        self.sock = None
        self.logger = getLogger('app.client_')
        self.database = database
        self.socket_load()
        self.database_load()
        self.running = True


    @Log()
    def socket_load(self):
        """
        connect socket
        @return:
        """
        self.sock = socket(AF_INET, SOCK_STREAM)
        self.sock.settimeout(5)
        try:
            self.logger.warning(f'client_ successfully started socket {self.sock}')
            self.sock.connect((self.ip, self.port))
            self.logger.debug(f'client_ successfully connected to {self.ip}:{self.port}')
            # if self.authenticate_request():
            #     self.logger.debug('client_ verified')
            # else:
            #     raise ConnectionRefusedError

        except ConnectionRefusedError:
            self.logger.critical(f'error - connection refused')
            sys.exit(1)

        except KeyboardInterrupt:
            print('client_ exited')
            sys.exit(1)
        else:
            self.pubkey = self.keys.publickey().export_key().decode('ascii')
            if self.to_register:
                try:
                    with sock_lock:
                        send_msg(self.sock, self.client_register())
                        self.presence_response(receive_msg(self.sock))
                except (OSError, json.JSONDecodeError):
                    self.logger.critical('connection lost')
            else:
                try:
                    with sock_lock:
                        send_msg(self.sock, self.client_presence())
                        self.presence_response(receive_msg(self.sock))
                except (OSError, json.JSONDecodeError):
                    self.logger.critical('connection lost')
            self.logger.info('connected to server_')

    @Log()
    def database_load(self):
        """
        connect database
        @return:
        """
        try:
            self.users_list = self.users_list_request()
        except ClientError:
            self.logger.error('error with users list request from server_')
        else:
            self.database.add_users(self.users_list)
            self.logger.debug('users list was added to database')
        try:
            self.contacts_list = self.contacts_list_request()
        except ClientError:
            self.logger.error('error with contacts list request from server_')
        else:
            for contact in self.contacts_list:
                self.database.add_contact(contact)
            self.logger.debug('contacts list was added to database')

    def run(self):
        while self.running:
            time.sleep(1)
            with sock_lock:
                try:
                    self.sock.settimeout(0.5)
                    message = receive_msg(self.sock)

                except OSError as err:
                    if err.errno:
                        self.logger.critical(f'connection lost')
                        self.running = False
                        self.connection_lost.emit()

                except (ConnectionError, ConnectionAbortedError, ConnectionResetError,
                        json.JSONDecodeError, TypeError):
                    self.logger.debug(f'connection lost')
                    self.running = False
                    self.connection_lost.emit()

                else:
                    self.logger.debug(f'received message {message}')
                    self.message_from_server(message)

                finally:
                    self.sock.settimeout(5)

    @Log()
    def authenticate_request(self):
        """
        send auth request to server_
        @return: bool
        """
        with sock_lock:
            auth_message = receive_msg(self.sock)
            hash = hmac.new(SECRET, auth_message, digestmod='sha256')
            digest = hash.digest()
            send_msg(self.sock, digest)
            ans = receive_msg(self.sock)
            if RESPONSE in ans:
                if ans[RESPONSE] == 200:
                    return True
            return False

    @Log()
    def users_list_request(self):
        """
        all users request from database
        @return: users list
        """
        self.logger.debug(f'making users_client_request {self.name}')
        request = {
            ACTION: USERS_REQUEST,
            TIME: time.time(),
            SENDER: self.name
        }
        self.logger.debug(f'users_client_request formed by {request}')
        with sock_lock:
            send_msg(self.sock, request)
            self.logger.debug('users_client_request has been sent')
            self.users_list = receive_msg(self.sock)
        if RESPONSE in self.users_list and self.users_list[RESPONSE] == 202:
            self.logger.debug(f'users_client_request has been received {self.users_list}')
            return self.users_list[USERS_REQUEST]
        return

    @Log()
    def contacts_list_request(self):
        """
        contacts request from database
        @return: contacts list
        """
        self.logger.debug(f'making contacts_client_request {self.name}')
        request = {
            ACTION: GET_CONTACTS,
            TIME: time.time(),
            SENDER: self.name
        }
        self.logger.debug(f'contacts_client_request formed by {request}')
        with sock_lock:
            send_msg(self.sock, request)
            self.logger.debug('contacts_client_request has been sent')
            self.contacts_list = receive_msg(self.sock)
        if RESPONSE in self.contacts_list and self.contacts_list[RESPONSE] == 203:
            self.logger.debug(f'contacts_client_request has been received {self.contacts_list}')
            return self.contacts_list[GET_CONTACTS]
        return

    @Log()
    def client_presence(self):
        """
        func creates login presence message to server_
        @return: dict
        """
        self.logger.debug(f'{self.name} started creating presence to server_')
        self.login_presence = {
            ACTION: PRESENCE,
            TIME: time.time(),
            USER: {
                ACCOUNT_NAME: self.name,
                PASSWORD: self.password,
                PUB_KEY: self.pubkey
            }
        }
        self.logger.debug(f'client_ created presence: {self.login_presence}')
        return self.login_presence

    @Log()
    def client_register(self):
        """
        func creates register presence message to server_
        @return: dict
        """
        self.logger.debug(f'{self.name} started register on server_')
        self.register_presence = {
            ACTION: REGISTER,
            TIME: time.time(),
            USER: {
                ACCOUNT_NAME: self.name,
                PASSWORD: self.password,
                PUB_KEY: self.pubkey
            }
        }
        self.logger.debug(f'client_ created presence: {self.register_presence}')
        return self.register_presence

    @Log()
    def presence_response(self, message):
        """
        func catch presence response from server_
        @param message: dict
        @return: bool
        """
        self.logger.debug(f'client_ received presence response from server_ {message}')
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
        """
        message handler from server_
        @param message: dict
        @return:
        """
        self.logger.debug(f'client_ received message from server_ {message}')
        try:
            if RESPONSE in message:
                if message[RESPONSE] == 200:
                    print('200 : OK')
                    return
                elif message[RESPONSE] == 412:
                    self.logger.critical(f'{message[ERROR]}')
                    self.transport_shutdown()
                elif message[RESPONSE] == 401:
                    self.logger.critical(f'{message[ERROR]}')
                    self.wrong_password = True
                    self.transport_shutdown()
                elif message[RESPONSE] == 403:
                    self.logger.critical(f'{message[ERROR]}')
                    self.transport_shutdown()
                self.logger.critical(f'{message[ERROR]}')
                return

            elif ACTION in message and message[ACTION] == MESSAGE and SENDER in message and MESSAGE_TXT in message:
                print(f'\n{time.ctime()}  message from:  '
                      f'{message[SENDER]}\n'
                      f'{message[MESSAGE_TXT]}')
                self.new_message.emit(message)

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
                raise json.JSONDecodeError

        except json.JSONDecodeError:
            self.logger.error(f'received incorrect data')

    @Log()
    def create_message(self, to, text):
        """
        func creates message to server_
        @param to: username
        @param text: message text
        @return: dict
        """
        self.logger.debug('client_ creating a message')
        self.message_to_server = {
            ACTION: MESSAGE,
            TIME: time.time(),
            TO: to,
            SENDER: self.name,
            MESSAGE_TXT: text
        }
        self.logger.debug(f'client_ created a message {self.message_to_server}')
        return self.message_to_server

    @Log()
    def key_request(self, user):
        """
        fucn makes request of public key to encrypt message
        @param user: username
        @return: public key, str
        """
        self.logger.debug(f'request pub_key {user}')
        request = {
            ACTION: PUBLIC_KEY_REQUEST,
            TIME: time.time(),
            ACCOUNT_NAME: user
        }
        with sock_lock:
            send_msg(self.sock, request)
            ans = receive_msg(self.sock)
        if RESPONSE in ans and ans[RESPONSE] == 511:
            return ans[DATA]
        else:
            self.logger.error(f'cant to get pub_key {user}.')

    @Log()
    def add_contact(self, contact):
        """
        func send to server_ message to add new contact
        @param contact: username
        @return:
        """
        self.logger.debug(f'Creating new contact {contact}')
        request = {
            ACTION: ADD_CONTACT,
            TIME: time.time(),
            SENDER: self.name,
            ACCOUNT_NAME: contact
        }
        with sock_lock:
            send_msg(self.sock, request)
            self.message_from_server(receive_msg(self.sock))
        return

    @Log()
    def remove_contact(self, contact):
        """
        func send to server_ message to del contact
        @param contact: username
        @return:
        """
        self.logger.debug(f'Removing contact {contact}')
        request = {
            ACTION: REMOVE_CONTACT,
            TIME: time.time(),
            SENDER: self.name,
            ACCOUNT_NAME: contact
        }
        with sock_lock:
            send_msg(self.sock, request)
            self.message_from_server(receive_msg(self.sock))
        return

    @Log()
    def send_message(self, to, text):
        """
        send message to server_ function
        @param to: username
        @param text: message text
        @return:
        """
        message = self.create_message(to, text)
        with sock_lock:
            send_msg(self.sock, message)
            self.message_from_server(receive_msg(self.sock))
            self.logger.info(f'message sent to {to}')

    @Log()
    def transport_shutdown(self):
        """
        shutdown socket connection
        @return:
        """
        self.running = False
        message = {
            ACTION: EXIT,
            TIME: time.time(),
            SENDER: self.name
        }
        with sock_lock:
            try:
                send_msg(self.sock, message)
            except OSError:
                pass
        self.logger.debug('socket closing')
        time.sleep(0.5)

