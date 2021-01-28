import sys
import logging

sys.path.append('../venv/lib/python3.8/')
from PyQt5.QtWidgets import QDialog, QLabel, QPushButton
from PyQt5.QtCore import Qt

logger = logging.getLogger('client_')


class AddContactDialog(QDialog):
    def __init__(self, sock, database, contact):
        """
        GUI for add dialog window
        :param sock: connection socket
        :param database: connected database
        :param contact: name of adding contact
        """
        super().__init__()
        self.sock = sock
        self.database = database

        self.setFixedSize(350, 120)
        self.setWindowTitle('Выберите контакт для добавления:')
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setModal(True)

        self.selector_label = QLabel(f'would u add:\n'
                                     f' {contact}', self)
        self.selector_label.setFixedSize(200, 40)
        self.selector_label.move(10, 0)
        #
        # self.selector = QComboBox(self)
        # self.selector.setFixedSize(200, 20)
        # self.selector.move(10, 30)

        # self.btn_refresh = QPushButton('Обновить список', self)
        # self.btn_refresh.setFixedSize(100, 30)
        # self.btn_refresh.move(60, 60)

        self.btn_ok = QPushButton('Добавить', self)
        self.btn_ok.setFixedSize(100, 30)
        self.btn_ok.move(230, 20)

        self.btn_cancel = QPushButton('Отмена', self)
        self.btn_cancel.setFixedSize(100, 30)
        self.btn_cancel.move(230, 60)
        self.btn_cancel.clicked.connect(self.close)

        # self.possible_contacts_update()
        # self.btn_refresh.clicked.connect(self.update_possible_contacts)

    def possible_contacts_update(self):
        """

        :return: set of possible contact from database
        """
        self.selector.clear()
        contacts_list = set(self.database.get_contacts())
        users_list = set(self.database.get_users())
        users_list.remove(self.sock.name)
        self.selector.addItems(users_list - contacts_list)

    def update_possible_contacts(self):
        """
        first of all update data from server_ database and then update client_ database
        :return:
        """
        try:
            self.sock.user_list_update()
        except OSError:
            pass
        else:
            logger.debug('updated successfully')
            self.possible_contacts_update()
