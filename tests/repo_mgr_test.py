import unittest
import os
from exceptions import NotFoundError, AccessError
from abstract_test_cases import AbstractTestCaseWithRepoAndSingleUOW,\
    AbstractTestCaseWithRepo
from tests_context import COPY_OF_TEST_REPO_BASE_PATH, itemWithFile, nonExistingItem,\
    itemWithTagsAndFields, itemWithoutFile
from repo_mgr import UnitOfWork
from db_schema import HistoryRec, Item, DataRef
import helpers


class GetItemTest(AbstractTestCaseWithRepoAndSingleUOW):
    def test_getExistingItem(self):
        item = self.uow.getExpungedItem(itemWithFile.id)
        self.assertEqual(item.title, itemWithFile.title)
        
    def test_getNonExistingItem(self):
        self.assertRaises(NotFoundError, self.uow.getExpungedItem, (nonExistingItem.id))
        
    def test_passBadIdToGetItem(self):
        self.assertRaises(NotFoundError, self.uow.getExpungedItem, ("This str is NOT a valid item id!"))


class SaveNewItemTest(AbstractTestCaseWithRepo):
    
    def test_saveNewMinimalItem(self):
        # "Minimal item" here means that this item has no data references, tags or fields
        item = Item("user", "Minimal Item")
        try:
            uow = self.repo.create_unit_of_work()
            self.savedItemId = uow.saveNewItem(item)
        finally:
            uow.close()
            
        try:
            uow = self.repo.create_unit_of_work()
            savedItem = uow.getExpungedItem(self.savedItemId)
            self.assertEqual(savedItem.title, item.title)
            
            histRec = UnitOfWork._find_item_latest_history_rec(uow.session, savedItem)
            self.assertIsNotNone(histRec)
            self.assertEqual(histRec.operation, HistoryRec.CREATE)
            self.assertEqual(histRec.user_login, savedItem.user_login)
            self.assertIsNone(histRec.parent1_id)
            self.assertIsNone(histRec.parent2_id)
        finally:
            uow.close()
            
    def test_saveNewItemByNonExistentUserLogin(self):
        nonExistentUserLogin = "NonExistentUserLogin" 
        item = Item(nonExistentUserLogin, "Item's title")
        try:
            uow = self.repo.create_unit_of_work()
            self.assertRaises(AccessError, uow.saveNewItem, (item))
            
        finally:
            uow.close()
            
    def test_saveNewItemByNullUserLogin(self):
        userLogin = None
        item = Item(userLogin, "Item's title")
        try:
            uow = self.repo.create_unit_of_work()
            self.assertRaises(AccessError, uow.saveNewItem, (item))
        finally:
            uow.close()
            
    def test_saveNewItemByEmptyUserLogin(self):
        userLogin = ""
        item = Item(userLogin, "Item's title")
        try:
            uow = self.repo.create_unit_of_work()
            self.assertRaises(AccessError, uow.saveNewItem, (item))
        finally:
            uow.close()

    
    def test_saveNewItemWithFileOutsideRepo(self):
        '''
        User wants to add an external file into the repo. File is copied to the repo.
        '''
        item = Item("user", "Item's title")
        self.srcAbsPath = os.path.abspath(os.path.join(self.repo.base_path, "..", "tmp", "file.txt"))
        self.dstRelPath = os.path.join("dir1", "dir2", "dir3", "newFile.txt")
        try:
            uow = self.repo.create_unit_of_work()
            self.savedItemId = uow.saveNewItem(item, self.srcAbsPath, self.dstRelPath)
        finally:
            uow.close()
            
        try:
            uow = self.repo.create_unit_of_work()
            savedItem = uow.getExpungedItem(self.savedItemId)
            self.assertEqual(savedItem.title, item.title)
            
            self.assertIsNotNone(savedItem.data_ref)
            self.assertEqual(savedItem.data_ref.url_raw, helpers.to_db_format(self.dstRelPath))
            self.assertTrue(os.path.exists(os.path.join(self.repo.base_path, savedItem.data_ref.url)))
            
            histRec = UnitOfWork._find_item_latest_history_rec(uow.session, savedItem)
            self.assertIsNotNone(histRec)
            self.assertEqual(histRec.operation, HistoryRec.CREATE)
            self.assertEqual(histRec.user_login, savedItem.user_login)
            self.assertIsNone(histRec.parent1_id)
            self.assertIsNone(histRec.parent2_id)
            
            self.assertTrue(os.path.exists(self.srcAbsPath))
        finally:
            uow.close()
            
    
    def test_saveNewItemWithFileInsideRepo(self):
        '''
        There is an untracked file inside the repo tree. User wants to add such file 
        into the repo to make it a stored file. File is not copied, because it is alredy in 
        the repo tree. It's essential that srcAbsPath and dstRelPath point to the same file.
        '''
        item = Item("user", "Item's title")
        self.srcAbsPath = os.path.abspath(os.path.join(
            self.repo.base_path, "this", "is", "untracked", "file.txt"))
        self.dstRelPath = os.path.join("this", "is", "untracked", "file.txt")
        try:
            uow = self.repo.create_unit_of_work()
            self.savedItemId = uow.saveNewItem(item, self.srcAbsPath, self.dstRelPath)
        finally:
            uow.close()
            
        try:
            uow = self.repo.create_unit_of_work()
            savedItem = uow.getExpungedItem(self.savedItemId)
            self.assertEqual(savedItem.title, item.title)
            
            self.assertIsNotNone(savedItem.data_ref)
            self.assertEqual(savedItem.data_ref.url_raw, helpers.to_db_format(self.dstRelPath))
            self.assertTrue(os.path.exists(os.path.join(self.repo.base_path, 
                                                        savedItem.data_ref.url)))
            
            histRec = UnitOfWork._find_item_latest_history_rec(uow.session, savedItem)
            self.assertIsNotNone(histRec)
            self.assertEqual(histRec.operation, HistoryRec.CREATE)
            self.assertEqual(histRec.user_login, savedItem.user_login)
            self.assertIsNone(histRec.parent1_id)
            self.assertIsNone(histRec.parent2_id)
        finally:
            uow.close()
            
    def test_saveNewItemWithACopyOfAStoredFileInRepo(self):
        '''
        User wants to add a copy of a stored file from the repo into the same repo 
        but to the another location. The copy of the original file will be attached 
        to the new Item object.
        '''
        item = Item("user", "Item's title")
        self.srcAbsPath = os.path.abspath(os.path.join(
            self.repo.base_path, "lyrics", "led_zeppelin", "stairway_to_heaven.txt"))
        self.dstRelPath = os.path.join("dir1", "dir2", "dir3", "copy_of_stairway_to_heaven.txt")
        try:
            uow = self.repo.create_unit_of_work()
            self.savedItemId = uow.saveNewItem(item, self.srcAbsPath, self.dstRelPath)
        finally:
            uow.close()
            
        try:
            uow = self.repo.create_unit_of_work()
            savedItem = uow.getExpungedItem(self.savedItemId)
            self.assertEqual(savedItem.title, item.title)
            
            self.assertIsNotNone(savedItem.data_ref)
            self.assertEqual(savedItem.data_ref.url_raw, helpers.to_db_format(self.dstRelPath))
            self.assertTrue(os.path.exists(os.path.join(self.repo.base_path, 
                                                        savedItem.data_ref.url)))
            
            histRec = UnitOfWork._find_item_latest_history_rec(uow.session, savedItem)
            self.assertIsNotNone(histRec)
            self.assertEqual(histRec.operation, HistoryRec.CREATE)
            self.assertEqual(histRec.user_login, savedItem.user_login)
            self.assertIsNone(histRec.parent1_id)
            self.assertIsNone(histRec.parent2_id)
            
            self.assertTrue(os.path.exists(self.srcAbsPath))
        finally:
            uow.close()
            
    def test_saveNewItemWithTags(self):
        userLogin = "user"
        item = Item(userLogin, "Item with tags")
        
        tagNameThatExistsInRepo = "Lyrics"
        tagNameNew = "No items in test repo with such Tag!"
        
        item.add_tag(tagNameThatExistsInRepo, userLogin)
        item.add_tag(tagNameNew, userLogin)
        
        try:
            uow = self.repo.create_unit_of_work()
            savedItemId = uow.saveNewItem(item)
        finally:
            uow.close()
            
        savedItem = self.getExistingItem(savedItemId)
        self.assertEqual(savedItem.title, item.title)
        self.assertTrue(savedItem.has_tag(tagNameThatExistsInRepo))
        self.assertTrue(savedItem.has_tag(tagNameNew))
        self.assertEqual(len(savedItem.item_tags), 2)
        
        histRec = self.getItemsMostRecentHistoryRec(savedItem)
        self.assertIsNotNone(histRec)
        self.assertEqual(histRec.operation, HistoryRec.CREATE)
        self.assertEqual(histRec.user_login, savedItem.user_login)
        self.assertIsNone(histRec.parent1_id)
        self.assertIsNone(histRec.parent2_id)
        
    def test_saveNewItemWithFields(self):
        userLogin = "user"
        item = Item(userLogin, "Item with fields")
        
        fieldOne = ("Year", 2012)
        fieldTwo = ("No items in test repo with such Field!", "Some value")
        
        item.set_field_value(fieldOne[0], fieldOne[1], userLogin)
        item.set_field_value(fieldTwo[0], fieldTwo[1], userLogin)
        
        try:
            uow = self.repo.create_unit_of_work()
            savedItemId = uow.saveNewItem(item)
        finally:
            uow.close()
            
        savedItem = self.getExistingItem(savedItemId)
        self.assertEqual(savedItem.title, item.title)
        self.assertTrue(savedItem.has_field(fieldOne[0], fieldOne[1]))
        self.assertTrue(savedItem.has_field(fieldTwo[0], fieldTwo[1]))
        self.assertEqual(len(savedItem.item_fields), 2)
        
        histRec = self.getItemsMostRecentHistoryRec(savedItem)
        self.assertIsNotNone(histRec)
        self.assertEqual(histRec.operation, HistoryRec.CREATE)
        self.assertEqual(histRec.user_login, savedItem.user_login)
        self.assertIsNone(histRec.parent1_id)
        self.assertIsNone(histRec.parent2_id)
        
        
    

class DeleteItemTest(AbstractTestCaseWithRepo):
    def test_deleteExistingItemWithExistingPhysicalFileByOwner(self):
        userThatDeletesItem = itemWithFile.ownerUserLogin
        try:
            uow = self.repo.create_unit_of_work()
            itemBeforeDelete = uow.getExpungedItem(itemWithFile.id)
            uow.deleteItem(itemWithFile.id, 
                        userThatDeletesItem, 
                        delete_physical_file=True)
        finally:
            uow.close()
        
        try:
            uow = self.repo.create_unit_of_work()
            deletedItem = uow.getExpungedItem(itemWithFile.id)
            self.assertFalse(deletedItem.alive)
            self.assertIsNone(deletedItem.data_ref)
            
            #NOTE that tags/fields collections are not cleared, as you might expect
            self.assertTrue(len(deletedItem.item_tags) >= 0)
            self.assertTrue(len(deletedItem.item_fields) >= 0)
            
            histRec = UnitOfWork._find_item_latest_history_rec(uow.session, itemBeforeDelete)
            self.assertIsNotNone(histRec)
            self.assertEqual(histRec.operation, HistoryRec.DELETE)
            self.assertEqual(histRec.user_login, userThatDeletesItem)
            self.assertIsNotNone(histRec.parent1_id)
            self.assertIsNone(histRec.parent2_id)
            #Should we test any other conditions?
            
        finally:
            uow.close()
        self.assertFalse(os.path.exists(os.path.join(COPY_OF_TEST_REPO_BASE_PATH, itemWithFile.relFilePath)))
        





class UpdateItemTest(AbstractTestCaseWithRepo):
    
    def test_updateItemTitleByOwner(self):
        item = self.getExistingItem(itemWithFile.id)
        self.assertEqual(item.title, itemWithFile.title)
            
        historyRecBefore = self.getItemsMostRecentHistoryRec(item)
            
        #Change item's title
        newItemTitle = "ABCDEF"
        self.assertNotEqual(item.title, newItemTitle, 
                            "You should change item's title to some different value.") 
        item.title = newItemTitle
            
        #Save changes to the repo
        try:
            uow = self.repo.create_unit_of_work()
            uow.updateExistingItem(item, item.user_login)
        finally:
            uow.close()
            
        #Get an item from repo again and check it's title
        item = self.getExistingItem(itemWithFile.id)
        self.assertEqual(item.title, newItemTitle)
        
        historyRecAfter = self.getItemsMostRecentHistoryRec(item)
        self.assertNotEqual(historyRecBefore.item_hash, historyRecAfter.item_hash)
        self.assertEqual(historyRecBefore.item_id, historyRecAfter.item_id)
        self.assertEqual(historyRecBefore.item_id, item.id)
        self.assertEqual(historyRecBefore.data_ref_hash, historyRecAfter.data_ref_hash)
        self.assertEqual(historyRecBefore.data_ref_url, historyRecAfter.data_ref_url)
        self.assertEqual(historyRecAfter.parent1_id, historyRecBefore.id)
        self.assertGreater(historyRecAfter.id, historyRecBefore.id)
        self.assertIsNone(historyRecAfter.parent2_id)
        self.assertEqual(historyRecAfter.operation, "UPDATE")
        self.assertEqual(historyRecAfter.user_login, "user")
        
        

    def test_updateItemTagsByOwner(self):
        userLogin = "user"
        item = self.getExistingItem(itemWithTagsAndFields.id)
        self.assertEqual(item.title, itemWithTagsAndFields.title)
        self.assertEqual(len(item.item_tags), len(itemWithTagsAndFields.tags))
        self.assertEqual(len(itemWithTagsAndFields.tags), 2)
        
        historyRecBefore = self.getItemsMostRecentHistoryRec(item)
        
        #Remove one existing tag
        tagNameToRemove = "RHCP"
        self.assertTrue(item.has_tag(tagNameToRemove))
        self.assertTrue(item.remove_tag(tagNameToRemove))
        
        #Add one new tag
        tagNameToAdd = "TagNameToAdd"
        self.assertNotEqual(tagNameToRemove, tagNameToAdd)
        self.assertFalse(item.has_tag(tagNameToAdd))
        item.add_tag(tagNameToAdd, userLogin)
        
        #Save changes to the repo
        try:
            uow = self.repo.create_unit_of_work()
            uow.updateExistingItem(item, item.user_login)
        finally:
            uow.close()
        
        item = self.getExistingItem(itemWithTagsAndFields.id)
        self.assertFalse(item.has_tag(tagNameToRemove))
        self.assertTrue(item.has_tag(tagNameToAdd))
        self.assertTrue(item.has_tag("Lyrics"))
        self.assertEqual(len(item.item_tags), 2)
               
        historyRecAfter = self.getItemsMostRecentHistoryRec(item)
        self.assertNotEqual(historyRecBefore.item_hash, historyRecAfter.item_hash)
        self.assertEqual(historyRecBefore.item_id, historyRecAfter.item_id)
        self.assertEqual(historyRecBefore.item_id, item.id)
        self.assertEqual(historyRecBefore.data_ref_hash, historyRecAfter.data_ref_hash)
        self.assertEqual(historyRecBefore.data_ref_url, historyRecAfter.data_ref_url)
        self.assertEqual(historyRecAfter.parent1_id, historyRecBefore.id)
        self.assertGreater(historyRecAfter.id, historyRecBefore.id)
        self.assertIsNone(historyRecAfter.parent2_id)
        self.assertEqual(historyRecAfter.operation, "UPDATE")
        self.assertEqual(historyRecAfter.user_login, "user")
        
        
    def test_updateItemFieldsByOwner(self):
        userLogin = itemWithTagsAndFields.ownerUserLogin
        
        item = self.getExistingItem(itemWithTagsAndFields.id)
        self.assertEqual(item.title, itemWithTagsAndFields.title)
        self.assertEqual(len(item.item_fields), len(itemWithTagsAndFields.fields))
        self.assertEqual(len(itemWithTagsAndFields.fields), 4)
        
        historyRecBefore = self.getItemsMostRecentHistoryRec(item)
        
        #Remove one existing field
        fieldNameToRemove = "Year"
        self.assertTrue(item.has_field(fieldNameToRemove, 1991))
        self.assertTrue(item.remove_field(fieldNameToRemove))
        
        #Add one new field
        fieldToAdd = ("FieldNameToAdd", "Some value")
        self.assertFalse(item.has_field(fieldToAdd[0]))
        item.set_field_value(fieldToAdd[0], fieldToAdd[1], userLogin)
        
        #Edit one existing field
        fieldToEdit = ("Notes", "Some new notes")
        self.assertTrue(item.has_field(fieldToEdit[0]))
        self.assertFalse(item.has_field(fieldToEdit[0], fieldToEdit[1]))
        item.set_field_value(fieldToEdit[0], fieldToEdit[1], userLogin)
        
        #Save changes to the repo
        try:
            uow = self.repo.create_unit_of_work()
            uow.updateExistingItem(item, item.user_login)
        finally:
            uow.close()
        
        item = self.getExistingItem(itemWithTagsAndFields.id)
        self.assertFalse(item.has_field(fieldNameToRemove))
        self.assertTrue(item.has_field(fieldToAdd[0], fieldToAdd[1]))
        self.assertTrue(item.has_field(fieldToEdit[0], fieldToEdit[1]))
        self.assertTrue(item.has_field("Rating", 5))
        self.assertTrue(item.has_field("Albom", "Blood Sugar Sex Magik"))
        self.assertEqual(len(item.item_fields), 4)
               
        historyRecAfter = self.getItemsMostRecentHistoryRec(item)
        self.assertNotEqual(historyRecBefore.item_hash, historyRecAfter.item_hash)
        self.assertEqual(historyRecBefore.item_id, historyRecAfter.item_id)
        self.assertEqual(historyRecBefore.item_id, item.id)
        self.assertEqual(historyRecBefore.data_ref_hash, historyRecAfter.data_ref_hash)
        self.assertEqual(historyRecBefore.data_ref_url, historyRecAfter.data_ref_url)
        self.assertEqual(historyRecAfter.parent1_id, historyRecBefore.id)
        self.assertGreater(historyRecAfter.id, historyRecBefore.id)
        self.assertIsNone(historyRecAfter.parent2_id)
        self.assertEqual(historyRecAfter.operation, "UPDATE")
        self.assertEqual(historyRecAfter.user_login, "user")

    def test_addFileToItemWithoutFile(self):
        #TODO: Add HistoryRec checking
        
        # Referenced file for new DataRef will be from the outside of the repo
        item = self.getExistingItem(itemWithoutFile.id)
        self.assertEqual(item.title, itemWithoutFile.title)
        self.assertIsNone(item.data_ref)
        self.assertFalse(os.path.exists(os.path.join(self.repo.base_path, "file.txt")))
        
        # Link file with the item
        srcAbsPath = os.path.abspath(os.path.join(self.repo.base_path, "..", "tmp", "file.txt"))
        item.data_ref = DataRef(DataRef.FILE, srcAbsPath)
        
        # Save changes to the repo
        try:
            uow = self.repo.create_unit_of_work()
            uow.updateExistingItem(item, item.user_login)
        finally:
            uow.close()
            
        item = self.getExistingItem(itemWithoutFile.id)
        self.assertEqual(item.title, itemWithoutFile.title)
        self.assertIsNotNone(item.data_ref)
        self.assertEqual(item.data_ref.url, "file.txt")
        self.assertTrue(os.path.exists(os.path.join(self.repo.base_path, "file.txt")))
        
        
    def test_addFileToItemWithoutFileWithDestinationInsideRepo(self):
        #TODO: Add HistoryRec checking
        
        # Referenced file for new DataRef will be from the outside of the repo
        # We will specify the destination path in the repo - where to put the file
        
        item = self.getExistingItem(itemWithoutFile.id)
        self.assertEqual(item.title, itemWithoutFile.title)
        self.assertIsNone(item.data_ref)
        self.assertFalse(os.path.exists(os.path.join(self.repo.base_path, "dir1", "dir2", "file.txt")))
        
        # Link file with the item
        srcAbsPath = os.path.abspath(os.path.join(self.repo.base_path, "..", "tmp", "file.txt"))
        item.data_ref = DataRef(DataRef.FILE, srcAbsPath)
        item.data_ref.dstRelPath = os.path.join("dir1", "dir2", "copied_file.txt")
        
        # Save changes to the repo
        try:
            uow = self.repo.create_unit_of_work()
            uow.updateExistingItem(item, item.user_login)
        finally:
            uow.close()
            
        item = self.getExistingItem(itemWithoutFile.id)
        self.assertEqual(item.title, itemWithoutFile.title)
        self.assertIsNotNone(item.data_ref)
        self.assertEqual(item.data_ref.url, "dir1/dir2/copied_file.txt")
        self.assertTrue(os.path.exists(os.path.join(self.repo.base_path, "dir1", "dir2", "copied_file.txt")))
        self.assertFalse(os.path.isdir(os.path.join(self.repo.base_path, "dir1", "dir2", "copied_file.txt")))
    
    
    def test_moveFileOfItemToAnotherLocationWithinRepo(self):
        item = self.getExistingItem(itemWithTagsAndFields.id)
        self.assertEqual(item.title, itemWithTagsAndFields.title)
        self.assertIsNotNone(item.data_ref)
        self.assertTrue(os.path.exists(os.path.join(self.repo.base_path, item.data_ref.url)))
        
        # Move linked file to another location within the repository
        path = ["new", "location", "for", "file", "I Could Have Lied.txt"]
        item.data_ref.dstRelPath = os.path.join(*path)
        
        # Save changes to the repo
        try:
            uow = self.repo.create_unit_of_work()
            uow.updateExistingItem(item, item.user_login)
        finally:
            uow.close()
            
        item = self.getExistingItem(itemWithTagsAndFields.id)
        self.assertEqual(item.title, itemWithTagsAndFields.title)
        self.assertIsNotNone(item.data_ref)
        self.assertEqual(item.data_ref.url, "new/location/for/file/I Could Have Lied.txt")
        self.assertFalse(os.path.isdir(os.path.join(self.repo.base_path, *path)))
        self.assertTrue(os.path.exists(os.path.join(self.repo.base_path, *path)))
    
    def test_moveFileOfItemToAnotherLocationWithinRepoAndRename(self):
        item = self.getExistingItem(itemWithTagsAndFields.id)
        self.assertEqual(item.title, itemWithTagsAndFields.title)
        self.assertIsNotNone(item.data_ref)
        self.assertTrue(os.path.exists(os.path.join(self.repo.base_path, item.data_ref.url)))
        
        # Move linked file to another location within the repository
        # NOTE: File will be not only moved, but also renamed
        path = ["new", "location", "for", "file", "could_have_lied_lyrics.txt"]
        item.data_ref.dstRelPath = os.path.join(*path)
        
        # Save changes to the repo
        try:
            uow = self.repo.create_unit_of_work()
            uow.updateExistingItem(item, item.user_login)
        finally:
            uow.close()
            
        item = self.getExistingItem(itemWithTagsAndFields.id)
        self.assertEqual(item.title, itemWithTagsAndFields.title)
        self.assertIsNotNone(item.data_ref)
        self.assertEqual(item.data_ref.url, "new/location/for/file/could_have_lied_lyrics.txt")
        self.assertFalse(os.path.isdir(os.path.join(self.repo.base_path, *path)))
        self.assertTrue(os.path.exists(os.path.join(self.repo.base_path, *path)))
    
    def test_removeFileFromItem(self):
        item = self.getExistingItem(itemWithTagsAndFields.id)
        self.assertEqual(item.title, itemWithTagsAndFields.title)
        self.assertIsNotNone(item.data_ref)
        self.assertTrue(os.path.exists(os.path.join(self.repo.base_path, item.data_ref.url)))
        
        item.data_ref = None
        
        # Save changes to the repo
        try:
            uow = self.repo.create_unit_of_work()
            uow.updateExistingItem(item, item.user_login)
        finally:
            uow.close()
        
            
        item = self.getExistingItem(itemWithTagsAndFields.id)
        self.assertEqual(item.title, itemWithTagsAndFields.title)
        self.assertIsNone(item.data_ref)
        
        # Physical file should not be deleted
        self.assertTrue(os.path.exists(os.path.join(self.repo.base_path, itemWithTagsAndFields.relFilePath)))
        
        #DataRef should not be deleted after this operation
        dataRef = self.getDataRef(itemWithTagsAndFields.relFilePath)
        self.assertIsNotNone(dataRef)
        

    def test_replaceFileOfItemWithAnotherOuterFile(self):
        #TODO implement test. Referenced file for new DataRef will be from the outside of the repo
        pass
    
    def test_replaceFileOfItemWithAnotherInnerFile(self):
        #TODO implement test. Referenced file for new DataRef will be from the same repo
        # But new file will not be a stored file (has no corresponding DataRef object)
        pass
    
    def test_replaceFileOfItemWithAnotherInnerStoredFile(self):
        #TODO implement test. Referenced file for new DataRef will be from the same repo
        pass

    
    
        
    def test_addTagsToItemByNotOwnerUser(self):
        #TODO implement test
        pass
    
    def test_removeTagsFromItemByNotOwnerUser(self):
        #TODO implement test
        pass
    
    
    

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()