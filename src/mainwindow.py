# -*- coding: utf-8 -*-
'''
Created on 20.08.2010

@author: vlkv
'''

import sqlite3
import os.path
import sys


from PyQt4.QtCore import (Qt, SIGNAL, QCoreApplication, QTextCodec)
from PyQt4.QtGui import (QApplication, QMainWindow, QDialog, QLineEdit, QTextBrowser, 
						QVBoxLayout, QPushButton, QFileDialog, QErrorMessage, QMessageBox)
import ui_mainwindow
from itemdialog import ItemDialog
from repo_mgr import RepoMgr, UnitOfWork
from translator_helper import tr

import sqlalchemy as sqa
from sqlalchemy.ext.declarative import declarative_base
from db_model import Base, User, Item, DataRef, Tag, Field, FieldVal 
import consts

from pyjavaproperties import Properties
from _pyio import open
from user_config import UserConfig



class MainWindow(QMainWindow):
	'''
	Главное окно приложения reggata.
	'''
	
	#Текущее активное открытое хранилище (объект RepoMgr)
	__active_repo = None
	
	#Текущий пользователь, который работает с программой
	__user = None
	
	def __init__(self, parent=None):
		super(MainWindow, self).__init__(parent)
		self.ui = ui_mainwindow.Ui_MainWindow()
		self.ui.setupUi(self)
		self.connect(self.ui.action_repo_create, SIGNAL("triggered()"), self.action_repo_create)
		self.connect(self.ui.action_repo_close, SIGNAL("triggered()"), self.action_repo_close)
		self.connect(self.ui.action_repo_open, SIGNAL("triggered()"), self.action_repo_open)
		self.connect(self.ui.action_repo_add_file, SIGNAL("triggered()"), self.action_repo_add_files)
		
		
		#Открываем последнее хранилище, с которым работал пользователь 
		tmp = UserConfig().get("recent_repo.base_path")
		if tmp:
			self.__active_repo = RepoMgr(tmp)
		
		
		
	def action_repo_create(self):
		try:
			base_path = QFileDialog.getExistingDirectory(self, tr("Выбор базовой директории хранилища"))
			if base_path == "":
				raise Exception(tr("Необходимо выбрать существующую директорию"))
			self.__active_repo = RepoMgr.create_new_repo(base_path)			
		except Exception as ex:
			QMessageBox.information(self, tr("Отмена операции"), str(ex))
			
		
	def action_repo_close(self):
		try:
			if self.__active_repo is None:
				raise Exception(tr("Нет открытых хранилищ"))
			self.__active_repo = None #Сборщик мусора и деструктор сделают свое дело
		except Exception as ex:
			QMessageBox.information(self, tr("Ошибка"), str(ex))

	def action_repo_open(self):
		try:
			base_path = QFileDialog.getExistingDirectory(self, tr("Выбор базовой директории хранилища"))
			if base_path == "":
				raise Exception(tr("Необходимо выбрать базовую директорию существующего хранилища"))
			self.__active_repo = RepoMgr(base_path)
			UserConfig().store("recent_repo.base_path", base_path)
		except Exception as ex:
			QMessageBox.information(self, tr("Ошибка"), str(ex))
			
	def action_repo_add_files(self):
		try:
			if self.__active_repo is None:
				raise Exception(tr("Необходимо сначала открыть хранилище."))
			
			item = Item()
			d = ItemDialog(item, self)
			if d.exec_():
				uow = self.__active_repo.createUnitOfWork()
				try:
					uow.saveNewItem(item)
				finally:
					uow.close()
				#TODO refresh
				
	
		except Exception as ex:
			QMessageBox.information(self, tr("Ошибка"), str(ex))
			
	def action_repo_add_file(self):
		try:
			if self.__active_repo is None:
				raise Exception(tr("Необходимо сначала открыть хранилище."))
			
			file_path = QFileDialog.getOpenFileName(self, tr("Выберите файл"))
			if file_path == "":
				raise Exception(tr("Отмена операции."))
			
			#Это тест
			uow = self.__active_repo.createUnitOfWork()
			try:
				uow.addTestItem(file_path)
			finally:
				uow.close()
			
		except Exception as ex:
			QMessageBox.information(self, tr("Ошибка"), str(ex))

#class MainWindow(QDialog):
#
#	def __init__(self, parent=None):
#		super(MainWindow, self).__init__(parent)
#		self.setWindowTitle("datorg - главное окно")
#		self.browser = QTextBrowser()
#		self.lineedit = QLineEdit("Type an expression and press Enter")
#		self.lineedit.selectAll()
#
#		layout = QVBoxLayout()
#		layout.addWidget(self.browser)
#		layout.addWidget(self.lineedit)
#		self.setLayout(layout)
#
#		self.lineedit.setFocus()
#		self.connect(self.lineedit, SIGNAL("returnPressed()"), self.updateUi)
#
#
#		self.button = QPushButton("Eval")
#		layout.addWidget(self.button)
#		self.connect(self.button, SIGNAL("pressed()"), self.updateUi)
#
#
#	def updateUi(self):
#		try:
#			text = self.lineedit.text()
#			self.browser.append("{0} = <b>{1}</b>".format(text, eval(text)))
#		except:
#			self.browser.append("<font color=red>{0} is invalid!</font>".format(text))



if __name__ == '__main__':
	
#	engine = sqa.create_engine("sqlite:///" + consts.DB_FILE)
#	Base.metadata.create_all(engine)

	app = QApplication(sys.argv)
	form = MainWindow()
	form.show()
	app.exec_()

#	path = '../test.sqlite'
#	if os.path.isfile(path):
#		conn = sqlite3.connect(path)
#		try:
#			c = conn.cursor()
#			c.execute('''insert into "data"
#				  (uri, size) values ('path_to_file 4', '10243434')''')
#			conn.commit()
#			c.close()
#		except:
#			print 'error: ', sys.exc_info()
#		finally:
#			conn.close()
#
#	else:
#		print 'file not found ', path
