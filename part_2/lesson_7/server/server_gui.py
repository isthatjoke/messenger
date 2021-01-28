import sys
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QMainWindow, QAction, qApp, QApplication, QDesktopWidget, QTableView, QPushButton, \
    QLineEdit, QLabel, QFileDialog, QDialog


def gui_create_model(database):
    """
    create model listing for connected users
    :param database: connected database
    :return: list of users
    """
    list_users = database.active_users_list()

    list = QStandardItemModel()
    list.setHorizontalHeaderLabels(['Username', 'IP', 'Port', 'Connection time'])
    for row in list_users:
        user, ip, port, time = row
        user = QStandardItem(user)
        user.setEditable(False)
        ip = QStandardItem(ip)
        ip.setEditable(False)
        port = QStandardItem(str(port))
        port.setEditable(False)
        time = QStandardItem(str(time.replace(microsecond=0)))
        time.setEditable(False)
        list.appendRow([user, ip, port, time])
    return list


def create_stat_model(database):
    """
    create model message statistics for connected users
    :param database: connected database
    :return: static list
    """
    hist_list = database.message_history()
    list = QStandardItemModel()
    list.setHorizontalHeaderLabels(
        ['Username', 'Last login', 'Sent messages', 'Received messages'])
    for row in hist_list:
        user, last_seen, sent, recvd = row
        user = QStandardItem(user)
        user.setEditable(False)
        last_seen = QStandardItem(str(last_seen.replace(microsecond=0)))
        last_seen.setEditable(False)
        sent = QStandardItem(str(sent))
        sent.setEditable(False)
        recvd = QStandardItem(str(recvd))
        recvd.setEditable(False)
        list.appendRow([user, last_seen, sent, recvd])
    return list


class MainGui(QMainWindow):
    """
    server main window GUI settings
    """
    def __init__(self):
        super().__init__()
        self.screen = QDesktopWidget().screenGeometry()
        self.width = int(self.screen.width() / 2)
        self.height = int(self.screen.height() / 1.8)
        self.x = int((self.screen.width() - self.width) / 2)
        self.y = int((self.screen.height() - self.height) / 2)
        self.initUI()

    def initUI(self):
        self.statusBar()
        self.exitAct = QAction('&Exit', self)
        self.exitAct.setShortcut('Ctrl+Q')
        self.exitAct.setStatusTip('Exit application')
        self.exitAct.triggered.connect(qApp.quit)

        self.refresh = QAction('&Refresh', self)
        self.refresh.setStatusTip('Refresh connected clients')

        self.history = QAction('&History', self)
        self.history.setStatusTip('Show clients history')

        self.server_config = QAction('&Server settings', self)
        self.server_config.setStatusTip('Edit server_ settings')

        self.menubar = self.menuBar()

        self.fileMenu = self.menubar.addMenu('&File')
        self.fileMenu.addAction(self.exitAct)

        self.settingsMenu = self.menubar.addMenu('&Settings')
        self.settingsMenu.addAction(self.server_config)

        self.ToolsMenu = self.menubar.addMenu('&Tools')
        self.ToolsMenu.addAction(self.refresh)
        self.ToolsMenu.addAction(self.history)

        self.setWindowTitle('Messenger')

        self.setFixedSize(self.width, self.height)
        self.move(self.x, self.y)
        self.active_users_table = QTableView(self)
        self.active_users_table.move(0, 45)
        self.active_users_table.setFixedSize(self.width, self.height - 65)

        self.show()


class HistoryWindow(QDialog):
    """
    server history window GUI settings
    """
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):

        self.setWindowTitle('Statistics')
        self.setFixedSize(600, 700)
        self.setAttribute(Qt.WA_DeleteOnClose)

        self.close_button = QPushButton('Close', self)
        self.close_button.move(250, 650)
        self.close_button.clicked.connect(self.close)

        self.history_table = QTableView(self)
        self.history_table.move(10, 10)
        self.history_table.setFixedSize(580, 620)

        self.show()


class ConfigWindow(QDialog):
    """
    server settings window GUI settings
    """
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setFixedSize(365, 260)
        self.setWindowTitle('Server configuration')

        self.db_path_label = QLabel('Path to DB file: ', self)
        self.db_path_label.move(10, 10)
        self.db_path_label.setFixedSize(240, 15)

        self.db_path = QLineEdit(self)
        self.db_path.setFixedSize(250, 20)
        self.db_path.move(10, 30)
        self.db_path.setReadOnly(True)

        self.db_path_select = QPushButton('Open...', self)
        self.db_path_select.move(275, 28)

        def open_file_dialog():
            global dialog
            dialog = QFileDialog(self)
            path = dialog.getExistingDirectory()
            # path = path.replace('/', '\\')
            if path:
                self.db_path.clear()
                self.db_path.insert(path)

        self.db_path_select.clicked.connect(open_file_dialog)

        self.db_file_label = QLabel('BD filename: ', self)
        self.db_file_label.move(10, 68)
        self.db_file_label.setFixedSize(180, 15)

        self.db_file = QLineEdit(self)
        self.db_file.move(200, 66)
        self.db_file.setFixedSize(150 , 20)

        self.port_label = QLabel('Connection port:', self)
        self.port_label.move(10, 108)
        self.port_label.setFixedSize(180, 15)

        self.port = QLineEdit(self)
        self.port.move(200, 108)
        self.port.setFixedSize(150, 20)

        self.ip_label = QLabel('Connection ip:', self)
        self.ip_label.move(10, 148)
        self.ip_label.setFixedSize(180, 15)

        self.ip_label_note = QLabel('', self)
        self.ip_label_note.move(10, 168)
        self.ip_label_note.setFixedSize(500, 30)

        self.ip = QLineEdit(self)
        self.ip.move(200, 148)
        self.ip.setFixedSize(150, 20)

        self.save_btn = QPushButton('Save', self)
        self.save_btn.move(190, 220)

        self.close_button = QPushButton('Close', self)
        self.close_button.move(275, 220)
        self.close_button.clicked.connect(self.close)

        self.show()


def main():
    # app = QApplication(sys.argv)
    # ex = MainGui()
    # sys.exit(app.exec_())
    app = QApplication(sys.argv)
    ex = MainGui()
    ex.statusBar().showMessage('Test Statusbar Message')
    test_list = QStandardItemModel(ex)
    test_list.setHorizontalHeaderLabels(['Имя Клиента', 'IP Адрес', 'Порт', 'Время подключения'])
    test_list.appendRow([QStandardItem('1'), QStandardItem('2'), QStandardItem('3')])
    test_list.appendRow([QStandardItem('4'), QStandardItem('5'), QStandardItem('6')])
    ex.active_users_table.setModel(test_list)
    ex.active_users_table.resizeColumnsToContents()

    app.exec_()


if __name__ == '__main__':
    main()
