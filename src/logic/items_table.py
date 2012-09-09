# -*- coding: utf-8 -*-
'''
Created on 21.01.2012
@author: vlkv
'''
import os
import consts
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import Qt
import traceback
from data.db_schema import Item, DataRef
from parsers import query_parser
from logic.worker_threads import ThumbnailBuilderThread
from data.repo_mgr import *
from data.commands import *
from logic.abstract_tool import AbstractTool
from gui.items_table_tool_gui import ItemsTableToolGui, ItemsTableModel
from logic.handler_signals import HandlerSignals
from gui.common_widgets import Completer
from logic.tag_cloud import TagCloud
from logic.action_handlers import ActionHandlerStorage, AddSingleItemActionHandler


class ItemsTable(AbstractTool):
    
    TOOL_ID = "ItemsTableTool"
    
    def __init__(self, widgetsUpdateManager, itemsLock, mainWindow, dialogsFacade):
        super(ItemsTable, self).__init__()
        
        self._repo = None
        self._user = None
        
        self._widgetsUpdateManager = widgetsUpdateManager
        self._itemsLock = itemsLock
        self._mainWindow = mainWindow
        self._dialogsFacade = dialogsFacade
        
        self._gui = None
        
        
    def id(self):
        return ItemsTable.TOOL_ID

        
    def title(self):
        return self.tr("Items Table Tool")

        
    def createGui(self, guiParent):
        self._gui = ItemsTableToolGui(guiParent)
        self._actionHandlers = ActionHandlerStorage(self._widgetsUpdateManager)
         
        return self._gui
    
    @property
    def gui(self):
        return self._gui

    
    
    def createMainMenuActions(self, menuParent, actionsParent):
        menu = self._gui.createMenuWithActions()
        
        self._actionHandlers.registerActionHandler(
            self._gui.actions['addOneItem'], 
            AddSingleItemActionHandler(self, self._dialogsFacade))
        
        return menu
    
#        # Separator
#        self.__actionHandlers.registerActionHandler(
#            self.ui.action_item_check_integrity, CheckItemIntegrityActionHandler(self))
#        
#        strategy = {Item.ERROR_FILE_HASH_MISMATCH: FileHashMismatchFixer.TRY_FIND_FILE}
#        self.__actionHandlers.registerActionHandler(
#            self.ui.action_item_fix_hash_error, FixItemIntegrityErrorActionHandler(self, strategy))
#        
#        strategy = {Item.ERROR_FILE_HASH_MISMATCH: FileHashMismatchFixer.UPDATE_HASH}
#        self.__actionHandlers.registerActionHandler(
#            self.ui.action_item_update_file_hash, FixItemIntegrityErrorActionHandler(self, strategy))
#        
#        strategy = {Item.ERROR_HISTORY_REC_NOT_FOUND: HistoryRecNotFoundFixer.TRY_PROCEED_ELSE_RENEW}
#        self.__actionHandlers.registerActionHandler(
#            self.ui.action_item_fix_history_rec_error, FixItemIntegrityErrorActionHandler(self, strategy))
#        
#        strategy = {Item.ERROR_FILE_NOT_FOUND: FileNotFoundFixer.TRY_FIND}
#        self.__actionHandlers.registerActionHandler(
#            self.ui.action_fix_file_not_found_try_find, FixItemIntegrityErrorActionHandler(self, strategy))
#        
#        strategy = {Item.ERROR_FILE_NOT_FOUND: FileNotFoundFixer.DELETE}
#        self.__actionHandlers.registerActionHandler(
#            self.ui.action_fix_file_not_found_delete, FixItemIntegrityErrorActionHandler(self, strategy))

#    def __createItemsTableContextMenu(self):
#        menu = QtGui.QMenu(self)
#        menu.addAction(self.ui.action_item_view)
#        menu.addAction(self.ui.action_item_view_m3u)
#        menu.addAction(self.ui.action_item_view_image_viewer)
#        menu.addAction(self.ui.action_item_to_external_filemanager)
#        menu.addMenu(self.ui.menuExport_items)
#        menu.addSeparator()
#        menu.addAction(self.ui.action_item_edit)
#        menu.addAction(self.ui.action_item_rebuild_thumbnail)        
#        menu.addSeparator()
#        menu.addAction(self.ui.action_item_delete)
#        menu.addSeparator()
#        menu.addAction(self.ui.action_item_check_integrity)
#        menu.addMenu(self.ui.menuFix_integrity_errors)
#        return menu

    
    def handlerSignals(self):
        return [HandlerSignals.ITEM_CHANGED, HandlerSignals.ITEM_CREATED, 
             HandlerSignals.ITEM_DELETED]


    def enable(self):
        pass

    
    def disable(self):
        pass

    
    def toggleEnableDisable(self, enable):
        if enable:
            self.enable()
        else:
            self.disable()
    
    
    def update(self):
        self._gui.update()
        
    @property
    def repo(self):
        return self._repo
        
    def setRepo(self, repo):
        self._repo = repo
        if repo is not None:
            itemsTableModel = ItemsTableModel(repo, self._itemsLock,
                                              self._user.login if self._user is not None else None)
            self._gui.itemsTableModel = itemsTableModel 
            
            completer = Completer(repo=repo, parent=self._gui)
            self._gui.set_tag_completer(completer)

            self._gui.restore_columns_width()
        else:
            self._gui.save_columns_width()
            
            self._gui.itemsTableModel = None
        
            self._gui.set_tag_completer(None)
    
    def checkActiveRepoIsNotNone(self):
        if self._repo is None:
            raise CurrentRepoIsNoneError("Current repository is None")
    
    
    @property
    def user(self):
        return self._user
    
    def setUser(self, user):
        self._user = user
        userLogin = user.login if user is not None else None
        if self._gui.itemsTableModel is not None:
            self._gui.itemsTableModel.user_login = userLogin 
            
    def checkActiveUserIsNotNone(self):
        if self._user is None:
            raise CurrentUserIsNoneError("Current user is None")
    
    
    def restoreRecentState(self):
        self._gui.restore_columns_width()


    def relatedToolIds(self):
        return [TagCloud.TOOL_ID]
    
    
    def connectRelatedTool(self, relatedTool):
        assert relatedTool is not None
        
        if relatedTool.id() == TagCloud.TOOL_ID:
            self.__connectTagCloudTool(relatedTool)
        else:
            assert False, "Unexpected relatedTool.id() = " + str(relatedTool.id())
    
    
    def __connectTagCloudTool(self, tagCloud):
        tagCloud._connectItemsTableTool(self)
        
        
    