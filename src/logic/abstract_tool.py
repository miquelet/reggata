'''
Created on 07.09.2012
@author: vlkv
'''

class AbstractTool(object):
    
    def __init__(self):
        pass
    
    def createMainMenuActions(self, menuParent, actionsParent):
        return None
    
    def relatedToolIds(self):
        return []
    
    def connectRelatedTool(self, relatedTool):
        pass