# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\changeuserpassword.ui'
#
# Created: Tue Oct 29 20:36:08 2013
#      by: PyQt4 UI code generator 4.10
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_ChangeUserPasswordDialog(object):
    def setupUi(self, ChangeUserPasswordDialog):
        ChangeUserPasswordDialog.setObjectName(_fromUtf8("ChangeUserPasswordDialog"))
        ChangeUserPasswordDialog.resize(294, 161)
        ChangeUserPasswordDialog.setModal(False)
        self.verticalLayout = QtGui.QVBoxLayout(ChangeUserPasswordDialog)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label_login = QtGui.QLabel(ChangeUserPasswordDialog)
        self.label_login.setObjectName(_fromUtf8("label_login"))
        self.gridLayout.addWidget(self.label_login, 0, 0, 1, 1)
        self.lineEdit_user_login = QtGui.QLineEdit(ChangeUserPasswordDialog)
        self.lineEdit_user_login.setReadOnly(True)
        self.lineEdit_user_login.setObjectName(_fromUtf8("lineEdit_user_login"))
        self.gridLayout.addWidget(self.lineEdit_user_login, 0, 1, 1, 1)
        self.label = QtGui.QLabel(ChangeUserPasswordDialog)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 1, 0, 1, 1)
        self.lineEdit_current_password = QtGui.QLineEdit(ChangeUserPasswordDialog)
        self.lineEdit_current_password.setEchoMode(QtGui.QLineEdit.Password)
        self.lineEdit_current_password.setObjectName(_fromUtf8("lineEdit_current_password"))
        self.gridLayout.addWidget(self.lineEdit_current_password, 1, 1, 1, 1)
        self.label_password = QtGui.QLabel(ChangeUserPasswordDialog)
        self.label_password.setObjectName(_fromUtf8("label_password"))
        self.gridLayout.addWidget(self.label_password, 2, 0, 1, 1)
        self.lineEdit_new_password1 = QtGui.QLineEdit(ChangeUserPasswordDialog)
        self.lineEdit_new_password1.setEchoMode(QtGui.QLineEdit.Password)
        self.lineEdit_new_password1.setObjectName(_fromUtf8("lineEdit_new_password1"))
        self.gridLayout.addWidget(self.lineEdit_new_password1, 2, 1, 1, 1)
        self.label_password_repeat = QtGui.QLabel(ChangeUserPasswordDialog)
        self.label_password_repeat.setObjectName(_fromUtf8("label_password_repeat"))
        self.gridLayout.addWidget(self.label_password_repeat, 3, 0, 1, 1)
        self.lineEdit_new_password2 = QtGui.QLineEdit(ChangeUserPasswordDialog)
        self.lineEdit_new_password2.setEchoMode(QtGui.QLineEdit.Password)
        self.lineEdit_new_password2.setObjectName(_fromUtf8("lineEdit_new_password2"))
        self.gridLayout.addWidget(self.lineEdit_new_password2, 3, 1, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.buttonBox = QtGui.QDialogButtonBox(ChangeUserPasswordDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(ChangeUserPasswordDialog)
        QtCore.QMetaObject.connectSlotsByName(ChangeUserPasswordDialog)

    def retranslateUi(self, ChangeUserPasswordDialog):
        ChangeUserPasswordDialog.setWindowTitle(_translate("ChangeUserPasswordDialog", "Change user password", None))
        self.label_login.setText(_translate("ChangeUserPasswordDialog", "Login:", None))
        self.label.setText(_translate("ChangeUserPasswordDialog", "Current password:", None))
        self.label_password.setText(_translate("ChangeUserPasswordDialog", "New password:", None))
        self.label_password_repeat.setText(_translate("ChangeUserPasswordDialog", "Repeat new password:", None))

