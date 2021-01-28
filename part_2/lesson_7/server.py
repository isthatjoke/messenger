import argparse
import configparser
import os
import select
import sys
import threading
import time
from collections import deque
from logging import getLogger
from socket import socket, AF_INET, SOCK_STREAM
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication, QMessageBox
from additionals.server_meta import ServerVerifier
from additionals.server_descriptor import PortVerifier, HostVerifier
from additionals.settings import RESPONSE_200, RESPONSE_400, ACTION, ACCOUNT_NAME, TIME, PRESENCE, USER, MESSAGE, \
    MESSAGE_TXT, SENDER, ERROR, TO, \
    EXIT, ADD_CONTACT, REMOVE_CONTACT, RESPONSE_202, GET_CONTACTS, USERS_REQUEST, RESPONSE_203, PASSWORD, REGISTER,\
    RESPONSE_412, PUB_KEY, PUBLIC_KEY_REQUEST, RESPONSE_511, DATA, RESPONSE_401, RESPONSE_403
from additionals.utils import send_msg, receive_msg
from additionals.decos import Log
from server.server_database import ServerDB
from server.server_gui import MainGui, gui_create_model, create_stat_model, ConfigWindow, HistoryWindow

new_connection = False
conflag_lock = threading.Lock()


@Log()
def arg_parser(default_address, default_port):
    """
    argument parser for server_.py
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', default=default_address, nargs='?', help='ip address')
    parser.add_argument('-p', default=default_port, type=int, nargs='?', help=':port')
    namespace = parser.parse_args(sys.argv[1:])
    addr = namespace.a
    port = namespace.p
    return addr, port


class Server(threading.Thread, metaclass=ServerVerifier):
    """
    Server Main Class
    """
    port = PortVerifier()
    ip = HostVerifier()

    def __init__(self, ip_addr, ip_port, database):
        """
        server_ initialization
        @param ip_addr: ip address
        @param ip_port: ip port
        @param database: connected database
        """
        self.database = database
        self.logger = getLogger('app.server_')
        self.ip = ip_addr
        self.port = ip_port
        self.connected_clients = deque()
        self.messages_lst = []
        self.r_clients = deque()
        self.w_clients = deque()
        self.e_clients = deque()
        self.names = {}
        self.authentication_lst = {}
        super().__init__()

    @Log()
    def init_socket(self):
        """
        create socket connection
        """
        self.logger.warning(f'server_ starts with {self.ip}:{self.port}')
        self.sock = socket(AF_INET, SOCK_STREAM)
        self.logger.debug(f'server_ successfully started socket {self.sock}')
        self.sock.bind((self.ip, self.port))
        self.sock.settimeout(0.5)
        self.logger.debug('server_ successfully got socket')
        self.sock.listen()
        self.logger.debug('server_ started to listen socket')

    def run(self):
        global new_connection
        self.init_socket()

        while True:
            try:
                self.client, self.addr = self.sock.accept()
                self.authentication_lst[self.client] = round(time.time())
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
                for client_to_receive in self.r_clients:
                    try:
                        self.message_handler(receive_msg(client_to_receive), client_to_receive)
                    except Exception as e:
                        print(e)
                        self.get_name(client_to_receive)
                        with conflag_lock:
                            new_connection = True

            for message in self.messages_lst:
                try:
                    self.process_message(message, self.w_clients)
                except (ConnectionAbortedError, ConnectionError, ConnectionResetError, ConnectionRefusedError):
                    self.logger.info(f'Connection with {message[TO]} has been lost')
                    self.connected_clients.remove(self.names[message[TO]])
                    self.database.user_logout(message[TO])
                    del self.names[message[TO]]
                    with conflag_lock:
                        new_connection = True
            self.messages_lst.clear()

    @Log()
    def authenticate_request(self, name, pwd):
        """
        check entered users password
        @param name: username
        @param pwd: password
        @return: bool
        """
        query_pwd = self.database.check_pwd(name)
        if pwd == query_pwd[0]:
            return True
        return False

    @Log()
    def process_message(self, message, listen_socks):
        """
        send messages func
        @param message: dict
        @param listen_socks: connected sockets
        @return:
        """
        if message[TO] in self.names and self.names[message[TO]] in listen_socks:
            send_msg(self.names[message[TO]], message)
            self.logger.info(f'Message to {message[TO]} has been sent from {message[SENDER]}.')
        elif message[TO] in self.names and self.names[message[TO]] not in listen_socks:
            raise ConnectionError
        else:
            self.logger.error(
                f'User {message[TO]} is not registered on server_, send message failed.')

    @Log()
    def message_handler(self, message, client):
        """
        incoming messages handler
        @param message: dict
        @param client: username
        @return:
        """
        global new_connection
        print(message)
        if ACTION in message and message[ACTION] == REGISTER and TIME in message \
                and USER in message and client in self.authentication_lst:
            if not message[USER][ACCOUNT_NAME] in self.names.keys()\
                    and not self.database.check_user(message[USER][ACCOUNT_NAME]):
                self.names[message[USER][ACCOUNT_NAME]] = client
                del self.authentication_lst[client]
                client_ip, client_port = client.getpeername()
                self.database.user_login(message[USER][ACCOUNT_NAME], client_ip, client_port,
                                         message[USER][PASSWORD], message[USER][PUB_KEY])
                self.send(client, RESPONSE_200)
                with conflag_lock:
                    new_connection = True
                return
            else:
                response = RESPONSE_412
                response[ERROR] = f'client_ with name "{message[USER][ACCOUNT_NAME]}" is registered already'
                self.send(client, response)
                self.connected_clients.remove(client)
                del self.authentication_lst[client]
                client.close()
                return

        elif ACTION in message and message[ACTION] == PRESENCE and TIME in message \
                and USER in message and client in self.authentication_lst and \
                self.authenticate_request(message[USER][ACCOUNT_NAME], message[USER][PASSWORD]) and \
                self.database.check_user(message[USER][ACCOUNT_NAME]):
            if not message[USER][ACCOUNT_NAME] in self.names.keys():
                self.names[message[USER][ACCOUNT_NAME]] = client
                del self.authentication_lst[client]
                client_ip, client_port = client.getpeername()
                self.database.user_login(message[USER][ACCOUNT_NAME], client_ip, client_port,
                                         message[USER][PASSWORD], message[USER][PUB_KEY])
                self.send(client, RESPONSE_200)
                with conflag_lock:
                    new_connection = True
                return
            else:
                response = RESPONSE_401
                response[ERROR] = f'client_ with name "{message[USER][ACCOUNT_NAME]}" is in chat already'
                self.send(client, response)
                self.connected_clients.remove(client)
                del self.authentication_lst[client]
                client.close()
                return

        elif ACTION in message and message[ACTION] == PRESENCE and TIME in message \
                and USER in message and client in self.authentication_lst and not\
                self.database.check_user(message[USER][ACCOUNT_NAME]):
            response = RESPONSE_403
            response[ERROR] = f'client_ with name "{message[USER][ACCOUNT_NAME]}" is not registered'
            self.send(client, response)
            self.connected_clients.remove(client)
            del self.authentication_lst[client]
            client.close()
            return

        elif ACTION in message and message[ACTION] == PRESENCE and TIME in message \
                and USER in message and client in self.authentication_lst and \
                self.database.check_user(message[USER][ACCOUNT_NAME]) and not \
                self.authenticate_request(message[USER][ACCOUNT_NAME], message[USER][PASSWORD]):
            response = RESPONSE_401
            response[ERROR] = f'wrong password'
            self.send(client, response)
            self.connected_clients.remove(client)
            del self.authentication_lst[client]
            client.close()
            return

        elif ACTION in message and message[ACTION] == MESSAGE and TIME in message \
                and MESSAGE_TXT in message and SENDER in message and TO in message \
                and message[SENDER] not in self.authentication_lst:
            if message[TO] in self.names:
                self.messages_lst.append(message)
                self.database.messages_count(message[SENDER], message[TO])
                self.send(client, RESPONSE_200)
            else:
                response = RESPONSE_400
                response[ERROR] = 'client_ is not authorized'
                self.send(client, response)
            return

        elif ACTION in message and message[ACTION] == EXIT and TIME in message \
                and SENDER in message and self.names[message[SENDER]] == client \
                and message[SENDER] not in self.authentication_lst:
            self.database.user_logout(message[SENDER])
            self.connected_clients.remove(client)
            self.names.pop(message[SENDER])
            self.r_clients.remove(client)
            self.w_clients.remove(client)
            client.close()
            with conflag_lock:
                new_connection = True
            return

        elif ACTION in message and message[ACTION] == GET_CONTACTS and SENDER in message and \
                self.names[message[SENDER]] == client and message[SENDER] not in self.authentication_lst:
            self.response = RESPONSE_203
            self.response[GET_CONTACTS] = self.database.get_contact(message[SENDER])
            self.send(client, self.response)
            return

        elif ACTION in message and message[ACTION] == ADD_CONTACT and ACCOUNT_NAME in message and SENDER in message \
                and self.names[message[SENDER]] == client and message[SENDER] not in self.authentication_lst:
            self.database.add_contact(message[SENDER], message[ACCOUNT_NAME])
            self.send(client, RESPONSE_200)
            return

        elif ACTION in message and message[ACTION] == REMOVE_CONTACT and ACCOUNT_NAME in message and SENDER in message \
                and self.names[message[SENDER]] == client and message[SENDER] not in self.authentication_lst:
            self.database.delete_contact(message[SENDER], message[ACCOUNT_NAME])
            self.send(client, RESPONSE_200)
            return

        elif ACTION in message and message[ACTION] == USERS_REQUEST and SENDER in message and \
                self.names[message[SENDER]] == client and message[SENDER] not in self.authentication_lst:
            self.response = RESPONSE_202
            self.response[USERS_REQUEST] = [user[0] for user in self.database.users_list()]
            self.send(client, self.response)
            return

        elif ACTION in message and message[ACTION] == PUBLIC_KEY_REQUEST and ACCOUNT_NAME in message:
            response = RESPONSE_511
            response[DATA] = self.database.get_keys(message[ACCOUNT_NAME])
            if response[DATA]:
                try:
                    send_msg(client, response)
                except OSError:
                    self.get_name(client)
            else:
                response = RESPONSE_400
                response[ERROR] = 'Нет публичного ключа для данного пользователя'
                try:
                    send_msg(client, response)
                except OSError:
                    self.get_name(client)

        else:
            self.logger.error(f'created answer to client_ - {RESPONSE_400}')
            self.send(client, RESPONSE_400)
            return

    @Log()
    def send(self, *args):
        """
        send message function
        @param args: socket, message
        @return:
        """
        send_msg(*args)

    @Log()
    def get_name(self, client):
        """
        handler to detect and delete disconnected users
        @param client: username
        @return:
        """
        try:
            if client in self.connected_clients:
                self.connected_clients.remove(client)
            elif client in self.r_clients:
                self.r_clients.remove(client)
            elif client in self.w_clients:
                self.w_clients.remove(client)
            for i in self.names.items():
                if i[1] == client:
                    self.names.pop(i[0])
                    self.database.user_logout(i[0])
        except Exception as e:
            self.logger.warning(f'get_name exception {e}')


def main():
    """
    main function, create server_ GUI, get server_ settings
    @return:
    """
    server_config = configparser.ConfigParser()
    path = os.path.dirname(os.path.realpath(__file__))
    server_config.read(os.path.join(path, 'server/server.ini'))
    ip_addr, ip_port = arg_parser(server_config['SETTINGS']['DEFAULT_IP'], server_config['SETTINGS']['DEFAULT_PORT'])
    database = ServerDB(os.path.join(server_config['SETTINGS']['db_path'], server_config['SETTINGS']['db_file_name']))

    app = Server(ip_addr, ip_port, database)
    app.daemon = True
    app.start()
    gui_app = QApplication(sys.argv)
    main_window = MainGui()
    main_window.statusBar().showMessage('Server Working')
    main_window.active_users_table.setModel(gui_create_model(database))
    main_window.active_users_table.resizeColumnsToContents()
    main_window.active_users_table.resizeRowsToContents()

    def list_update():
        """
        func shows active users in GUI
        @return:
        """
        global new_connection
        if conflag_lock:
            main_window.active_users_table.setModel(
                gui_create_model(database))
            main_window.active_users_table.resizeColumnsToContents()
            main_window.active_users_table.resizeRowsToContents()
            with conflag_lock:
                new_connection = False

    def show_statistics():
        """
        func shows messages history in GUI
        @return:
        """
        global stat_window
        stat_window = HistoryWindow()
        stat_window.history_table.setModel(create_stat_model(database))
        stat_window.history_table.resizeColumnsToContents()
        stat_window.history_table.resizeRowsToContents()
        stat_window.show()

    def server_configuration():
        """
        func shows settings window in GUI
        @return:
        """
        global config_window
        config_window = ConfigWindow()
        config_window.db_path.insert(server_config['SETTINGS']['db_path'])
        config_window.db_file.insert(server_config['SETTINGS']['db_file_name'])
        config_window.port.insert(server_config['SETTINGS']['DEFAULT_PORT'])
        config_window.ip.insert(server_config['SETTINGS']['DEFAULT_IP'])
        config_window.save_btn.clicked.connect(save_server_config)

    def save_server_config():
        """
        check setting and save it in INI file
        @return:
        """
        global config_window
        message = QMessageBox()
        server_config['SETTINGS']['db_path'] = config_window.db_path.text()
        server_config['SETTINGS']['db_file_name'] = config_window.db_file.text()
        try:
            port = int(config_window.port.text())
        except ValueError:
            message.warning(config_window, 'Error', 'Port should be an integer')
        else:
            server_config['SETTINGS']['DEFAULT_IP'] = config_window.ip.text()
            if 1023 < port < 65536:
                server_config['SETTINGS']['DEFAULT_PORT'] = str(port)
                print(port)
                with open('server/server.ini', 'w') as conf:
                    server_config.write(conf)
                    message.information(
                        config_window, 'OK', 'Settings saved')
            else:
                message.warning(
                    config_window,
                    'Error',
                    'Port should be 1024 - 65536')

    timer = QTimer()
    timer.timeout.connect(list_update)
    timer.start(1000)

    main_window.refresh.triggered.connect(list_update)
    main_window.history.triggered.connect(show_statistics)
    main_window.server_config.triggered.connect(server_configuration)

    gui_app.exec_()


if __name__ == '__main__':
    main()
