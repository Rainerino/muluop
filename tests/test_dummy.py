import unittest


class TestDummy(unittest.TestCase):
    
    def test_basic(self):
        self.assertEqual(1 + 1, 2)
    
    def test_string(self):
        self.assertTrue("hello" == "hello")
    
    def test_list(self):
        items = [1, 2, 3]
        self.assertEqual(len(items), 3)

