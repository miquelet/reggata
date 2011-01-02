# -*- coding: utf-8 -*-
'''
Copyright 2010 Vitaly Volkov

This file is part of Reggata.

Reggata is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Reggata is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Reggata.  If not, see <http://www.gnu.org/licenses/>.

Created on 05.12.2010

@author: vlkv
'''
from user_config import UserConfig
from helpers import tr
import os
import consts
import subprocess
import shlex

class ExtAppMgr(object):
    '''
    Класс для вызова внешних приложений, которые нужны для просмотра
    элементов (файлов) хранилища.
    
    Кстати, если редактировать файлы, а не просматривать, то надо как-то оперативно
    обновлять их DataRef.hash.
    
    Пример фрагмента reggata.conf:
    
    ext_app_mgr.file_types = ['images', 'pdf', 'audio']
    ext_app_mgr.images.extensions = ['.jpg', '.png', '.gif', '.bmp']
    ext_app_mgr.images.command = gqview {}
    ext_app_mgr.pdf.extensions = ['.pdf']
    ext_app_mgr.pdf.command = xpdf {}
    ext_app_mgr.audio.extensions = ['.mp3', '.ogg', '.flac', '.wav', '.m3u']
    ext_app_mgr.audio.command = vlc {}    
    '''

    def __init__(self):

        file_types_list = eval(UserConfig().get('ext_app_mgr.file_types', "[]"))
        
        #Ключ - название группы файлов, значение - список расширений файлов
        self.file_types = dict()
        for file_type in file_types_list:
            self.file_types[file_type] = eval(UserConfig().get('ext_app_mgr.{}.extensions'.format(file_type)))
            
        #Ключ - расширение файла (в нижнем регистре), значение - название группы файлов
        self.extensions = dict()
        for type, ext_list in self.file_types.items():             
            for ext in ext_list:
                ext = ext.lower()
                if ext in self.extensions.keys():
                    raise ValueError(tr("File extension {} cannot be in more than one file_type group.").format(ext))
                self.extensions[ext] = type
             
    def invoke(self, abs_path, file_type=None):
        if not file_type:
            name, ext = os.path.splitext(abs_path)
            file_type = self.extensions.get(ext.lower())
        
        if not file_type:
            raise Exception(tr("File type is not defined for {0} file extension. Edit your {1} file.").format(ext, consts.USER_CONFIG_FILE))
        
        command = UserConfig().get("ext_app_mgr.{}.command".format(file_type))
        if not command:
            raise Exception(tr("Command for file_type {0} not found. Edit your {1} file.").format(file_type, consts.USER_CONFIG_FILE))

        command = command.format('"' + abs_path + '"')
        print("subprocess.Popen(): " + command)
        args = shlex.split(command)
        print(args)
        #subprocess.call(args) #Такой вызов блокирует текущий поток
        pid = subprocess.Popen(args).pid #Такой вызов не блокирует поток
        print("Created process with PID = {}".format(pid))


if __name__ == '__main__':
    pass    

