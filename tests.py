import unittest
from unittest.mock import patch
from main import Miner
import unittest

class TestMinesweeper(unittest.TestCase):
    def testMinerClassCreation(self):
        miner = Miner()
        self.assertIsNotNone(miner)

if __name__ == '__main__':
    unittest.main()