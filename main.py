import tkinter as tk
import random
from tkinter import messagebox


class Miner:
    def __init__(self, rows=10, cols=10, mines=20):
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
                                   command=lambda r=row, c=col: self.on_button_click(r, c))
                button.grid(row=row, column=col)
                self.buttons[(row, col)] = button

    def on_button_click(self, row, col):
        if self.first_click:
            self.place_mines(row, col)
            self.first_click = False
        if (row, col) in self.mine_positions:
            messagebox.showinfo("Игра окончена", "Вы наткнулись на мину!")
            self.buttons[(row, col)].config(text='*', bg='red')


if __name__ == '__main__':
    app = Miner()
    app.root.mainloop()