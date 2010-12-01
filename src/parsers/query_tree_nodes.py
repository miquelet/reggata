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

Created on 27.11.2010

Модуль содержит классы, представляющие собой узлы дерева разбора предложений 
языка запросов.
'''
import consts
import helpers
from user_config import UserConfig


class QueryExpression(object):
    '''Базовый класс для всех классов-узлов синтаксического дерева разбора.'''
    def interpret(self):
        raise NotImplementedError(tr('This is an abstract method.'))


class Tag(QueryExpression):
    '''Узел синтаксического дерева для представления Тегов.'''
    name = None
    is_negative = None
    
    def __init__(self, name, is_negative=False):
        self.name = name
        self.is_negative = is_negative
    
    def negate(self):
        self.is_negative = not self.is_negative
        
    def interpret(self):
        return self.name
    
    def __str__(self):
        return self.name

class TagsConjunction(QueryExpression):
    '''
    Конъюнкция тегов или их отрицаний, например:
    "Книга И Программирование И НЕ Проектирование"
    
    Реализация такого запроса на SQL:
    
    select * from items i 
    left join items_tags it on i.id = it.item_id
    left join tags t on t.id = it.tag_id
    where
        (t.name='Книга' or t.name='Программирование')    --yes_tags_str
        
        and i.id NOT IN (select i.id from items i        --no_tags_str
        left join items_tags it on i.id = it.item_id 
        left join tags t on t.id = it.tag_id
        where t.name='Проектирование')
        
        group by i.id having count(*)=2                  --group_by_having
    '''    
    
    def __init__(self):
        #Списки для хранения тегов
        self.yes_tags = []
        self.no_tags = []
        
        #Список дополнительных условий USER и PATH
        self.extras_paths = []
        self.extras_users = []
    
    
            
    def interpret(self):
        
        #yes_tags_str, group_by_having
        group_by_having = ""
        if len(self.yes_tags) > 0:
            yes_tags_str = helpers.to_commalist(self.yes_tags, lambda x: "t.name='" + x.interpret() + "'", " or ")
            
            if len(self.yes_tags) > 1:
                group_by_having = " group by i.id having count(*)={} ".format(len(self.yes_tags))
        else:
            yes_tags_str = " 1 "
            
        #extras_users_str
        if len(self.extras_users) > 0:
            comma_list = helpers.to_commalist(self.extras_users, lambda x: "'" + x.interpret() + "'", ", ") 
            extras_users_str = " it.user_login IN (" + comma_list + ") "
        else:
            extras_users_str = " 1 "
        
        #no_tags_str
        if len(self.no_tags) > 0:
            no_tags_str = " i.id NOT IN (select i.id from items i " + \
            " left join items_tags it on i.id = it.item_id " + \
            " left join tags t on t.id = it.tag_id " + \
            " where (" + helpers.to_commalist(self.no_tags, lambda x: "t.name='" + x.interpret() + "'", " or ") + ") " + \
            extras_users_str + ") "
        else:
            no_tags_str = " 1 "
        
        
        #thumbnails_str
        thumbnails_str = "th.size = {} ".format(UserConfig().get("thumbnails.size", consts.THUMBNAIL_DEFAULT_SIZE))
        
        
        #Данный запрос будет попутно извлекать информацию о 
        #связанных с элементами объектов DataRef
        s = '''
        --TagsConjunction.interpret() function
        select distinct 
            i.*,
            dr.id AS dr_id, 
            dr.url AS dr_url, 
            dr.type AS dr_type, 
            dr.hash AS dr_hash, 
            dr.date_hashed AS dr_date_hashed, 
            dr.size AS dr_size, 
            dr.date_created AS dr_date_created, 
            dr.user_login AS dr_user_login,
            th.data_ref_id AS th_data_ref_id, 
            th.size AS th_size, 
            th.dimension AS th_dimension, 
            th.data AS th_data, 
            th.date_created AS th_date_created 
        from items i 
        left outer join items_tags it on i.id = it.item_id 
        left outer join tags t on t.id = it.tag_id
        left outer join data_refs dr on dr.id = i.data_ref_id
        left outer join thumbnails th on th.data_ref_id = dr.id and ''' + thumbnails_str + '''
            where (''' + yes_tags_str + ''') 
            and (''' + extras_users_str + ''') 
            and (''' + no_tags_str + ''')
            ''' + group_by_having
        #!!! Тут будет ошибка, если у data_ref-а будет более одной миниатюры!!!
        #Поэтому нужно указывать в запросе точно какой размер thumbnail-ов необходим.
                
        #TODO сделать интерпретацию для токенов PATH            
            
        return s
    
    @property
    def tags(self):
        return self.yes_tags + self.no_tags
    
    def add_tag(self, tag):
        if tag.is_negative:
            self.no_tags.append(tag)
        else:
            self.yes_tags.append(tag)
            
    def add_extras(self, ext):
        if ext.type == 'USER':
            self.extras_users.append(ext)
        elif ext.type == 'PATH':
            self.extras_paths.append(ext)
        else:
            raise Exception(tr("Unexpected type of extras {}").format(str(ext.type)))
        
        
        
class Extras(QueryExpression):
    type = None
    value = None
    
    def interpret(self):
        return str(self.value)