import tkinter as tk
import random
from tkinter import messagebox


class Miner:
    def __init__(self, rows=10, cols=10, mines=20):
        self.rows = rows
        self.cols = cols
        self.mines = mines
        self.board = self.initialize_board()

    def initialize_board(self):
        board = [['0' for _ in range(self.cols)] for _ in range(self.rows)]
        return board