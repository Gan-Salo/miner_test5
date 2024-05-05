import unittest
from unittest.mock import patch
from main import Miner
import tkinter as tk
import unittest

class TestMiner(unittest.TestCase):
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
        self.assertEqual(sum(row.count('*') for row in miner.board), 0)

    def test_mines_quantity(self):
        rows, cols, mines = 10, 10, 20
        start_row, start_col = 0, 0
        miner = Miner(rows, cols, mines)
        miner.on_button_click(start_row, start_col)
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

    def test_mines_not_placed_before_first_click(self):
        rows, cols, mines = 10, 10, 20
        miner = Miner(rows, cols, mines)
        self.assertEqual(len(miner.mine_positions), 0, "Должно быть 0 мин до первого клика")

    def test_no_mine_on_first_click_location(self):
        rows, cols, mines = 10, 10, 20
        miner = Miner(rows, cols, mines)
        self.assertNotIn((rows, cols), miner.mine_positions,
                         "При первом клике не должно быть мины")

    def test_first_click_flag_cleared(self):
        rows, cols, mines = 10, 10, 20
        start_row, start_col = 0, 0
        miner = Miner(rows, cols, mines)
        miner.on_button_click(start_row, start_col)
        self.assertFalse(miner.first_click, "Флаг первого клика должен быть изменен")

    def test_no_mines_around(self):
        rows, cols, mines = 3, 3, 0
        miner = Miner(rows, cols, mines)
        miner.mine_positions = set()
        count = miner.count_mines_around(1, 1)
        self.assertEqual(count, 0, "Вокруг должно быть 0 мин")

    def test_all_mines_around(self):
        rows, cols, mines = 3, 3, 0
        miner = Miner(rows, cols, mines)
        miner.mine_positions = {(0, 0), (0, 1), (0, 2), (1, 0), (1, 2), (2, 0), (2, 1), (2, 2)}
        count = miner.count_mines_around(1, 1)
        self.assertEqual(count, 8, "Вокруг должно быть 8 мин")

    def test_some_mines_around(self):
        rows, cols, mines = 3, 3, 0
        miner = Miner(rows, cols, mines)
        miner.mine_positions = {(0, 0), (1, 2), (2, 2)}
        count = miner.count_mines_around(1, 1)
        self.assertEqual(count, 3, "Вокруг должно быть 3 мины")

    def test_no_mines_corner(self):
        rows, cols, mines = 3, 3, 0
        miner = Miner(rows, cols, mines)
        miner.mine_positions = {(1, 1), (2, 2)}
        count = miner.count_mines_around(0, 0)
        self.assertEqual(count, 1, "Вокруг должна быть 1 мина")

    def test_reveal_space_already_opened(self):
        miner = Miner(10, 10, 20)
        miner.opened.add((0, 0))
        with patch.object(tk.Button, 'config') as mocked_button:
            miner.reveal_space(0, 0)
            mocked_button.assert_not_called()

    def test_flag_placement(self):
        miner = Miner(10, 10, 20)
        miner.on_right_click(0, 0)
        self.assertIn((0, 0), miner.flags)
        self.assertEqual(miner.buttons[(0, 0)]['text'], 'F')

    def test_flag_remove(self):
        miner = Miner(10, 10, 20)
        miner.flags.add((0, 0))
        miner.buttons[(0, 0)]['text'] = 'F'
        miner.on_right_click(0, 0)
        self.assertNotIn((0, 0), miner.flags)
        self.assertEqual(miner.buttons[(0, 0)]['text'], ' ')

    def test_no_flag_for_opened_cell(self):
        miner = Miner(10, 10, 20)
        miner.opened.add((0, 0))
        flags_count = len(miner.flags)
        miner.on_right_click(0, 0)
        self.assertEqual(len(miner.flags), flags_count)

    def test_win_condition(self):
        miner = Miner(3, 3, 1)
        miner.mine_positions = {(0, 0)}
        for row in range(3):
            for col in range(3):
                if (row, col) != (0, 0):
                    miner.opened.add((row, col))
        with patch('tkinter.messagebox.showinfo') as mock_showinfo:
            miner.check_win()
            mock_showinfo.assert_called_once_with("Игра окончена", "Вы выиграли!")

    def test_not_win_condition(self):
        miner = Miner(3, 3, 1)
        miner.mine_positions = {(0, 0)}
        miner.opened.add((0, 1))
        with patch('tkinter.messagebox.showinfo') as mock_showinfo:
            miner.check_win()
            mock_showinfo.assert_not_called()

    def test_lose_conditions(self):
        miner = Miner(3, 3, 1)
        miner.mine_positions = {(0, 0)}
        with patch('tkinter.messagebox.showinfo') as mock_showinfo:
            miner.on_button_click(0, 0)
            mock_showinfo.assert_called_once_with("Игра окончена", "Вы наткнулись на мину!")


if __name__ == '__main__':
    unittest.main()