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
from Server_Meta import ServerVerifier
from additionals.server_descriptor import PortVerifier, HostVerifier
from additionals.settings import RESPONSE_200, RESPONSE_400, ACTION, ACCOUNT_NAME, TIME, PRESENCE, USER, MESSAGE, \
    MESSAGE_TXT, SENDER, ERROR, TO, \
    EXIT, ADD_CONTACT, REMOVE_CONTACT, RESPONSE_202, GET_CONTACTS, USERS_REQUEST, RESPONSE_203
from additionals.utils import send_msg, receive_msg
from decos import Log
from server_database import ServerDB
from server_gui import MainGui, gui_create_model, create_stat_model, ConfigWindow, HistoryWindow

new_connection = False
conflag_lock = threading.Lock()


@Log()
def arg_parser(default_address, default_port):
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', default=default_address, nargs='?', help='ip address')
    parser.add_argument('-p', default=default_port, type=int, nargs='?', help=':port')
    namespace = parser.parse_args(sys.argv[1:])
    addr = namespace.a
    port = namespace.p
    return addr, port


class Server(threading.Thread, metaclass=ServerVerifier):
    # __slots__ = ('logger', 'ip', 'ip_port', 'sock', 'messages_count', 'client', 'addr', 'message', 'response',
    #              'connected_clients', 'r_clients', 'w_clients', 'e_clients', 'messages_lst', 'names')

    port = PortVerifier()
    ip = HostVerifier()

    def __init__(self, ip_addr, ip_port, database):
        self.database = database
        self.logger = getLogger('app.server')
        self.ip = ip_addr
        self.port = ip_port
        self.connected_clients = deque()
        self.messages_lst = []
        self.r_clients = deque()
        self.w_clients = deque()
        self.e_clients = deque()
        self.message = {}
        self.names = {}
        super().__init__()

    def init_socket(self):
        self.logger.warning(f'server starts with {self.ip}:{self.port}')
        self.sock = socket(AF_INET, SOCK_STREAM)
        self.logger.debug(f'server successfully started socket {self.sock}')
        self.sock.bind((self.ip, self.port))
        self.sock.settimeout(0.5)
        self.logger.debug('server successfully got socket')
        self.sock.listen()
        self.logger.debug('server started to listen socket')

    def run(self):
        self.init_socket()

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
                # print(f'connected {self.connected_clients}')
                # print(f'r_clients {self.r_clients}')
                # print(f'w_clients {self.w_clients}')
            except OSError:
                pass

            if self.r_clients:
                self.parse_r_clients()

            if self.messages_lst and self.w_clients:
                self.parse_w_clients()

    @Log()
    def message_handler(self, message, client):
        global new_connection
        if ACTION in message and message[ACTION] == PRESENCE and TIME in message \
                and USER in message:
            if not message[USER][ACCOUNT_NAME] in self.names.keys():
                self.names[message[USER][ACCOUNT_NAME]] = client
                client_ip, client_port = client.getpeername()
                self.database.user_login(message[USER][ACCOUNT_NAME], client_ip, client_port)
                self.send(client, RESPONSE_200)
                with conflag_lock:
                    new_connection = True
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
            self.database.get_message(message[SENDER], message[TO], message[MESSAGE_TXT])
            self.database.messages_count(message[SENDER], message[TO])
            return

        elif ACTION in message and message[ACTION] == EXIT and TIME in message \
                and SENDER in message:
            self.database.user_logout(message[SENDER])
            self.connected_clients.remove(client)
            self.names.pop(message[SENDER])
            self.r_clients.remove(client)
            self.w_clients.remove(client)
            client.close()
            return

        elif ACTION in message and message[ACTION] == GET_CONTACTS and SENDER in message and \
                self.names[message[SENDER]] == client:
            self.response = RESPONSE_203
            self.response[GET_CONTACTS] = self.database.get_contact(message[SENDER])
            self.send(client, self.response)
            return

        elif ACTION in message and message[ACTION] == ADD_CONTACT and ACCOUNT_NAME in message and SENDER in message \
                and self.names[message[SENDER]] == client:
            self.database.add_contact(message[SENDER], message[ACCOUNT_NAME])
            self.send(client, RESPONSE_200)
            return

        elif ACTION in message and message[ACTION] == REMOVE_CONTACT and ACCOUNT_NAME in message and SENDER in message \
                and self.names[message[SENDER]] == client:
            self.database.remove_contact(message[SENDER], message[ACCOUNT_NAME])
            self.send(client, RESPONSE_200)
            return

        elif ACTION in message and message[ACTION] == USERS_REQUEST and SENDER in message and \
                self.names[message[SENDER]] == client:
            self.response = RESPONSE_202
            self.response[USERS_REQUEST] = [user[0] for user in self.database.users_list()]
            self.send(client, self.response)
            return

        self.logger.error(f'created answer to client - {RESPONSE_400}')
        self.send(client, RESPONSE_400)
        return

    @Log()
    def parse_r_clients(self):  # TODO
        for client_to_receive in self.r_clients:
            try:
                self.message_handler(receive_msg(client_to_receive), client_to_receive)

            except Exception as e:
                print(e)
                self.get_name(client_to_receive)

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

    def help(self):
        _help = (
            """
        commands:
        - users           -show all user in db
        - connected       -show connected users at the moment
        - history         -show login history
            - name (optional)
        - messages        -show messages
            - name (optional)  
        """
        )
        return _help

    def command_mode(self):
        try:
            while True:
                command = input('type your command: ')
                if command == 'help':
                    print(self.help())
                elif command == 'users':
                    for user in sorted(self.database.users_list()):
                        print(f'user <{user[0]}>, last seen {user[1]}')
                elif command == 'connected':
                    for user in sorted(self.database.active_users_list()):
                        print(f'user <{user[0]}>, from {user[1]}:{user[2]}, connected at {user[3]}')
                elif command == 'history':
                    username = input('type username or push enter to show all history: ')
                    for user in sorted(self.database.login_history(username)):
                        print(f'user <{user[0]}>, from {user[1]}:{user[2]} was there {user[3]}')
                elif command == 'messages':
                    username = input('type username or push enter to show all messages: ')
                    for user in sorted(self.database.messages_list(username)):
                        print(f'user <{user[0]}>, sent message at {user[3]} to <{user[1]}> with text:\n'
                              f'{user[2]}')
                else:
                    print('unknown command')
        except KeyboardInterrupt:
            self.logger.warning(f'server stopped by user')
            self.sock.close()

    def get_name(self, client):
        self.connected_clients.remove(client)
        self.r_clients.remove(client)
        self.w_clients.remove(client)
        for i in self.names.items():
            if i[1] == client:
                self.names.pop(i[0])
                self.database.user_logout(i[0])
                return

    def __str__(self):
        return {'Server.app'}


def main():
    server_config = configparser.ConfigParser()
    path = os.path.dirname(os.path.realpath(__file__))
    server_config.read(os.path.join(path, 'server.ini'))
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
        global new_connection
        if conflag_lock:
            main_window.active_users_table.setModel(
                gui_create_model(database))
            main_window.active_users_table.resizeColumnsToContents()
            main_window.active_users_table.resizeRowsToContents()
            with conflag_lock:
                new_connection = False

    def show_statistics():
        global stat_window
        stat_window = HistoryWindow()
        stat_window.history_table.setModel(create_stat_model(database))
        stat_window.history_table.resizeColumnsToContents()
        stat_window.history_table.resizeRowsToContents()
        stat_window.show()

    def server_configuration():
        global config_window
        config_window = ConfigWindow()
        config_window.db_path.insert(server_config['SETTINGS']['db_path'])
        config_window.db_file.insert(server_config['SETTINGS']['db_file_name'])
        config_window.port.insert(server_config['SETTINGS']['DEFAULT_PORT'])
        config_window.ip.insert(server_config['SETTINGS']['DEFAULT_IP'])
        config_window.save_btn.clicked.connect(save_server_config)

    def save_server_config():
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
                with open('server.ini', 'w') as conf:
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
