import tkinter as tk
import random
from tkinter import messagebox


class Miner:
    def __init__(self, rows=8, cols=8, mines=120):
        self.rows = rows
        self.cols = cols
        self.mines = mines
        self.board = self.initialize_board()
        self.root = tk.Tk()
        self.root.title("Сапёр")
        self.root.resizable(False, False)
        self.create_buttons_on_win()
        self.mine_positions = set()
        self.first_click = True
        self.opened = set()
        self.flags = set()

    def initialize_board(self):
        board = [['0' for _ in range(self.cols)] for _ in range(self.rows)]
        return board

    def place_mines(self, start_row, start_col):
        while len(self.mine_positions) < self.mines:
            row = random.randint(0, self.rows - 1)
            col = random.randint(0, self.cols - 1)
            if (row, col) != (start_row, start_col) and (row, col) not in self.mine_positions:
                self.mine_positions.add((row, col))

    def create_buttons_on_win(self):
        self.buttons = {}
        for row in range(self.rows):
            for col in range(self.cols):
                button = tk.Button(self.root, text='', width=4, height=2,
                                   command=lambda r=row, c=col: self.on_button_click(r, c),
                                   relief='raised')
                button.bind('<Button-3>', lambda event, r=row, c=col: self.on_right_click(r, c))
                button.grid(row=row, column=col)
                self.buttons[(row, col)] = button

    def on_button_click(self, row, col):
        if self.first_click:
            self.place_mines(row, col)
            self.first_click = False
        if (row, col) in self.mine_positions:
            self.game_over(False)
        else:
            self.reveal_space(row, col)
            self.check_win()

    def count_mines_around(self, row, col):
        return sum(
            (row + dx, col + dy) in self.mine_positions
            for dx in [-1, 0, 1]
            for dy in [-1, 0, 1]
            if dx != 0 or dy != 0 if 0 <= row + dx < self.rows and 0 <= col + dy < self.cols
        )

    def reveal_space(self, row, col):
        if (row, col) in self.opened:
            return
        self.opened.add((row, col))
        count = self.count_mines_around(row, col)
        button = self.buttons[(row, col)]
        button.config(text=str(count) if count > 0 else ' ', bg='lightgrey')
        if count == 0:
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    if 0 <= row + dx < self.rows and 0 <= col + dy < self.cols and (dx != 0 or dy != 0):
                        self.reveal_space(row + dx, col + dy)

    def on_right_click(self, x, y):
        btn = self.buttons[(x, y)]
        if (x, y) in self.opened:
            return
        if (x, y) in self.flags:
            btn.config(text=' ')
            self.flags.remove((x, y))
        else:
            btn.config(text='F')
            self.flags.add((x, y))

    def check_win(self):
        if len(self.opened) == self.rows * self.cols - self.mines:
            self.game_over(True)

    def game_over(self, win):
        for (row, col) in self.mine_positions:
            btn = self.buttons[(row, col)]
            btn.config(text='*' if not win else 'F', bg='red' if not win else 'green')
        messagebox.showinfo("Игра окончена", "Вы выиграли!" if win else "Вы наткнулись на мину!")
        self.root.quit()

if __name__ == '__main__':
    app = Miner()
    app.root.mainloop()