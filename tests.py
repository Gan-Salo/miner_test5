import unittest
from unittest.mock import patch
from main import Miner
import tkinter as tk
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

    def test_mines_placement(self):
        rows, cols, mines = 10, 10, 20
        miner = Miner(rows, cols, mines)
        board = [['0' for _ in range(cols)] for _ in range(rows)]
        miner.place_mines(board, mines)
        actual_mines_count = sum(row.count('M') for row in board)
        self.assertEqual(actual_mines_count, mines, "Количество расставленных мин не совпадает с инициализированным количеством.")

    def test_main_window_initialization(self):
        app = Miner()
        self.assertIsInstance(app.root, tk.Tk, "Окно должно быть экземпляром Tk")
        self.assertEqual(app.root.title(), "Сапёр", "Заголовок окна должен быть 'Сапёр'")
        self.assertFalse(app.root.resizable()[0], "Окно не должно быть изменяемым по горизонтали")
        self.assertFalse(app.root.resizable()[1], "Окно не должно быть изменяемым по вертикали")

if __name__ == '__main__':
    unittest.main()