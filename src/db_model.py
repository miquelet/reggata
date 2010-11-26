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

Created on 11.10.2010

@author: vlkv
'''
import sqlalchemy as sqa
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from sqlalchemy import ForeignKey, ForeignKeyConstraint
from helpers import tr, is_none_or_empty
import datetime
import os


Base = declarative_base()


class User(Base):
    '''
    Пользователь системы reggata.
    '''
    __tablename__ = "users"
    
    login = sqa.Column(sqa.String, primary_key=True)
    password = sqa.Column(sqa.String)
    group = sqa.Column(sqa.Enum("USER", "ADMIN"), nullable=False, default="USER")
    date_created = sqa.Column(sqa.DateTime)
    
    def check_valid(self):
        if self.login is None or self.login=="":
            raise ValueError(tr("Attribute User.login shouldn't be empty."))        
        return True



#Таблица связей Tag и Item
#tags_items = sqa.Table('tags_items', Base.metadata,
#    sqa.Column('item_id', sqa.Integer, ForeignKey('items.id'), primary_key=True),
#    sqa.Column('tag_name', sqa.String, primary_key=True),
#    sqa.Column('tag_user_login', sqa.String, primary_key=True),
#    ForeignKeyConstraint(['tag_name', 'tag_user_login'], ['tags.name', 'tags.user_login'])
#)



class Item(Base):
    '''
    Элемент (запись, объект) хранилища.
    '''
    __tablename__ = "items"
    
    id = sqa.Column(sqa.Integer, primary_key=True)
    title = sqa.Column(sqa.String, nullable=False)
    notes = sqa.Column(sqa.String)
    user_login = sqa.Column(sqa.String, ForeignKey("users.login"))
    date_created = sqa.Column(sqa.DateTime)
    data_ref_id = sqa.Column(sqa.Integer, ForeignKey("data_refs.id"))
    
    #пользователь-владелец данного элемента
    user = relationship(User)
    
    #связанный файл/ссылка_URL
    data_ref = relationship("DataRef")
    
    #tags - список связанных тегов
    item_tags = relationship("Item_Tag", cascade="all, delete-orphan")
    
    #field_vals - список связанных полей
    item_fields = relationship("Item_Field", cascade="all, delete-orphan")

    def __init__(self, user_login=None, title=None, notes=None, date_created=None):
        self.user_login = user_login
        self.title = title
        self.notes = notes
        if date_created is not None:
            self.date_created = date_created
        else:
            self.date_created = datetime.datetime.today()
        
        
    def check_valid(self):
        '''Проверяет, что состояние объекта допустимое. Связи с другими объектами не учитываются.'''
        if self.title == "" or self.title is None:
            raise Exception(tr("Attribute Item.title shouldn't be empty."))
        return True
        
    def has_data_ref(self, url_str):
        '''Проверяет, связан ли с данным элементом объект DataRef, 
        имеющий url=url_str.'''
        for idr in self.item_data_refs:
            dr = idr.data_ref
            if dr is None:
                continue
            else:
                if dr.url == url_str:
                    return True
        return False
            
    def remove_data_ref(self, url_str):
        '''Удаляет DataRef (и соответствующий Item_DataRef) с указанным значением url.
        Из БД ничего не удаляется, эта операция только в ОП.'''
        target_idr = None
        for idr in self.item_data_refs:
            dr = idr.data_ref
            if dr is None:
                continue
            else:
                if dr.url == url_str:
                    return True
        

        
class DataRef(Base):
    '''
    Ссылка на файл или URL.
    '''
    __tablename__ = "data_refs"
    
    id = sqa.Column(sqa.Integer, primary_key=True)
    
    #Локатор ресурса. Для объектов типа 'FILE' это путь к файлу внутри хранилища
    #для объектов 'URL' --- это непосредственно url-ссылка
    url = sqa.Column(sqa.String, nullable=False, unique=True)
    
    #TODO Возможно имеет смысл для объектов типа FILE отдельно хранить путь и базовое имя файла.
    #Это может пригодиться для поиска файлов по его физическому имени (т.к. так как сейчас
    #если искать наподобие data_ref.url LIKE '%something%' то поиск будет выдавать совпадения,
    #если совпадает имя директории на пути к файлу.
    
    #Тип объекта DataRef
    #TODO Добавить тип ZIP (архив), а также можно добавить тип DIR (директория)
    type = sqa.Column(sqa.Enum("FILE", "URL"), nullable=False)
    
    #Хеш (md5 или sha1) от содержимого файла. Для объектов DataRef имеющих тип type отличный от 'FILE' равен NULL
    hash = sqa.Column(sqa.String)
    
    #Дата/время вычисления хеша hash. Если date_hashed < даты последней модификации физического файла, то хеш нужно пересчитать
    date_hashed = sqa.Column(sqa.DateTime)
    
    #Размер физического файла на диске (для объектов типа 'FILE', для остальных NULL)
    size = sqa.Column(sqa.Integer)    
    
    #Это дата создания объекта DataRef в БД (не имеет ничего общего с датой создания файла на ФС)
    date_created = sqa.Column(sqa.DateTime)
    
    #Пользователь-владелец данного объекта (обычно тот, кто его создал)
    user_login = sqa.Column(sqa.String, ForeignKey("users.login"))
        
    user = relationship(User)
    
    thumbnails = relationship("Thumbnail")

    #При добавлении в хранилище файлов это поле определяет, куда внутри хранилища
    #их необходимо скопировать. Данное поле в БД не сохраняется.
    dst_path = None
    

    def __init__(self, url=None, date_created=None, type=None):
        self.url = url
        
        if date_created is not None:
            self.date_created = date_created
        else:
            self.date_created = datetime.datetime.today()
        self.type = type
        self.dst_path = None
        self.orig_url = None
        
    def is_image(self):
        '''Возвращает True, если данный DataRef объект имеет тип FILE и ссылается
        на растровое графическое изображение, одного из поддерживаемых форматов.
        Проверка основана на сравнении расширения файла со списком расширений поддерживаемых
        форматов.'''
        supported = set([".bmp", ".gif", ".jpg", ".jpeg", ".png", ".pbm", ".pgm", ".ppm", ".xbm", ".xpm"])
        if self.type and self.type == "FILE" and not is_none_or_empty(self.url):
            
            root, ext = os.path.splitext(self.url.lower())
            if ext in supported:
                return True
        
        return False
            
        
    
#TODO Нужно еще подумать, сильно ли нужен данный класс... Хотя в будущем я думаю, что все-таки нужен
class Thumbnail(Base):
    '''
    Миниатюра изображения графического файла, сама ссылка на файл хранится в DataRef.
    
    TODO: Кстати, миниатюры можно добавлять не только для графических файлов.
    Если DataRef указывает на книгу в формате pdf, то миниатюра может содержать 
    изображение титульного листа книги (причем не обязательно очень маленького разрешения).
    Для mp3 файла это может быть обложка диска альбома и т.п.
    '''
    __tablename__ = "thumbnails"
    
    data_ref_id = sqa.Column(sqa.Integer, ForeignKey("data_refs.id"), primary_key=True)
    
    #Размер в пикселях миниатюры (это величина наибольшей размерности)
    size = sqa.Column(sqa.Integer, primary_key=True)
    
    #Размерность (ширина или высота), размер которой записан в size
    dimension = sqa.Column(sqa.Enum("WIDTH", "HEIGHT"), nullable=False)
    
    #Двоичные данные изображения миниатюры
    data = sqa.Column(sqa.Binary)
    
    #Дата создания миниатюры
    #Если Thumbnail.date_created будет новее, чем DataRef.date_hashed, 
    #то это повод для обновления миниатюры
    date_created = sqa.Column(sqa.DateTime)
    
    #Логическое поле, определяющее, следует ли автоматически обновлять миниатюру
    #auto_updated = sqa.Column(sqa.Boolean, default=True)
    
    
    data_ref = relationship(DataRef)
    
    def __init__(self):
        self.data_ref_id = None
        self.size = None        
        self.data = None
        
    
    
class Tag(Base):
    '''
    Тег (ключевое слово), описывающий элементы хранилища.
    '''
    __tablename__ = "tags"
    
    id = sqa.Column(sqa.Integer, primary_key=True)
    name = sqa.Column(sqa.String, nullable=False, unique=True)
    synonym_code = sqa.Column(sqa.Integer)

    def __init__(self, name=None):
        self.id = None
        self.name = name
        self.synonym_code = None
        
class Item_Tag(Base):
    __tablename__ = "items_tags"
        
    item_id = sqa.Column(sqa.Integer, ForeignKey("items.id"), primary_key=True)
    tag_id = sqa.Column(sqa.Integer, ForeignKey("tags.id"), primary_key=True)
    user_login = sqa.Column(sqa.String, ForeignKey("users.login"), primary_key=True)
    
    item = relationship(Item)
    tag = relationship(Tag)
    user = relationship(User)
    
    def __init__(self, tag=None, user_login=None):
        self.tag = tag
        self.user_login = user_login
        if tag is not None:
            self.tag_id = tag.id            
            
        
    
class Field(Base):
    '''
    Поле вида ключ=значение, описывающее элементы хранилища.
    '''
    __tablename__ = "fields"    
    
    id = sqa.Column(sqa.Integer, primary_key=True)
    name = sqa.Column(sqa.String, nullable=False, unique=True)
    synonym_code = sqa.Column(sqa.Integer)
#    value_type = sqa.Column(sqa.Enum("STRING", "NUMBER"), nullable=False, default="STRING")

    def __init__(self, name=None):
        self.id = None
        self.name = name
        self.synonym_code = None
        
    

class Item_Field(Base):
    '''
    Значение поля, связанное с элементом хранилища.
    '''
    __tablename__ = "items_fields"
#    __table_args__ = (ForeignKeyConstraint(["field_name", "field_user_login"], ["fields.name", "fields.user_login"]),
#        {} #{} обязательно нужны, даже если внутри них - пусто
#        )
    
    item_id = sqa.Column(sqa.Integer, ForeignKey("items.id"), primary_key=True)
    field_id = sqa.Column(sqa.String, ForeignKey("fields.id"), primary_key=True)
    user_login = sqa.Column(sqa.String, ForeignKey("users.login"), primary_key=True)
    field_value = sqa.Column(sqa.String, nullable=False, default="")

    item = relationship(Item)
    field = relationship(Field)
    user = relationship(User)
    
    
    def __init__(self, field=None, value=None, user_login=None):
        self.field = field        
        if field is not None:
            self.field_id = field.id
        self.field_value = value
        self.user_login = user_login
                    
        
#TODO сделать классы для групп полей и тегов





