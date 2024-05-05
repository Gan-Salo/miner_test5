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

    def test_mines_quantity(self):
        rows, cols, mines = 10, 10, 20
        miner = Miner(rows, cols, mines)
        self.assertEqual(len(miner.mine_positions), mines, "Количество размещенных мин не совпадает с инициализированным количеством.")

    def test_mines_within_bounds(self):
        rows, cols, mines = 10, 10, 20
        miner = Miner(rows, cols, mines)
        all_within_bounds = all(0 <= r < rows and 0 <= c < cols for r, c in miner.mine_positions)
        self.assertTrue(all_within_bounds, "Все мины должны находиться в пределах доски.")

    def test_main_window_initialization(self):
        app = Miner()
        self.assertIsInstance(app.root, tk.Tk, "Окно должно быть экземпляром Tk")
        self.assertEqual(app.root.title(), "Сапёр", "Заголовок окна должен быть 'Сапёр'")
        self.assertFalse(app.root.resizable()[0], "Окно не должно быть изменяемым по горизонтали")
        self.assertFalse(app.root.resizable()[1], "Окно не должно быть изменяемым по вертикали")

    def test_win_buttons_creation(self):
        app = Miner(10, 10, 20)
        app.initialize_board()
        button_count = sum(isinstance(widget, tk.Button) for widget in app.root.children.values())
        self.assertEqual(button_count, 100, "Должно быть 100 кнопок на поле 10x10")

if __name__ == '__main__':
    unittest.main()