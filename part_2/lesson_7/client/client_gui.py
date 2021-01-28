import base64
import json
import logging
from Cryptodome.PublicKey import RSA
from Cryptodome.Cipher import PKCS1_OAEP
from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QBrush, QColor
from PyQt5.QtWidgets import QMainWindow, qApp, QMessageBox, QApplication
from .client_window import Ui_MainClientWindow
from .add_contact import AddContactDialog
from .del_contact import DelContactDialog
from additionals.settings import MESSAGE_TXT, SENDER


class ClientMainWindow(QMainWindow):
    """
    main window GUI
    """
    def __init__(self, database, sock, keys):
        super().__init__()
        self.logger = logging.getLogger('app.client_')
        self.database = database
        self.sock = sock
        self.ui = Ui_MainClientWindow()
        self.ui.setupUi(self)
        self.ui.menu_exit.triggered.connect(qApp.exit)
        self.ui.btn_send.clicked.connect(self.send_message)
        self.ui.btn_add_contact.clicked.connect(self.add_contact_window)
        self.ui.btn_remove_contact.clicked.connect(self.delete_contact_window)
        self.ui.btn_start.clicked.connect(self.select_active_user)
        self.ui.btn_refresh.clicked.connect(self.users_list_update)
        self.contacts_model = None
        self.history_model = None
        self.messages = QMessageBox()
        self.current_chat = None
        self.keys = keys
        self.decrypter = PKCS1_OAEP.new(self.keys)
        self.current_chat_key = None
        self.encryptor = None
        self.ui.list_messages.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.ui.list_messages.setWordWrap(True)
        # self.ui.list_contacts.doubleClicked.connect(self.select_active_user)
        self.clients_list_update()
        self.users_list_update()
        self.set_disabled_input()
        self.show()

    def set_disabled_input(self):
        """
        disable send button if contact is not chosen
        :return:
        """
        self.ui.text_message.clear()
        if self.history_model:
            self.history_model.clear()
        self.ui.btn_send.setDisabled(True)
        self.ui.text_message.setDisabled(True)
        self.encryptor = None
        self.current_chat = None
        self.current_chat_key = None

    def history_list_update(self):
        """
        messages history update
        :return:
        """
        list = sorted(self.database.get_history(self.current_chat), key=lambda item: item[3])
        if not self.history_model:
            self.history_model = QStandardItemModel()
            self.ui.list_messages.setModel(self.history_model)
        self.history_model.clear()
        length = len(list)
        start_index = 0
        if length > 20:
            start_index = length - 20

        for i in range(start_index, length):
            item = list[i]
            if item[1] == 'in':
                mess = QStandardItem(f'Incoming {item[3].replace(microsecond=0)}:\n {item[2]}')
                mess.setEditable(False)
                mess.setBackground(QBrush(QColor(255, 213, 213)))
                mess.setTextAlignment(Qt.AlignLeft)
                self.history_model.appendRow(mess)
            else:
                mess = QStandardItem(f'Outgoing {item[3].replace(microsecond=0)}:\n {item[2]}')
                mess.setEditable(False)
                mess.setTextAlignment(Qt.AlignRight)
                mess.setBackground(QBrush(QColor(204, 255, 204)))
                self.history_model.appendRow(mess)
        self.ui.list_messages.scrollToBottom()

    def select_active_user(self):
        """
        select active user by click
        :return:
        """
        self.current_chat = self.ui.list_contacts.currentIndex().data()
        if self.current_chat:
            self.set_active_user()
        else:
            self.current_chat = self.ui.list_users.currentIndex().data()
            self.set_active_user()

    def set_active_user(self):
        """
        set active user, get public key to encrypt
        :return:
        """
        try:
            self.current_chat_key = self.sock.key_request(
                self.current_chat)
            self.logger.debug(f'got pub_key {self.current_chat}')
            if self.current_chat_key:
                self.encryptor = PKCS1_OAEP.new(RSA.import_key(self.current_chat_key))
        except (OSError, json.JSONDecodeError):
            self.current_chat_key = None
            self.encryptor = None
            self.logger.debug(f'cant to get pub_key {self.current_chat}')

        if not self.current_chat_key:
            self.messages.warning(
                self, 'Error', f'theres no encryption key for {self.current_chat}')
            return
        self.ui.btn_send.setDisabled(False)
        self.ui.text_message.setDisabled(False)
        self.history_list_update()

    def clients_list_update(self):
        """
        update contacts list
        :return:
        """
        contacts_list = self.database.get_contacts()
        self.contacts_model = QStandardItemModel()
        for i in sorted(contacts_list):
            item = QStandardItem(i)
            item.setEditable(False)
            self.contacts_model.appendRow(item)
        self.ui.list_contacts.setModel(self.contacts_model)

    def users_list_update(self):
        """
        update users list
        :return:
        """
        users_list = self.sock.users_list_request()
        self.users_model = QStandardItemModel()
        for i in sorted(users_list):
            item = QStandardItem(i)
            item.setEditable(False)
            self.users_model.appendRow(item)
        self.ui.list_users.setModel(self.users_model)

    def add_contact_window(self):
        """
        add new contact window
        :return:
        """
        global select_dialog
        global contact
        contact = self.ui.list_users.currentIndex().data()
        select_dialog = AddContactDialog(self.sock, self.database, contact)
        select_dialog.btn_ok.clicked.connect(lambda: self.add_contact_action(select_dialog))
        select_dialog.show()

    def add_contact_action(self, item):
        self.add_contact(contact)
        item.close()

    def add_contact(self, new_contact):
        """
        add new contact and save in database
        :param new_contact:
        :return:
        """
        try:
            self.sock.add_contact(new_contact)
        except OSError as err:
            if err.errno:
                self.messages.critical(self, 'Error', 'Connection lost')
                self.close()
            self.messages.critical(self, 'Error', 'Connection timeout')
        else:
            self.database.add_contact(new_contact)
            new_contact = QStandardItem(new_contact)
            new_contact.setEditable(False)
            self.contacts_model.appendRow(new_contact)
            self.logger.info(f'Contact added {new_contact}')
            self.messages.information(self, 'Great', 'Contact added')

    def delete_contact_window(self):
        """
        delete contact window
        :return:
        """
        global remove_dialog
        global contact_to_remove
        contact_to_remove = self.ui.list_contacts.currentIndex().data()
        remove_dialog = DelContactDialog(self.database, contact_to_remove)
        remove_dialog.btn_ok.clicked.connect(lambda: self.delete_contact(remove_dialog))
        remove_dialog.show()

    def delete_contact(self, item):
        """
        delete contact and save in database
        :param item:
        :return:
        """
        global contact_to_remove
        try:
            self.sock.remove_contact(contact_to_remove)
            print(contact_to_remove)
        except OSError as err:
            if err.errno:
                self.messages.critical(self, 'Error', 'Connection lost')
                self.close()
            self.messages.critical(self, 'Error', 'Connection timeout')
        else:
            self.database.del_contact(contact_to_remove)
            self.clients_list_update()
            self.logger.info(f'Contact deleted {contact_to_remove}')
            self.messages.information(self, 'Great', 'Contact deleted')
            item.close()
            if contact_to_remove == self.current_chat:
                self.current_chat = None
                self.set_disabled_input()

    def send_message(self):
        """
        send message function with encryption
        :return:
        """
        message_text = self.ui.text_message.toPlainText()
        self.ui.text_message.clear()
        if not message_text:
            return
        message_text_encrypted = self.encryptor.encrypt(message_text.encode('utf8'))
        message_text_encrypted_base64 = base64.b64encode(message_text_encrypted)
        try:
            self.sock.send_message(self.current_chat, message_text_encrypted_base64.decode('ascii'))
            pass
        except OSError as err:
            print(err, 'send message error')
            if err.errno:
                self.messages.critical(self, 'Error', 'Connection lost')
                self.close()
            self.messages.critical(self, 'Error', 'Connection timeout')
        except (ConnectionResetError, ConnectionAbortedError) as err:
            print(err, 'Connection lost')
            self.messages.critical(self, 'Error', 'Connection lost')
            self.close()
        else:
            self.database.save_new_message(self.current_chat, 'out', message_text)
            self.logger.debug(f'message sent {self.current_chat}: {message_text}')
            self.history_list_update()

    @pyqtSlot(dict)
    def message(self, message):
        """
        message receive and decrypt function. also open new chat with contact if it's closed
        :param message:
        :return:
        """
        encrypted_message = base64.b64decode(message[MESSAGE_TXT])

        try:
            decrypted_message = self.decrypter.decrypt(encrypted_message)
        except (ValueError, TypeError):
            self.messages.warning(
                self, 'Ошибка', 'Не удалось декодировать сообщение.')
            return

        self.database.save_new_message(
            self.current_chat,
            'in',
            decrypted_message.decode('utf8'))

        sender = message[SENDER]
        if sender == self.current_chat:
            self.history_list_update()
        else:

            if self.database.check_contact(sender):

                if self.messages.question(self, 'New message',
                                          f'New message from {sender} has been received, would you like to chat?',
                                          QMessageBox.Yes, QMessageBox.No) == QMessageBox.Yes:
                    self.current_chat = sender
                    self.set_active_user()
            else:
                print('NO')

                if self.messages.question(self, 'New message', f'New message from {sender} has been received.\n '
                                                               f'Contact is not in your contact list.\n '
                                                               f'Want to add contact and start chat?',
                                          QMessageBox.Yes,
                                          QMessageBox.No) == QMessageBox.Yes:
                    self.add_contact(sender)
                    self.current_chat = sender
                    self.database.save_new_message(self.current_chat, 'in', decrypted_message.decode('utf8'))
                    self.set_active_user()

    @pyqtSlot()
    def connection_lost(self):
        """
        allert about lost connection
        :return:
        """
        self.messages.warning(self, 'Connection failed', 'Connection lost. ')
        self.close()

    def make_connection(self, trans_obj):
        """
        signal connect function
        :param trans_obj:
        :return:
        """
        trans_obj.new_message.connect(self.message)
        trans_obj.connection_lost.connect(self.connection_lost)


if __name__ == '__main__':
    pass


