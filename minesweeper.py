# minesweeper.py
import tkinter as tk
import random
from tkinter import messagebox, ttk, simpledialog
#

class Miner:
    def __init__(self, rows=8, cols=8, mines=10):
        self.rows = rows
        self.cols = cols
        self.mines = mines
        if mines >= rows * cols:
            raise ValueError("Количество мин должно быть меньше, чем количество клеток на поле.")
        self.board = self.initialize_board()
        self.root = tk.Tk()
        self.root.title("Сапёр")
        self.root.resizable(False, False)

        # Добавляем меню
        self.create_menu()

        # Добавляем строку состояния
        self.status_frame = tk.Frame(self.root)
        self.status_frame.grid(row=0, column=0, columnspan=self.cols, sticky='ew')

        self.mine_counter = tk.Label(self.status_frame, text=f"Мины: {mines}")
        self.mine_counter.pack(side=tk.LEFT, padx=5, pady=5)

        self.timer_label = tk.Label(self.status_frame, text="Время: 0")
        self.timer_label.pack(side=tk.RIGHT, padx=5, pady=5)

        self.time_elapsed = 0
        self.timer_running = False

        # Создаем рамку для кнопок
        self.button_frame = tk.Frame(self.root)
        self.button_frame.grid(row=1, column=0)

        self.create_buttons_on_win()
        self.mine_positions = set()
        self.first_click = True
        self.opened = set()
        self.flags = set()
        self.game_active = True
        self.best_times = self.load_best_times()

    def create_menu(self):
        menubar = tk.Menu(self.root)

        # Создаем меню "Игра"
        game_menu = tk.Menu(menubar, tearoff=0)
        game_menu.add_command(label="Новая игра", command=self.new_game)
        game_menu.add_separator()

        difficulty_menu = tk.Menu(game_menu, tearoff=0)
        difficulty_menu.add_command(label="Начинающий (8x8, 10 мин)",
                                    command=lambda: self.set_difficulty(8, 8, 10))
        difficulty_menu.add_command(label="Средний (16x16, 40 мин)",
                                    command=lambda: self.set_difficulty(16, 16, 40))
        difficulty_menu.add_command(label="Эксперт (16x30, 99 мин)",
                                    command=lambda: self.set_difficulty(16, 30, 99))
        difficulty_menu.add_command(label="Пользовательский", command=self.custom_difficulty)

        game_menu.add_cascade(label="Сложность", menu=difficulty_menu)
        game_menu.add_separator()
        game_menu.add_command(label="Рекорды", command=self.show_best_times)
        game_menu.add_separator()
        game_menu.add_command(label="Выход", command=self.root.quit)

        menubar.add_cascade(label="Игра", menu=game_menu)

        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="Как играть", command=self.show_help)
        help_menu.add_command(label="О программе", command=self.show_about)
        menubar.add_cascade(label="Помощь", menu=help_menu)

        self.root.config(menu=menubar)

    def set_difficulty(self, rows, cols, mines):
        self.rows = rows
        self.cols = cols
        self.mines = mines
        self.new_game()

    def custom_difficulty(self):
        custom_window = tk.Toplevel(self.root)
        custom_window.title("Пользовательская сложность")
        custom_window.resizable(False, False)

        tk.Label(custom_window, text="Строки:").grid(row=0, column=0, padx=5, pady=5)
        rows_entry = tk.Entry(custom_window)
        rows_entry.grid(row=0, column=1, padx=5, pady=5)
        rows_entry.insert(0, str(self.rows))

        tk.Label(custom_window, text="Столбцы:").grid(row=1, column=0, padx=5, pady=5)
        cols_entry = tk.Entry(custom_window)
        cols_entry.grid(row=1, column=1, padx=5, pady=5)
        cols_entry.insert(0, str(self.cols))

        tk.Label(custom_window, text="Мины:").grid(row=2, column=0, padx=5, pady=5)
        mines_entry = tk.Entry(custom_window)
        mines_entry.grid(row=2, column=1, padx=5, pady=5)
        mines_entry.insert(0, str(self.mines))

        def apply_settings():
            try:
                rows = int(rows_entry.get())
                cols = int(cols_entry.get())
                mines = int(mines_entry.get())

                if rows < 5 or cols < 5:
                    messagebox.showerror("Ошибка", "Минимальный размер поля 5x5")
                    return

                if mines >= rows * cols:
                    messagebox.showerror("Ошибка", "Слишком много мин для данного размера поля")
                    return

                self.set_difficulty(rows, cols, mines)
                custom_window.destroy()
            except ValueError:
                messagebox.showerror("Ошибка", "Пожалуйста, введите корректные числа")

        tk.Button(custom_window, text="Применить", command=apply_settings).grid(row=3, column=0, columnspan=2, pady=10)

        custom_window.transient(self.root)
        custom_window.grab_set()
        self.root.wait_window(custom_window)

    def new_game(self):
        # Останавливаем таймер, если он запущен
        self.timer_running = False
        self.time_elapsed = 0
        self.timer_label.config(text="Время: 0")

        # Сбрасываем состояние игры
        self.board = self.initialize_board()
        self.mine_positions = set()
        self.first_click = True
        self.opened = set()
        self.flags = set()
        self.game_active = True

        # Обновляем счетчик мин
        self.mine_counter.config(text=f"Мины: {self.mines}")

        # Пересоздаем кнопки
        for widget in self.button_frame.winfo_children():
            widget.destroy()

        self.create_buttons_on_win()

    def initialize_board(self):
        board = [['0' for _ in range(self.cols)] for _ in range(self.rows)]
        return board

    def place_mines(self, start_row, start_col):
        # Создаем защитную зону вокруг первого клика
        protected = {(start_row + dx, start_col + dy)
                     for dx in [-1, 0, 1]
                     for dy in [-1, 0, 1]
                     if 0 <= start_row + dx < self.rows and 0 <= start_col + dy < self.cols}

        while len(self.mine_positions) < self.mines:
            row = random.randint(0, self.rows - 1)
            col = random.randint(0, self.cols - 1)
            if (row, col) not in protected and (row, col) not in self.mine_positions:
                self.mine_positions.add((row, col))

    def create_buttons_on_win(self):
        self.buttons = {}
        for row in range(self.rows):
            for col in range(self.cols):
                button = tk.Button(self.button_frame, text='', width=2, height=1,
                                   command=lambda r=row, c=col: self.on_button_click(r, c),
                                   relief='raised')
                button.bind('<Button-3>', lambda event, r=row, c=col: self.on_right_click(r, c))
                button.grid(row=row, column=col)
                self.buttons[(row, col)] = button

    def on_button_click(self, row, col):
        if not self.game_active:
            return

        if (row, col) in self.flags:
            return

        if self.first_click:
            self.place_mines(row, col)
            self.first_click = False
            # Запускаем таймер при первом клике
            self.timer_running = True
            self.update_timer()

        if (row, col) in self.mine_positions:
            self.game_over(False)
        else:
            self.reveal_space(row, col)
            self.check_win()

    def update_timer(self):
        if self.timer_running:
            self.time_elapsed += 1
            self.timer_label.config(text=f"Время: {self.time_elapsed}")
            self.root.after(1000, self.update_timer)

    def count_mines_around(self, row, col):
        return sum(
            (row + dx, col + dy) in self.mine_positions
            for dx in [-1, 0, 1]
            for dy in [-1, 0, 1]
            if dx != 0 or dy != 0 if 0 <= row + dx < self.rows and 0 <= col + dy < self.cols
        )

    def reveal_space(self, row, col):
        if (row, col) in self.opened or (row, col) in self.flags:
            return

        self.opened.add((row, col))
        count = self.count_mines_around(row, col)
        button = self.buttons[(row, col)]

        # Цветовая схема для чисел
        color_map = {
            1: 'blue', 2: 'green', 3: 'red', 4: 'purple',
            5: 'maroon', 6: 'turquoise', 7: 'black', 8: 'gray'
        }

        if count > 0:
            button.config(text=str(count), bg='lightgrey', fg=color_map.get(count, 'black'))
        else:
            button.config(text=' ', bg='lightgrey')
            # Рекурсивно открываем соседние пустые клетки
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    if 0 <= row + dx < self.rows and 0 <= col + dy < self.cols:
                        self.reveal_space(row + dx, col + dy)

    def on_right_click(self, row, col):
        if not self.game_active or (row, col) in self.opened:
            return

        btn = self.buttons[(row, col)]
        if (row, col) in self.flags:
            btn.config(text=' ')
            self.flags.remove((row, col))
            self.mine_counter.config(text=f"Мины: {self.mines - len(self.flags)}")
        else:
            btn.config(text='F', fg='red')
            self.flags.add((row, col))
            self.mine_counter.config(text=f"Мины: {self.mines - len(self.flags)}")

    def check_win(self):
        if len(self.opened) == self.rows * self.cols - self.mines:
            self.game_over(True)

    def game_over(self, win):
        self.timer_running = False
        self.game_active = False

        for (row, col) in self.mine_positions:
            btn = self.buttons[(row, col)]
            if win:
                if (row, col) not in self.flags:
                    btn.config(text='F', fg='red')
            else:
                if (row, col) in self.flags:
                    btn.config(text='F', bg='green')
                else:
                    btn.config(text='*', bg='red')

        if win:
            # Сохраняем результат, если это рекорд
            self.save_best_time()
            messagebox.showinfo("Поздравляем!", f"Вы выиграли за {self.time_elapsed} секунд!")
        else:
            messagebox.showinfo("Игра окончена", "Вы наткнулись на мину!")

    def load_best_times(self):
        # В реальном приложении здесь бы загружались данные из файла
        return {
            "beginner": 999,
            "intermediate": 999,
            "expert": 999
        }

    def save_best_time(self):
        if self.rows == 8 and self.cols == 8 and self.mines == 10:
            difficulty = "beginner"
        elif self.rows == 16 and self.cols == 16 and self.mines == 40:
            difficulty = "intermediate"
        elif self.rows == 16 and self.cols == 30 and self.mines == 99:
            difficulty = "expert"
        else:
            # Пользовательская сложность не сохраняется в рекордах
            return

        if self.time_elapsed < self.best_times.get(difficulty, 999):
            self.best_times[difficulty] = self.time_elapsed
            messagebox.showinfo("Новый рекорд!",
                                f"Вы установили новый рекорд для уровня сложности!")

    def show_best_times(self):
        records_window = tk.Toplevel(self.root)
        records_window.title("Рекорды")
        records_window.resizable(False, False)

        ttk.Label(records_window, text="Лучшее время:").grid(row=0, column=0, columnspan=2, pady=10)

        difficulties = {
            "beginner": "Начинающий (8x8, 10 мин)",
            "intermediate": "Средний (16x16, 40 мин)",
            "expert": "Эксперт (16x30, 99 мин)"
        }

        row = 1
        for key, name in difficulties.items():
            ttk.Label(records_window, text=name).grid(row=row, column=0, sticky='w', padx=5, pady=2)
            time_value = self.best_times.get(key, 999)
            time_text = str(time_value) if time_value < 999 else "-"
            ttk.Label(records_window, text=f"{time_text} сек").grid(row=row, column=1, padx=5, pady=2)
            row += 1

        ttk.Button(records_window, text="OK", command=records_window.destroy).grid(
            row=row, column=0, columnspan=2, pady=10)

        records_window.transient(self.root)
        records_window.grab_set()
        self.root.wait_window(records_window)

    def show_help(self):
        help_text = """
        Правила игры "Сапёр":

        1. Цель игры - открыть все клетки, не содержащие мины.
        2. Левый клик мыши открывает клетку.
        3. Правый клик устанавливает/снимает флаг.
        4. Числа показывают, сколько мин находится рядом.
        5. Игра заканчивается победой, когда открыты все клетки без мин.
        6. Игра заканчивается поражением, если вы открыли клетку с миной.

        Удачи!
        """
        messagebox.showinfo("Как играть", help_text)

    def show_about(self):
        about_text = """
        Игра "Сапёр" v1.0

        Разработана на Python с использованием Tkinter.

        © Овсянников Георгий
        """
        messagebox.showinfo("О программе", about_text)


if __name__ == '__main__':
    miner = Miner()
    miner.root.mainloop()