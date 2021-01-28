import sys
from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, qApp, QDialog
from .login_reg_window import Ui_Dialog


class LoginWindow(QDialog):
    """
    login window GUI
    """
    def __init__(self):
        super(LoginWindow, self).__init__()
        self.set_name = False
        self.set_pwd = True
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.ui.ok_btn.clicked.connect(self.get_name)
        self.ui.cancel_btn.clicked.connect(qApp.exit)
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

    def get_name(self):
        """
        get username from GUI
        :return:
        """
        if self.ui.nick_line.text() and self.ui.pass_line.text():
            self.check_verify()
            self.set_name = True
            qApp.exit()

    def check_verify(self):
        """
        verify equal between passcode and verify passcode lines
        :return:
        """
        if self.ui.to_register.isChecked():
            if self.ui.pass_line.text() == self.ui.verify_line.text():
                return
            else:
                self.set_pwd = False
        return


if __name__ == '__main__':
    app = QApplication(sys.argv)
    application = LoginWindow()
    sys.exit(app.exec_())


