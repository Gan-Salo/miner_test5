import tkinter as tk
import random
from tkinter import messagebox


class Miner:
    def __init__(self, rows=10, cols=10, mines=20):
        self.rows = rows
        self.cols = cols
        self.mines = mines
