import sys
from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, qApp, QDialog
from .login_fail_window import Ui_Dialog


class LoginWindowFail(QDialog):
    """
    login fail window GUI
    """
    def __init__(self):
        super(LoginWindowFail, self).__init__()
        self.set_name = False
        self.set_pwd = True
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.show()

    def event(self, e):
        """
        func catch events about <enter> or <esc> buttons
        :param e: event
        :return: data for parent class
        """
        if e.type() == QtCore.QEvent.KeyPress and e.key() == 16777216:
            qApp.exit()
        if e.type() == QtCore.QEvent.KeyPress and e.key() == 16777220 \
                or e.type() == QtCore.QEvent.KeyPress and e.key() == 16777221:
            self.get_name()

        return super().event(e)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    application = LoginWindowFail()
    sys.exit(app.exec_())


