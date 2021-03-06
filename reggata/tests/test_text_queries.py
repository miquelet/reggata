from reggata.tests.abstract_test_cases import AbstractTestCaseWithRepo
from reggata.data.commands import QueryItemsByParseTree
from reggata.parsers.query_parser import parser


# NOTE: This list contains tuples (query, expectedItemIds)
testsData = [
    ("Txt AND Lyrics", [14, 15]),
    ("Txt And Lyrics", [14, 15]),
    ("Txt and Lyrics", [14, 15]),
    ("Txt aND Lyrics", []), # 'aND' is interpreted as a name of a tag
    ("Txt Lyrics", [14, 15]), # AND operator is optional 
    ("Tabs AND Error AND RHCP", [9]),
    
    ("Lyrics AND NOT RHCP", [4, 10]),
    
    ("Rating > 2", [5, 13, 14, 15]),
    ("(Txt AND Lyrics) AND (Rating > 0)", [14, 15]),
    ("(Txt AND Lyrics) AND (Rating > 3)", [14]),
    
    ("ALL", [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]),
    ("All", [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]),
    ("all", [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]),
    ("aLL", []),
    ('''"ALL"''', []),
    
    # TODO: Add more test cases here...
]


def create_test_func(query, expectedItemIds):
    
    def _test_func(self):
        try:
            uow = self.repo.createUnitOfWork()
            queryTree = parser.parse(query)
            cmd = QueryItemsByParseTree(queryTree)
            items = uow.executeCommand(cmd)
            actualItemIds = [item.id for item in items]
            actualItemIds.sort()
            expectedItemIds.sort()
            self.assertEqual(actualItemIds, expectedItemIds, "Query: {}".format(query))
        finally:
            uow.close()
            
    return _test_func


class QueriesTests(AbstractTestCaseWithRepo):
    # NOTE: Test functions will be added to this class dynamically
    pass


# This for cycle dynamically adds test functions to test case class QueriesTests
for i, (query, expectedItemIds) in enumerate(testsData):
    setattr(QueriesTests, 'test_{}'.format(i), create_test_func(query, expectedItemIds))




    