import unittest
import tkinter as tk
from unittest.mock import patch, MagicMock
import sys
import os

# Добавляем родительскую директорию в пути для импорта
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Импортируем класс Miner из основного файла
from minesweeper import Miner


class TestMinerInitialization(unittest.TestCase):
    """Тесты для проверки инициализации игры"""

    def setUp(self):
        # Создаем фиктивный главный объект tkinter
        self.root_patcher = patch('tkinter.Tk')
        self.mock_tk = self.root_patcher.start()
        # Заглушка для messagebox
        self.msg_patcher = patch('tkinter.messagebox')
        self.mock_msg = self.msg_patcher.start()

    def tearDown(self):
        self.root_patcher.stop()
        self.msg_patcher.stop()

    def test_default_initialization(self):
        """Проверка значений по умолчанию"""
        miner = Miner()
        self.assertEqual(miner.rows, 8)
        self.assertEqual(miner.cols, 8)
        self.assertEqual(miner.mines, 10)
        self.assertEqual(len(miner.board), 8)
        self.assertEqual(len(miner.board[0]), 8)
        self.assertTrue(miner.first_click)
        self.assertTrue(miner.game_active)
        self.assertEqual(len(miner.opened), 0)
        self.assertEqual(len(miner.flags), 0)
        self.assertEqual(len(miner.mine_positions), 0)

    def test_custom_initialization(self):
        """Проверка пользовательских настроек"""
        miner = Miner(rows=10, cols=12, mines=15)
        self.assertEqual(miner.rows, 10)
        self.assertEqual(miner.cols, 12)
        self.assertEqual(miner.mines, 15)
        self.assertEqual(len(miner.board), 10)
        self.assertEqual(len(miner.board[0]), 12)

    def test_too_many_mines(self):
        """Проверка на исключение при слишком большом количестве мин"""
        with self.assertRaises(ValueError):
            Miner(rows=5, cols=5, mines=25)  # равно количеству клеток

        with self.assertRaises(ValueError):
            Miner(rows=5, cols=5, mines=30)  # больше количества клеток


class TestMinerGameLogic(unittest.TestCase):
    """Тесты для проверки игровой логики"""

    def setUp(self):
        # Создаем фиктивный главный объект tkinter и другие необходимые патчи
        self.root_patcher = patch('tkinter.Tk')
        self.mock_tk = self.root_patcher.start()
        self.msg_patcher = patch('tkinter.messagebox')
        self.mock_msg = self.msg_patcher.start()

        # Создаем экземпляр игры с известными параметрами
        self.miner = Miner(rows=5, cols=5, mines=5)

        # Создаем фиктивные кнопки
        self.miner.buttons = {}
        for r in range(5):
            for c in range(5):
                mock_button = MagicMock()
                self.miner.buttons[(r, c)] = mock_button

    def tearDown(self):
        self.root_patcher.stop()
        self.msg_patcher.stop()

    def test_place_mines(self):
        """Проверка размещения мин"""
        # Размещаем мины (первый клик в центре)
        self.miner.place_mines(2, 2)

        # Проверяем, что мины размещены
        self.assertEqual(len(self.miner.mine_positions), 5)

        # Проверяем, что мины не размещены вокруг первого клика
        protected = {(2 + dx, 2 + dy) for dx in [-1, 0, 1] for dy in [-1, 0, 1]}
        for mine_pos in self.miner.mine_positions:
            self.assertNotIn(mine_pos, protected)

    def test_count_mines_around(self):
        """Проверка подсчета мин вокруг клетки"""
        # Устанавливаем известные позиции мин
        self.miner.mine_positions = {(0, 0), (0, 1), (1, 0)}

        # Проверяем количество мин вокруг различных клеток
        self.assertEqual(self.miner.count_mines_around(0, 0), 2)  # Сама мина не считается
        self.assertEqual(self.miner.count_mines_around(1, 1), 3)
        self.assertEqual(self.miner.count_mines_around(2, 2), 0)
        self.assertEqual(self.miner.count_mines_around(0, 2), 1)

    def test_reveal_space(self):
        """Проверка открытия клетки"""
        # Устанавливаем известные позиции мин
        self.miner.mine_positions = {(0, 0), (0, 1), (1, 0)}

        # Открываем клетку с цифрой 3
        self.miner.reveal_space(1, 1)

        # Проверяем, что клетка добавлена в открытые
        self.assertIn((1, 1), self.miner.opened)

        # Проверяем, что была вызвана конфигурация кнопки с текстом "3"
        button = self.miner.buttons[(1, 1)]
        button.config.assert_called_with(text="3", bg='lightgrey', fg='red')

    def test_reveal_empty_space(self):
        """Проверка открытия пустой клетки (рекурсивное открытие)"""
        # Устанавливаем известные позиции мин далеко от тестируемой области
        self.miner.mine_positions = {(4, 4), (4, 3), (3, 4)}

        # Открываем пустую клетку
        self.miner.reveal_space(0, 0)

        # Должно открыться несколько клеток из-за рекурсии
        self.assertGreater(len(self.miner.opened), 1)

        # Проверяем, что была вызвана конфигурация кнопки без текста
        button = self.miner.buttons[(0, 0)]
        button.config.assert_called_with(text=" ", bg='lightgrey')

    def test_on_right_click(self):
        """Проверка установки и снятия флага"""
        # Проверяем установку флага
        self.miner.on_right_click(1, 1)
        self.assertIn((1, 1), self.miner.flags)
        button = self.miner.buttons[(1, 1)]
        button.config.assert_called_with(text='F', fg='red')

        # Проверяем снятие флага
        self.miner.on_right_click(1, 1)
        self.assertNotIn((1, 1), self.miner.flags)
        button.config.assert_called_with(text=' ')

    def test_on_button_click_first_click(self):
        """Проверка первого нажатия на кнопку"""
        # Патчим метод reveal_space
        with patch.object(self.miner, 'reveal_space') as mock_reveal:
            with patch.object(self.miner, 'place_mines') as mock_place_mines:
                # Симулируем первый клик
                self.miner.on_button_click(2, 2)

                # Проверяем, что мины были размещены
                mock_place_mines.assert_called_once_with(2, 2)

                # Проверяем, что первый клик больше не активен
                self.assertFalse(self.miner.first_click)

                # Проверяем, что таймер был запущен
                self.assertTrue(self.miner.timer_running)

                # Проверяем, что метод reveal_space был вызван
                mock_reveal.assert_called_once_with(2, 2)

    def test_on_button_click_mine(self):
        """Проверка нажатия на мину"""
        # Устанавливаем мину на известную позицию
        self.miner.mine_positions = {(2, 2)}
        self.miner.first_click = False  # Имитируем, что первый клик уже был

        # Патчим метод game_over
        with patch.object(self.miner, 'game_over') as mock_game_over:
            # Симулируем клик на мину
            self.miner.on_button_click(2, 2)

            # Проверяем, что game_over был вызван с параметром False (проигрыш)
            mock_game_over.assert_called_once_with(False)

    def test_check_win(self):
        """Проверка определения выигрыша"""
        # Устанавливаем 5 мин на известные позиции
        self.miner.mine_positions = {(0, 0), (0, 1), (1, 0), (2, 2), (4, 4)}

        # Открываем все клетки, кроме клеток с минами
        for r in range(5):
            for c in range(5):
                if (r, c) not in self.miner.mine_positions:
                    self.miner.opened.add((r, c))

        # Патчим метод game_over
        with patch.object(self.miner, 'game_over') as mock_game_over:
            # Проверяем условие победы
            self.miner.check_win()

            # Проверяем, что game_over был вызван с параметром True (победа)
            mock_game_over.assert_called_once_with(True)


class TestMinerGameFlow(unittest.TestCase):
    """Тесты для проверки игрового процесса"""

    def setUp(self):
        # Создаем фиктивный главный объект tkinter и другие необходимые патчи
        self.root_patcher = patch('tkinter.Tk')
        self.mock_tk = self.root_patcher.start()
        self.msg_patcher = patch('tkinter.messagebox')
        self.mock_msg = self.msg_patcher.start()

        # Создаем экземпляр игры с известными параметрами
        self.miner = Miner(rows=5, cols=5, mines=5)

        # Создаем фиктивные кнопки
        self.miner.buttons = {}
        for r in range(5):
            for c in range(5):
                mock_button = MagicMock()
                self.miner.buttons[(r, c)] = mock_button

    def tearDown(self):
        self.root_patcher.stop()
        self.msg_patcher.stop()

    def test_new_game(self):
        """Проверка сброса игры"""
        # Имитируем некоторое состояние игры
        self.miner.first_click = False
        self.miner.game_active = False
        self.miner.opened.add((0, 0))
        self.miner.flags.add((1, 1))
        self.miner.mine_positions.add((2, 2))
        self.miner.time_elapsed = 100

        # Создаем патч для метода create_buttons_on_win
        with patch.object(self.miner, 'create_buttons_on_win'):
            # Вызываем новую игру
            self.miner.new_game()

            # Проверяем, что состояние игры сброшено
            self.assertTrue(self.miner.first_click)
            self.assertTrue(self.miner.game_active)
            self.assertEqual(len(self.miner.opened), 0)
            self.assertEqual(len(self.miner.flags), 0)
            self.assertEqual(len(self.miner.mine_positions), 0)
            self.assertEqual(self.miner.time_elapsed, 0)
            self.assertFalse(self.miner.timer_running)


class TestMinerUiComponents(unittest.TestCase):
    """Тесты для проверки компонентов пользовательского интерфейса"""

    def setUp(self):
        # Создаем фиктивный главный объект tkinter и другие необходимые патчи
        self.root_patcher = patch('tkinter.Tk')
        self.mock_tk = self.root_patcher.start()
        self.msg_patcher = patch('tkinter.messagebox')
        self.mock_msg = self.msg_patcher.start()

        # Создаем экземпляр игры
        self.miner = Miner()

    def tearDown(self):
        self.root_patcher.stop()
        self.msg_patcher.stop()

    def test_set_difficulty(self):
        """Проверка изменения сложности"""
        # Патчим метод new_game
        with patch.object(self.miner, 'new_game'):
            # Изменяем сложность
            self.miner.set_difficulty(16, 16, 40)

            # Проверяем, что параметры были изменены
            self.assertEqual(self.miner.rows, 16)
            self.assertEqual(self.miner.cols, 16)
            self.assertEqual(self.miner.mines, 40)

            # Проверяем, что метод new_game был вызван
            self.miner.new_game.assert_called_once()

    def test_custom_difficulty_validation(self):
        """Проверка валидации пользовательской сложности"""
        # Тест можно дополнить при необходимости более глубокого тестирования UI
        pass

if __name__ == '__main__':
    unittest.main()
