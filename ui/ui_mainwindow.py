# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'mainwindow.ui'
#
# Created: Mon Nov 15 23:00:16 2010
#      by: PyQt4 UI code generator 4.8.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.resize(659, 447)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.verticalLayout_3 = QtGui.QVBoxLayout(self.centralwidget)
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.frame = QtGui.QFrame(self.centralwidget)
        self.frame.setObjectName(_fromUtf8("frame"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.frame)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.label = QtGui.QLabel(self.frame)
        self.label.setObjectName(_fromUtf8("label"))
        self.horizontalLayout.addWidget(self.label)
        self.lineEdit_query = QtGui.QLineEdit(self.frame)
        self.lineEdit_query.setObjectName(_fromUtf8("lineEdit_query"))
        self.horizontalLayout.addWidget(self.lineEdit_query)
        self.pushButton_query_exec = QtGui.QPushButton(self.frame)
        self.pushButton_query_exec.setObjectName(_fromUtf8("pushButton_query_exec"))
        self.horizontalLayout.addWidget(self.pushButton_query_exec)
        self.pushButton_query_reset = QtGui.QPushButton(self.frame)
        self.pushButton_query_reset.setObjectName(_fromUtf8("pushButton_query_reset"))
        self.horizontalLayout.addWidget(self.pushButton_query_reset)
        self.verticalLayout_2.addLayout(self.horizontalLayout)
        self.tableView_items = QtGui.QTableView(self.frame)
        self.tableView_items.setObjectName(_fromUtf8("tableView_items"))
        self.verticalLayout_2.addWidget(self.tableView_items)
        self.verticalLayout_3.addWidget(self.frame)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 659, 29))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        self.menu_repo = QtGui.QMenu(self.menubar)
        self.menu_repo.setObjectName(_fromUtf8("menu_repo"))
        self.menu = QtGui.QMenu(self.menubar)
        self.menu.setObjectName(_fromUtf8("menu"))
        self.menuItem = QtGui.QMenu(self.menubar)
        self.menuItem.setObjectName(_fromUtf8("menuItem"))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        MainWindow.setStatusBar(self.statusbar)
        self.dockWidget_tag_cloud = QtGui.QDockWidget(MainWindow)
        self.dockWidget_tag_cloud.setFloating(False)
        self.dockWidget_tag_cloud.setFeatures(QtGui.QDockWidget.DockWidgetFloatable|QtGui.QDockWidget.DockWidgetMovable)
        self.dockWidget_tag_cloud.setObjectName(_fromUtf8("dockWidget_tag_cloud"))
        self.dockWidgetContents = QtGui.QWidget()
        self.dockWidgetContents.setObjectName(_fromUtf8("dockWidgetContents"))
        self.dockWidget_tag_cloud.setWidget(self.dockWidgetContents)
        MainWindow.addDockWidget(QtCore.Qt.DockWidgetArea(4), self.dockWidget_tag_cloud)
        self.action_repo_create = QtGui.QAction(MainWindow)
        self.action_repo_create.setObjectName(_fromUtf8("action_repo_create"))
        self.action_repo_open = QtGui.QAction(MainWindow)
        self.action_repo_open.setObjectName(_fromUtf8("action_repo_open"))
        self.action_repo_close = QtGui.QAction(MainWindow)
        self.action_repo_close.setObjectName(_fromUtf8("action_repo_close"))
        self.action_item_add = QtGui.QAction(MainWindow)
        self.action_item_add.setObjectName(_fromUtf8("action_item_add"))
        self.action_user_create = QtGui.QAction(MainWindow)
        self.action_user_create.setObjectName(_fromUtf8("action_user_create"))
        self.action_user_login = QtGui.QAction(MainWindow)
        self.action_user_login.setObjectName(_fromUtf8("action_user_login"))
        self.action_user_logout = QtGui.QAction(MainWindow)
        self.action_user_logout.setObjectName(_fromUtf8("action_user_logout"))
        self.action_item_edit = QtGui.QAction(MainWindow)
        self.action_item_edit.setObjectName(_fromUtf8("action_item_edit"))
        self.menu_repo.addAction(self.action_repo_create)
        self.menu_repo.addAction(self.action_repo_open)
        self.menu_repo.addAction(self.action_repo_close)
        self.menu.addAction(self.action_user_create)
        self.menu.addAction(self.action_user_login)
        self.menu.addAction(self.action_user_logout)
        self.menuItem.addAction(self.action_item_add)
        self.menuItem.addAction(self.action_item_edit)
        self.menubar.addAction(self.menu_repo.menuAction())
        self.menubar.addAction(self.menu.menuAction())
        self.menubar.addAction(self.menuItem.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QtGui.QApplication.translate("MainWindow", "Reggata", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("MainWindow", "Query:", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_query_exec.setText(QtGui.QApplication.translate("MainWindow", "Execute", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_query_reset.setText(QtGui.QApplication.translate("MainWindow", "Reset", None, QtGui.QApplication.UnicodeUTF8))
        self.menu_repo.setTitle(QtGui.QApplication.translate("MainWindow", "Repository", None, QtGui.QApplication.UnicodeUTF8))
        self.menu.setTitle(QtGui.QApplication.translate("MainWindow", "User", None, QtGui.QApplication.UnicodeUTF8))
        self.menuItem.setTitle(QtGui.QApplication.translate("MainWindow", "Item", None, QtGui.QApplication.UnicodeUTF8))
        self.dockWidget_tag_cloud.setWindowTitle(QtGui.QApplication.translate("MainWindow", "Tag cloud", None, QtGui.QApplication.UnicodeUTF8))
        self.action_repo_create.setText(QtGui.QApplication.translate("MainWindow", "New", None, QtGui.QApplication.UnicodeUTF8))
        self.action_repo_open.setText(QtGui.QApplication.translate("MainWindow", "Open", None, QtGui.QApplication.UnicodeUTF8))
        self.action_repo_close.setText(QtGui.QApplication.translate("MainWindow", "Close", None, QtGui.QApplication.UnicodeUTF8))
        self.action_item_add.setText(QtGui.QApplication.translate("MainWindow", "Add", None, QtGui.QApplication.UnicodeUTF8))
        self.action_user_create.setText(QtGui.QApplication.translate("MainWindow", "Create", None, QtGui.QApplication.UnicodeUTF8))
        self.action_user_login.setText(QtGui.QApplication.translate("MainWindow", "Login", None, QtGui.QApplication.UnicodeUTF8))
        self.action_user_logout.setText(QtGui.QApplication.translate("MainWindow", "Logout", None, QtGui.QApplication.UnicodeUTF8))
        self.action_item_edit.setText(QtGui.QApplication.translate("MainWindow", "Edit", None, QtGui.QApplication.UnicodeUTF8))

