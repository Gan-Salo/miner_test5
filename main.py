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

    def initialize_board(self):
        board = [['0' for _ in range(self.cols)] for _ in range(self.rows)]
        return board

    def place_mines(self, board, mines):
        placed_mines = 0
        while placed_mines < mines:
            row = random.randint(0, self.rows - 1)
            col = random.randint(0, self.cols - 1)
            if board[row][col] != 'M':
                board[row][col] = 'M'
                placed_mines += 1

if __name__ == '__main__':
    app = Miner()
    app.root.mainloop()