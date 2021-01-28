import binascii
import hashlib
import os
import sys
import argparse
from Cryptodome.PublicKey import RSA
from PyQt5.QtWidgets import QApplication
from client import ClientMainWindow
from client import ClientDB
from client.login import LoginWindow
from client import Client
from additionals.settings import DEFAULT_PORT, DEFAULT_IP
from additionals.decos import Log
from client.login_fail import LoginWindowFail


@Log()
def arg_parser():
    """
    argument parser for client_.py
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', default=DEFAULT_IP, nargs='?', help='ip address')
    parser.add_argument('-p', default=DEFAULT_PORT, type=int, nargs='?', help=':port')
    parser.add_argument('-n', '--name', default=None, nargs='?', help='your nick name')
    parser.add_argument('-P', '--password', default=None, nargs='?', help='password')
    namespace = parser.parse_args(sys.argv[1:])
    addr = namespace.a
    port = namespace.p
    name = namespace.n
    password = namespace.P
    return addr, port, name, password


if __name__ == '__main__':
    ip, port, name, password = arg_parser()
    client_gui = QApplication(sys.argv)
    if not name:
        get_name = LoginWindow()
        client_gui.exec_()
        if get_name.set_name:
            name = get_name.ui.nick_line.text()
            password = get_name.ui.pass_line.text()
            if get_name.ui.to_register.isChecked() and get_name.set_pwd:
                to_register = True
            else:
                to_register = False
            del get_name
        else:
            exit(0)
    database = ClientDB(name)
    pass_bytes = password.encode('utf-8')
    salt = name[::-1].lower().encode('utf-8')
    password = hashlib.pbkdf2_hmac('sha256', pass_bytes, salt, 100000)
    password = binascii.hexlify(password)
    password = password.decode('utf-8')
    dir_path = os.path.dirname(os.path.realpath(__file__))
    key_file = os.path.join(dir_path, f'{name}.key')
    if not os.path.exists(key_file):
        keys = RSA.generate(2048, os.urandom)
        with open(key_file, 'wb') as key:
            key.write(keys.export_key())
    else:
        with open(key_file, 'rb') as key:
            keys = RSA.import_key(key.read())

    try:
        client_app = Client(ip, port, name, password, database, keys, to_register)

    except:
        get_name = LoginWindowFail()
        client_gui.exec_()
        exit(1)

    client_app.setDaemon(True)
    client_app.start()
    window = ClientMainWindow(database, client_app, keys)
    window.make_connection(client_app)
    window.setWindowTitle(f'Python chat alpha v.0.2.0 - {name.upper()}')
    client_gui.exec_()
    get_name = LoginWindowFail()
    client_gui.exec_()
    client_app.transport_shutdown()
    client_app.join()

