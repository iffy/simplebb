from twisted.trial.unittest import TestCase

from simplebb.util import generateId



class generateIdTest(TestCase):    


    def test_different(self):
        """
        Each one should be different
        """
        a = generateId()
        b = generateId()
        self.assertNotEqual(a, b)


    def test_string(self):
        """
        Should be a string
        """
        a = generateId()
        self.assertEqual(type(a), str)


    def test_timeComponent(self):
        """
        There should be a time component
        """
        import random
        import time
        random.seed(10)
        a = generateId()
        time.sleep(0.1)
        random.seed(10)
        b = generateId()
        self.assertNotEqual(a, b)
    
    
    def test_increment(self):
        """
        There should be an incrementing component
        """
        import random
        random.seed(6)
        a = generateId()
        random.seed(6)
        b = generateId()
        self.assertNotEqual(a, b)


