import unittest
# from google.appengine.api import memcache
from google.appengine.ext import db
from google.appengine.ext import testbed


class TestModel(db.Model):
    """A model class used for testing."""
    number = db.IntegerProperty(default=42)
    text = db.StringProperty()


class TestEntityGroupRoot(db.Model):
    """Entity group root"""
    pass


class DemoTestCase(unittest.TestCase):

    def setUp(self):
        # First, create an instance of the Testbed class.
        self.testbed = testbed.Testbed()
        # Then activate the testbed, which prepares the service stubs for use.
        self.testbed.activate()
        # Next, declare which service stubs you want to use.
        self.testbed.init_datastore_v3_stub()

    def tearDown(self):
        self.testbed.deactivate()

    def testInsertEntity(self):
        TestModel().put()
        self.assertEqual(1, len(TestModel.all().fetch(2)))

    def testFilterByNumber(self):
        root = TestEntityGroupRoot(key_name="root")
        TestModel(parent=root.key()).put()
        TestModel(number=17, parent=root.key()).put()
        query = TestModel.all().ancestor(root.key()).filter('number =', 42)
        results = query.fetch(2)
        self.assertEqual(1, len(results))
        self.assertEqual(42, results[0].number)


if __name__ == '__main__':
    unittest.main()
