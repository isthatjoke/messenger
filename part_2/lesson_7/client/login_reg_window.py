# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'login_reg.ui'
#
# Created by: PyQt5 UI code generator 5.15.2
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtWidgets


class Ui_Dialog(object):
    """
    login window GUI settings
    """
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(358, 166)
        Dialog.setTabletTracking(True)
        Dialog.setFocusPolicy(QtCore.Qt.StrongFocus)
        Dialog.setSizeGripEnabled(False)
        self.nick_label = QtWidgets.QLabel(Dialog)
        self.nick_label.setGeometry(QtCore.QRect(20, 30, 71, 31))
        self.nick_label.setObjectName("nick_label")
        self.nick_line = QtWidgets.QLineEdit(Dialog)
        self.nick_line.setGeometry(QtCore.QRect(100, 40, 161, 21))
        self.nick_line.setAutoFillBackground(False)
        self.nick_line.setStyleSheet("")
        self.nick_line.setObjectName("nick_line")
        self.ok_btn = QtWidgets.QPushButton(Dialog)
        self.ok_btn.setGeometry(QtCore.QRect(110, 130, 61, 25))
        self.ok_btn.setObjectName("ok_btn")
        self.cancel_btn = QtWidgets.QPushButton(Dialog)
        self.cancel_btn.setGeometry(QtCore.QRect(190, 130, 61, 25))
        self.cancel_btn.setObjectName("cancel_btn")
        self.sign_label = QtWidgets.QLabel(Dialog)
        self.sign_label.setGeometry(QtCore.QRect(130, 10, 91, 20))
        self.sign_label.setObjectName("sign_label")
        self.pass_label = QtWidgets.QLabel(Dialog)
        self.pass_label.setGeometry(QtCore.QRect(20, 70, 67, 17))
        self.pass_label.setObjectName("pass_label")
        self.pass_line = QtWidgets.QLineEdit(Dialog)
        self.pass_line.setGeometry(QtCore.QRect(100, 70, 161, 21))
        self.pass_line.setObjectName("pass_line")
        self.pass_line.setEchoMode(QtWidgets.QLineEdit.Password)
        self.to_register = QtWidgets.QCheckBox(Dialog)
        self.to_register.setGeometry(QtCore.QRect(10, 130, 81, 23))
        self.to_register.setObjectName("to_register")
        self.verify_line = QtWidgets.QLineEdit(Dialog)
        self.verify_line.setGeometry(QtCore.QRect(100, 100, 161, 21))
        self.verify_line.setObjectName("verify_line")
        self.verify_line.setEchoMode(QtWidgets.QLineEdit.Password)
        self.verify_label = QtWidgets.QLabel(Dialog)
        self.verify_label.setGeometry(QtCore.QRect(20, 100, 67, 17))
        self.verify_label.setObjectName("verify_label")

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Authentification"))
        self.nick_label.setText(_translate("Dialog", "nickname"))
        self.ok_btn.setText(_translate("Dialog", "Ok"))
        self.cancel_btn.setText(_translate("Dialog", "Cancel"))
        self.sign_label.setText(_translate("Dialog", "Please sign in"))
        self.pass_label.setText(_translate("Dialog", "password"))
        self.to_register.setText(_translate("Dialog", "register"))
        self.verify_label.setText(_translate("Dialog", "verify"))