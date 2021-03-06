'''
Created on 01.10.2012
@author: vlkv
'''
import os
import PyQt4.QtGui as QtGui
import reggata
import reggata.helpers as helpers
import reggata.consts as consts
import reggata.statistics as stats
from reggata.helpers import show_exc_info
from reggata.consts import STATUSBAR_TIMEOUT
from reggata.errors import MsgException, LoginError
from reggata.ui.ui_aboutdialog import Ui_AboutDialog # TODO: gui imports should be removed from logic package!
from reggata.data.db_schema import User
from reggata.data.commands import SaveNewUserCommand, ChangeUserPasswordCommand
from reggata.data.repo_mgr import RepoMgr
from reggata.logic.ext_app_mgr import ExtAppMgr
from reggata.logic.handler_signals import HandlerSignals
from reggata.logic.worker_threads import ImportItemsThread
from reggata.logic.action_handlers import AbstractActionHandler
from reggata.gui.external_apps_dialog import ExternalAppsDialog
from reggata.gui.user_dialogs_facade import UserDialogsFacade
from reggata.gui.user_dialog import UserDialog


class CreateUserActionHandler(AbstractActionHandler):
    def __init__(self, model):
        super(CreateUserActionHandler, self).__init__(model)

    def handle(self):
        try:
            self._model.checkActiveRepoIsNotNone()

            user = User()

            dialogs = UserDialogsFacade()
            if not dialogs.execUserDialog(
                user=user, gui=self._model.gui, dialogMode=UserDialog.CREATE_MODE):
                return

            uow = self._model.repo.createUnitOfWork()
            try:
                uow.executeCommand(SaveNewUserCommand(user))
                self._model.user = user
            finally:
                uow.close()

            stats.sendEvent("main_window.create_user")

        except Exception as ex:
            show_exc_info(self._model.gui, ex)


class LoginUserActionHandler(AbstractActionHandler):
    def __init__(self, model):
        super(LoginUserActionHandler, self).__init__(model)

    def handle(self):
        try:
            self._model.checkActiveRepoIsNotNone()

            user = User()

            dialogs = UserDialogsFacade()
            if not dialogs.execUserDialog(
                user=user, gui=self._model.gui, dialogMode=UserDialog.LOGIN_MODE):
                return

            self._model.loginUser(user.login, user.password)

            stats.sendEvent("main_window.login_user")

        except Exception as ex:
            show_exc_info(self._model.gui, ex)


class LogoutUserActionHandler(AbstractActionHandler):
    def __init__(self, model):
        super(LogoutUserActionHandler, self).__init__(model)

    def handle(self):
        try:
            self._model.user = None
            stats.sendEvent("main_window.logout_user")
        except Exception as ex:
            show_exc_info(self._model.gui, ex)


class ChangeUserPasswordActionHandler(AbstractActionHandler):
    def __init__(self, model):
        super(ChangeUserPasswordActionHandler, self).__init__(model)

    def handle(self):
        try:
            self._model.checkActiveRepoIsNotNone()
            self._model.checkActiveUserIsNotNone()

            user = self._model.user

            dialogs = UserDialogsFacade()
            dialogExecOk, newPasswordHash = \
                dialogs.execChangeUserPasswordDialog(user=user, gui=self._model.gui)
            if not dialogExecOk:
                return

            uow = self._model.repo.createUnitOfWork()
            try:
                command = ChangeUserPasswordCommand(user.login, newPasswordHash)
                uow.executeCommand(command)
            finally:
                uow.close()

            user.password = newPasswordHash

            stats.sendEvent("main_window.change_user_password")

        except Exception as ex:
            show_exc_info(self._model.gui, ex)
        else:
            self._emitHandlerSignal(HandlerSignals.STATUS_BAR_MESSAGE,
                self.tr("Operation completed."), STATUSBAR_TIMEOUT)


class CreateRepoActionHandler(AbstractActionHandler):
    def  __init__(self, model):
        super(CreateRepoActionHandler, self).__init__(model)

    def handle(self):
        try:
            dialogs = UserDialogsFacade()
            basePath = dialogs.getExistingDirectory(
                self._model.gui, self.tr("Choose a base path for new repository"))

            if not basePath:
                raise MsgException(
                    self.tr("You haven't chosen existent directory. Operation canceled."))

            # QFileDialog returns forward slashes in windows! Because of this
            # the path should be normalized
            basePath = os.path.normpath(basePath)
            self._model.repo = RepoMgr.createNewRepo(basePath)
            self._model.user = self.__createDefaultUser()

            stats.sendEvent("main_window.create_repo")

        except Exception as ex:
            show_exc_info(self._model.gui, ex)


    def __createDefaultUser(self):
        self._model.checkActiveRepoIsNotNone()

        defaultLogin = consts.DEFAULT_USER_LOGIN
        defaultPassword = helpers.computePasswordHash(consts.DEFAULT_USER_PASSWORD)
        user = User(login=defaultLogin, password=defaultPassword)

        uow = self._model.repo.createUnitOfWork()
        try:
            uow.executeCommand(SaveNewUserCommand(user))
        finally:
            uow.close()
        return user


class CloseRepoActionHandler(AbstractActionHandler):
    def __init__(self, model):
        super(CloseRepoActionHandler, self).__init__(model)

    def handle(self):
        try:
            self._model.checkActiveRepoIsNotNone()
            self._model.repo = None
            self._model.user = None

            stats.sendEvent("main_window.close_repo")

        except Exception as ex:
            show_exc_info(self._model.gui, ex)


class OpenRepoActionHandler(AbstractActionHandler):
    def __init__(self, model):
        super(OpenRepoActionHandler, self).__init__(model)

    def handle(self):
        try:
            dialogs = UserDialogsFacade()
            basePath = dialogs.getExistingDirectory(
                self._model.gui, self.tr("Choose a repository base path"))

            if not basePath:
                raise Exception(
                    self.tr("You haven't chosen existent directory. Operation canceled."))

            #QFileDialog returns forward slashes in windows! Because of this path should be normalized
            basePath = os.path.normpath(basePath)
            self._model.repo = RepoMgr(basePath)
            self._model.user = None
            self._model.loginRecentUser()

            stats.sendEvent("main_window.open_repo")

        except LoginError:
            self.__letUserLoginByHimself()

        except Exception as ex:
            show_exc_info(self._model.gui, ex)


    def __letUserLoginByHimself(self):
        user = User()
        dialogs = UserDialogsFacade()
        if not dialogs.execUserDialog(
            user=user, gui=self._model.gui, dialogMode=UserDialog.LOGIN_MODE):
            return
        try:
            self._model.loginUser(user.login, user.password)
        except Exception as ex:
            show_exc_info(self._model.gui, ex)


class AddCurrentRepoToFavoritesActionHandler(AbstractActionHandler):

    def __init__(self, model, favoriteReposStorage):
        super(AddCurrentRepoToFavoritesActionHandler, self).__init__(model)
        self.__favoriteReposStorage = favoriteReposStorage

    def handle(self):
        try:
            self._model.checkActiveRepoIsNotNone()
            self._model.checkActiveUserIsNotNone()

            repoBasePath = self._model.repo.base_path
            userLogin = self._model.user.login

            #TODO: Maybe ask user for a repoAlias...
            self.__favoriteReposStorage.addRepoToFavorites(userLogin,
                                                           repoBasePath,
                                                           os.path.basename(repoBasePath))

            self._emitHandlerSignal(HandlerSignals.STATUS_BAR_MESSAGE,
                self.tr("Current repository saved in favorites list."), STATUSBAR_TIMEOUT)
            self._emitHandlerSignal(HandlerSignals.LIST_OF_FAVORITE_REPOS_CHANGED)

            stats.sendEvent("main_window.add_repo_to_favorites")

        except Exception as ex:
            show_exc_info(self._model.gui, ex)


class RemoveCurrentRepoFromFavoritesActionHandler(AbstractActionHandler):
    def __init__(self, model, favoriteReposStorage):
        super(RemoveCurrentRepoFromFavoritesActionHandler, self).__init__(model)
        self.__favoriteReposStorage = favoriteReposStorage

    def handle(self):
        try:
            self._model.checkActiveRepoIsNotNone()
            self._model.checkActiveUserIsNotNone()

            repoBasePath = self._model.repo.base_path
            userLogin = self._model.user.login

            self.__favoriteReposStorage.removeRepoFromFavorites(userLogin, repoBasePath)

            self._emitHandlerSignal(HandlerSignals.STATUS_BAR_MESSAGE,
                self.tr("Current repository removed from favorites list."), STATUSBAR_TIMEOUT)
            self._emitHandlerSignal(HandlerSignals.LIST_OF_FAVORITE_REPOS_CHANGED)

            stats.sendEvent("main_window.remove_repo_from_favorites")

        except Exception as ex:
            show_exc_info(self._model.gui, ex)


class ImportItemsActionHandler(AbstractActionHandler):
    '''
        Imports previously exported items.
    '''
    def __init__(self, model, dialogs):
        super(ImportItemsActionHandler, self).__init__(model)
        self._dialogs = dialogs

    def handle(self):
        try:
            self._model.checkActiveRepoIsNotNone()
            self._model.checkActiveUserIsNotNone()

            importFromFilename = self._dialogs.getOpenFileName(
                self._model.gui,
                self.tr("Open Reggata Archive File"),
                self.tr("Reggata Archive File (*.raf)"))
            if not importFromFilename:
                raise MsgException(self.tr("You haven't chosen a file. Operation canceled."))

            thread = ImportItemsThread(self, self._model.repo, importFromFilename,
                                       self._model.user.login)

            self._dialogs.startThreadWithWaitDialog(thread, self._model.gui, indeterminate=False)

            self._emitHandlerSignal(HandlerSignals.ITEM_CREATED)

            #TODO: display information about how many items were imported
            self._emitHandlerSignal(HandlerSignals.STATUS_BAR_MESSAGE,
                self.tr("Operation completed."), STATUSBAR_TIMEOUT)

            stats.sendEvent("main_window.import_items")

        except Exception as ex:
            show_exc_info(self._model.gui, ex)



class ExitReggataActionHandler(AbstractActionHandler):
    def __init__(self, tool):
        super(ExitReggataActionHandler, self).__init__(tool)

    def handle(self):
        try:
            self._tool.gui.close()
            stats.sendEvent("main_window.exit_reggata")
        except Exception as ex:
            show_exc_info(self._tool.gui, ex)


class ManageExternalAppsActionHandler(AbstractActionHandler):
    def __init__(self, model, dialogs):
        super(ManageExternalAppsActionHandler, self).__init__(model)
        self._dialogs = dialogs

    def handle(self):
        try:
            extAppMgrState = ExtAppMgr.readCurrentState()
            dialog = ExternalAppsDialog(self._model.gui, extAppMgrState, self._dialogs)
            if dialog.exec_() != QtGui.QDialog.Accepted:
                return

            ExtAppMgr.setCurrentState(dialog.extAppMgrState())
            self._emitHandlerSignal(HandlerSignals.REGGATA_CONF_CHANGED)
            self._emitHandlerSignal(HandlerSignals.STATUS_BAR_MESSAGE,
                self.tr("Operation completed."), STATUSBAR_TIMEOUT)

            stats.sendEvent("main_window.manage_external_apps")

        except Exception as ex:
            show_exc_info(self._model.gui, ex)




class ShowAboutDialogActionHandler(AbstractActionHandler):
    def __init__(self, model):
        super(ShowAboutDialogActionHandler, self).__init__(model)

    def handle(self):
        try:
            ad = AboutDialog(self._model.gui)
            ad.exec_()
            stats.sendEvent("main_window.show_about_dialog")
        except Exception as ex:
            show_exc_info(self._model.gui, ex)
        else:
            self._emitHandlerSignal(HandlerSignals.STATUS_BAR_MESSAGE,
                self.tr("Operation completed."), STATUSBAR_TIMEOUT)



about_message = \
'''
<h1>Reggata</h1>
<p>Version: {0}</p>

<p>Reggata is a tagging system for local files.</p>

<p>Copyright 2012 Vitaly Volkov, <font color="blue">vitvlkv@gmail.com</font></p>

<p>Home page: <font color="blue">http://github.com/vlkv/reggata</font></p>

<p>Reggata is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
</p>

<p>Reggata is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
</p>

<p>You should have received a copy of the GNU General Public License
along with Reggata.  If not, see <font color="blue">http://www.gnu.org/licenses</font>.
</p>
'''.format(reggata.__version__)


class AboutDialog(QtGui.QDialog):
    def __init__(self, parent=None):
        super(AboutDialog, self).__init__(parent)
        self.ui = Ui_AboutDialog()
        self.ui.setupUi(self)
        self.ui.textEdit.setHtml(about_message)


class OpenFavoriteRepoActionHandler(AbstractActionHandler):
    def __init__(self, model):
        super(OpenFavoriteRepoActionHandler, self).__init__(model)

    def handle(self):
        try:
            action = self.sender()
            repoBasePath = action.repoBasePath

            currentUser = self._model.user
            assert currentUser is not None

            self._model.repo = RepoMgr(repoBasePath)

            try:
                self._model.loginUser(currentUser.login, currentUser.password)
                self._emitHandlerSignal(HandlerSignals.STATUS_BAR_MESSAGE,
                    self.tr("Repository opened. Login succeded."), STATUSBAR_TIMEOUT)

            except LoginError:
                self._model.user = None
                self._emitHandlerSignal(HandlerSignals.STATUS_BAR_MESSAGE,
                    self.tr("Repository opened. Login failed."), STATUSBAR_TIMEOUT)

            stats.sendEvent("main_window.open_favorite_repo")

        except Exception as ex:
            show_exc_info(self._model.gui, ex)
