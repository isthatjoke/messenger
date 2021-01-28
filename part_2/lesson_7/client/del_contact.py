import sys
import logging

sys.path.append('../venv/lib/python3.8/')
from PyQt5.QtWidgets import QDialog, QLabel, QPushButton, QApplication
from PyQt5.QtCore import Qt

logger = logging.getLogger('client_')


class DelContactDialog(QDialog):
    def __init__(self, database, contact):
        """
        GUI for delete dialog window
        :param database: connected database
        :param contact: name of deleting contact
        """
        super().__init__()
        self.database = database
        self.contact = contact
        self.setFixedSize(350, 120)
        self.setWindowTitle('Confirm deleting contact:')
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setModal(True)

        self.selector_label = QLabel(f'do u really want to delete:\n'
                                     f' {self.contact}', self)
        self.selector_label.setFixedSize(200, 40)
        self.selector_label.move(10, 0)

        self.btn_ok = QPushButton('Удалить', self)
        self.btn_ok.setFixedSize(100, 30)
        self.btn_ok.move(230, 20)

        self.btn_cancel = QPushButton('Отмена', self)
        self.btn_cancel.setFixedSize(100, 30)
        self.btn_cancel.move(230, 60)
        self.btn_cancel.clicked.connect(self.close)


if __name__ == '__main__':
    app = QApplication([])
    window = DelContactDialog(None, 'name')
    window.show()
    app.exec_()
