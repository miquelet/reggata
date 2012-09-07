'''
Created on 04.09.2012
@author: vlkv
'''

# TODO: rename to a better name. Maybe RepoSignals
class HandlerSignals():
    '''Named constants in this class is not the signal names, but the signal types.
    They are arguments of the following signals: handlerSignal, handlerSignals.
    handlerSignal accepts single signal type. handlerSignals accepts a list of
    signal types. See also WidgetsUpdateManager, ActionHandlerStorage and
    AbstractActionHandler classes.
    '''
    
    ITEM_CREATED = "itemCreated"
    ITEM_CHANGED = "itemChanged"
    ITEM_DELETED = "itemDeleted"
    LIST_OF_FAVORITE_REPOS_CHANGED = "listOfFavoriteReposChanged"