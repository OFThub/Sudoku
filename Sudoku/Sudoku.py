import tkinter as tk
import random
from tkinter import ttk, messagebox

#############################################
# SUDOKU OLUŞTURMA
#############################################

def is_valid(board, r, c, val, size, sr, sc):
    for i in range(size):
        if board[r][i] == val or board[i][c] == val:
            return False

    br = (r // sr) * sr
    bc = (c // sc) * sc
    for i in range(br, br + sr):
        for j in range(bc, bc + sc):
            if board[i][j] == val:
                return False
    return True


def solve(board, size, sr, sc):
    for r in range(size):
        for c in range(size):
            if board[r][c] == 0:
                nums = list(range(1, size + 1))
                random.shuffle(nums)
                for n in nums:
                    if is_valid(board, r, c, n, size, sr, sc):
                        board[r][c] = n
                        if solve(board, size, sr, sc):
                            return True
                        board[r][c] = 0
                return False
    return True


def generate_sudoku(size, diff):
    sr, sc = (2, 3) if size == 6 else (3, 3)
    board = [[0]*size for _ in range(size)]
    solve(board, size, sr, sc)

    ratio = {"Kolay": 0.55, "Orta": 0.4, "Zor": 0.28}[diff]
    keep = int(size * size * ratio)

    cells = [(r, c) for r in range(size) for c in range(size)]
    random.shuffle(cells)
    for r, c in cells[keep:]:
        board[r][c] = 0

    return board, sr, sc

#############################################
# AYARLAR EKRANI
#############################################

class Settings:
    def __init__(self, root):
        self.root = root
        self.root.title("Sudoku Ayarları")

        f = tk.Frame(root, padx=20, pady=20)
        f.pack()

        tk.Label(f, text="Boyut").grid(row=0, column=0)
        self.size = tk.IntVar(value=6)
        ttk.Combobox(f, values=[6, 9], textvariable=self.size, state="readonly").grid(row=0, column=1)

        tk.Label(f, text="Hücre Boyutu").grid(row=1, column=0)
        self.cell = tk.IntVar(value=60)
        ttk.Combobox(f, values=[40, 50, 60, 70], textvariable=self.cell).grid(row=1, column=1)

        tk.Label(f, text="Zorluk").grid(row=2, column=0)
        self.diff = tk.StringVar(value="Orta")
        ttk.Combobox(f, values=["Kolay", "Orta", "Zor"], textvariable=self.diff, state="readonly").grid(row=2, column=1)

        ttk.Button(f, text="Başlat", command=self.start).grid(row=3, columnspan=2, pady=10)

    def start(self):
        board, sr, sc = generate_sudoku(self.size.get(), self.diff.get())
        self.root.destroy()
        Game(board, self.size.get(), self.cell.get(), sr, sc)

#############################################
# OYUN
#############################################

class Game:
    def __init__(self, board, size, cell, sr, sc):
        self.size = size
        self.sr = sr
        self.sc = sc
        self.board = board
        self.entries = [[None]*size for _ in range(size)]

        self.root = tk.Tk()
        self.root.title("Sudoku")

        vcmd = (self.root.register(self.validate_input), '%P')

        f = tk.Frame(self.root, bg="black", padx=4, pady=4)
        f.pack(padx=20, pady=20)

        for r in range(size):
            for c in range(size):
                bg = "#E6E6E6" if board[r][c] else "white"
                e = tk.Entry(
                    f, width=2,
                    font=("Segoe UI", cell//2, "bold"),
                    justify="center",
                    bg=bg, relief="solid", bd=1,
                    validate="key",
                    validatecommand=vcmd
                )

                px = (1, 4) if (c+1) % sc == 0 and c != size-1 else 1
                py = (1, 4) if (r+1) % sr == 0 and r != size-1 else 1
                e.grid(row=r, column=c, padx=px, pady=py, ipady=cell//6)

                if board[r][c]:
                    e.insert(0, board[r][c])
                    e.config(state="disabled")

                e.bind("<KeyRelease>", lambda ev: self.check())
                self.entries[r][c] = e

        self.root.mainloop()

    def validate_input(self, P):
        if P == "":
            return True
        return P.isdigit() and 1 <= int(P) <= self.size

    def get(self, r, c):
        v = self.entries[r][c].get()
        return int(v) if v.isdigit() else 0

    #############################################
    # KONTROL VE RENKLENDİRME
    #############################################

    def check(self):
        size = self.size
        valid = [[True]*size for _ in range(size)]

        # RESET
        for r in range(size):
            for c in range(size):
                if self.entries[r][c]["state"] == "normal":
                    self.entries[r][c].config(bg="white")

        # SATIR
        for r in range(size):
            seen = {}
            for c in range(size):
                v = self.get(r, c)
                if v:
                    if v in seen:
                        valid[r][c] = False
                        valid[r][seen[v]] = False
                    else:
                        seen[v] = c

        # SÜTUN
        for c in range(size):
            seen = {}
            for r in range(size):
                v = self.get(r, c)
                if v:
                    if v in seen:
                        valid[r][c] = False
                        valid[seen[v]][c] = False
                    else:
                        seen[v] = r

        # HÜCRE
        for br in range(0, size, self.sr):
            for bc in range(0, size, self.sc):
                seen = {}
                for r in range(br, br+self.sr):
                    for c in range(bc, bc+self.sc):
                        v = self.get(r, c)
                        if v:
                            if v in seen:
                                pr, pc = seen[v]
                                valid[r][c] = False
                                valid[pr][pc] = False
                            else:
                                seen[v] = (r, c)

        solved = True

        # KIRMIZI
        for r in range(size):
            for c in range(size):
                if self.get(r, c) == 0:
                    solved = False
                elif not valid[r][c]:
                    self.entries[r][c].config(bg="#F28B82")
                    solved = False

        # YEŞİL SATIR
        for r in range(size):
            if all(self.get(r, c) and valid[r][c] for c in range(size)):
                for c in range(size):
                    self.entries[r][c].config(bg="#CCFFCC")

        # YEŞİL SÜTUN
        for c in range(size):
            if all(self.get(r, c) and valid[r][c] for r in range(size)):
                for r in range(size):
                    self.entries[r][c].config(bg="#CCFFCC")

        # YEŞİL HÜCRE
        for br in range(0, size, self.sr):
            for bc in range(0, size, self.sc):
                cells = [(r, c) for r in range(br, br+self.sr) for c in range(bc, bc+self.sc)]
                if all(self.get(r, c) and valid[r][c] for r, c in cells):
                    for r, c in cells:
                        self.entries[r][c].config(bg="#CCFFCC")

        if solved:
            messagebox.showinfo("Tebrikler", "🎉 Sudokuyu çözdünüz!")

#############################################
# ANA PROGRAM
#############################################

if __name__ == "__main__":
    root = tk.Tk()
    Settings(root)
    root.mainloop()
