import unittest
from unittest.mock import patch
from main import Miner
import unittest

class TestMinesweeper(unittest.TestCase):
    def testMinerClassCreation(self):
        miner = Miner()
        self.assertIsNotNone(miner)
    def test_initial_attributes(self):
        rows, cols, mines = 10, 10, 20
        miner = Miner(rows, cols, mines)
        self.assertEqual(miner.rows, rows)
        self.assertEqual(miner.cols, cols)
        self.assertEqual(miner.mines, mines)

    def test_empty_board_initialization(self):
        rows, cols, mines = 10, 10, 0
        miner = Miner(rows, cols, mines)
        self.assertEqual(sum(row.count('M') for row in miner.board), 0)

if __name__ == '__main__':
    unittest.main()