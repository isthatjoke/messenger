import argparse
import dis
import json
import sys
import time
from logging import getLogger
from socket import socket, AF_INET, SOCK_STREAM
import threading
from additionals.client_descriptor import PortVerifier, HostVerifier
from additionals.errors import IncorrectData
from additionals.settings import DEFAULT_PORT, DEFAULT_IP, ACTION, PRESENCE, TIME, USER, ACCOUNT_NAME, \
    RESPONSE, ERROR, MESSAGE, MESSAGE_TXT, SENDER, TO, EXIT, RESPONSE_OK, ADD_CONTACT, USERS_REQUEST, GET_CONTACTS, \
    CONTACTS
from additionals.utils import send_msg, receive_msg
from decos import Log
from client_database import ClientDB

# sock_lock = threading.Lock()
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


class Client(threading.Thread, metaclass=ClientVerifier):
    # __slots__ = ('parser', 'namespace', 'connection_addr', 'connection_port', 'mode', 'logger', 'name', 'message',
    #              'message_to_server', 'presence', 'sock', 'response', 'daemon', 'send_thread', 'listen_thread',
    #              'buddy_name', 'command')

    def __init__(self, addr, port, name, database, sock):
        super().__init__()
        self.daemon = True
        self.connection_addr = addr
        self.connection_port = port
        self.username = name
        self.logger = getLogger('app.client')
        self.message_to_server = {}
        self.database = database
        self.sock = sock


    def start(self):
        self.logger.debug(f'client successfully connected to {self.connection_addr}:{self.connection_port}')
        send_msg(self.sock, self.client_presence())
        self.logger.debug(f'client sent message to {self.sock} with {self.client_presence()}')
        try:

            self.send_thread = threading.Thread(target=self.send_mode)
            self.listen_thread = threading.Thread(target=self.listen_mode)

            for thread_ in [self.send_thread, self.listen_thread]:
                thread_.start()
            self.listen_thread.join()


        except ConnectionRefusedError:
            self.logger.critical(f'error - connection refused')
            sys.exit(1)

        except KeyboardInterrupt:
            print('client exited')
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
            print(f'connected to chat with nick - {self.username}')
        while True:
            time.sleep(1)
            if self.send_thread.is_alive() and self.listen_thread.is_alive():
                continue
            break

    # def users_list_request(self):  # TODO
    #     self.logger.debug(f'Запрос списка известных пользователей {self.username}')
    #     self.request = {
    #         ACTION: USERS_REQUEST,
    #         TIME: time.time(),
    #         USER: self.username
    #     }
    #     send_msg(self.sock, self.request)
    #     return

    # def get_info(self):
    #     self.users_list_request()
    #     self.contacts_list_request()

    # def contacts_list_request(self):
    #     self.logger.debug(f'Запрос контакт листа для пользователся {self.username}')
    #     self.request = {
    #         ACTION: GET_CONTACTS,
    #         TIME: time.time(),
    #         USER: self.username
    #     }
    #     self.logger.debug(f'Сформирован запрос {self.request}')
    #     send_msg(self.sock, self.request)
    #     return

    @Log()
    def client_presence(self):
        self.presence = {
            ACTION: PRESENCE,
            TIME: time.time(),
            USER: {
                ACCOUNT_NAME: self.username
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

        self.message_to_server = {
            ACTION: MESSAGE,
            TIME: time.time(),
            TO: self.buddy_name,
            SENDER: self.username,
            MESSAGE_TXT: self.message
        }

        return self.message_to_server

    @Log()
    def exit_message(self):

        self.message_to_server = {
            ACTION: EXIT,
            TIME: time.time(),
            SENDER: self.username,
        }

        return self.message_to_server

    def get_history(self):
        ask = input('Показать входящие сообщения - in, исходящие - out, все - просто Enter: ')
        with database_lock:
            if ask == 'in':
                history_list = self.database.get_history(to_=self.username)
                for message in history_list:
                    print(f'\nСообщение от пользователя: {message[0]} от {message[3]}:\n{message[2]}')
            elif ask == 'out':
                history_list = self.database.get_history(from_=self.username)
                for message in history_list:
                    print(f'\nСообщение пользователю: {message[1]} от {message[3]}:\n{message[2]}')
            else:
                history_list = self.database.get_history()
                for message in history_list:
                    print(
                        f'\nСообщение от пользователя: {message[0]}, пользователю {message[1]} от {message[3]}\n{message[2]}')

    def edit_contacts(self):
        ans = input('Для удаления введите del, для добавления add: ')
        if ans == 'del':
            edit = input('Введите имя удаляемного контакта: ')
            with database_lock:
                if self.database.check_contact(edit):
                    self.database.del_contact(edit)
                else:
                    self.logger.error('Попытка удаления несуществующего контакта.')
                # with sock_lock:
                try:
                    return self.remove_contact(edit)
                except:  # ServerError:
                    self.logger.error('Не удалось отправить информацию на сервер.')
        elif ans == 'add':
            # Проверка на возможность такого контакта
            edit = input('Введите имя создаваемого контакта: ')
            if self.database.check_user(edit):
                with database_lock:
                    self.database.add_contact(edit)
                # with sock_lock:
                try:
                    return self.add_contact(edit)
                except:  # ServerError:
                    self.logger.error('Не удалось отправить информацию на сервер.')

    def add_contact(self, contact):
        self.logger.debug(f'Создание контакта {contact}')
        self.request = {
            ACTION: ADD_CONTACT,
            TIME: time.time(),
            USER: self.username,
            ACCOUNT_NAME: contact
        }
        return self.request

    def remove_contact(self, contact):
        self.logger.debug(f'Создание контакта {contact}')
        self.request = {
            ACTION: ADD_CONTACT,
            TIME: time.time(),
            USER: self.username,
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
                        f'Попытка отправить сообщение незарегистрированому получателю: {self.buddy_name}')  # TODO
                    return
            self.message = input('type your message here: ')
            with database_lock:
                self.database.save_new_message(self.username, self.buddy_name, self.message)
            return self.create_message()

        elif self.command == 'contacts':  # TODO
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
                sys.exit(1)
            finally:
                sys.exit(1)
        else:
            print('incorrect command')

    @Log()
    def send_mode(self):
        print(f'connected to chat with nick - {self.username}')

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


def contacts_list_request(sock, name):
    req = {
        ACTION: GET_CONTACTS,
        TIME: time.time(),
        USER: name
    }

    send_msg(sock, req)
    ans = receive_msg(sock)

    if RESPONSE in ans and ans[RESPONSE] == 203:
        return ans[GET_CONTACTS]


def user_list_request(sock, username):
    req = {
        ACTION: USERS_REQUEST,
        TIME: time.time(),
        USER: username
    }
    send_msg(sock, req)
    ans = receive_msg(sock)
    if RESPONSE in ans and ans[RESPONSE] == 202:
        return ans[USERS_REQUEST]


def database_load(sock, database, username):
    # Загружаем список известных пользователей
    try:
        users_list = user_list_request(sock, username)
    except:
        print('shit')
    else:
        database.add_users(users_list)

    # Загружаем список контактов
    try:
        contacts_list = contacts_list_request(sock, username)
    except:
        print('shit')
    else:
        for contact in contacts_list:
            database.add_contact(contact)


def main():
    addr, port, name = arg_parser()
    sock = socket(AF_INET, SOCK_STREAM)
    # self.logger.warning(f'client successfully started socket {self.sock}')
    sock.connect((addr, port))
    database = ClientDB(name)
    database_load(sock, database, name)
    app = Client(addr, port, name, database, sock)
    app.start()


if __name__ == '__main__':
    main()
