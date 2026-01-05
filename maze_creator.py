import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import os
import sys
import subprocess

# Kolory
COLOR_WALL = "#000000"   # ściana (0)
COLOR_PASS = "#FFFFFF"   # przejście (1)
COLOR_START = "#D93636"  # start i meta (S/E)
COLOR_END = "#D93636"
GRID_LINE = "#888888"    # linie siatki

class MazeCreator:
    def __init__(self, width=21, height=21, cell=24):
        # Logika
        self.w = width
        self.h = height
        self.cell = cell
        self.grid = [[0 for _ in range(self.w)] for _ in range(self.h)]  # 0=ściana, 1=przejście
        self.start = None  # (y, x)
        self.end = None    # (y, x)

        # GUI – najpierw root, potem zmienne tkinter!
        self.root = tk.Tk()
        self.root.title("Maze Creator")
        self.mode = tk.StringVar(master=self.root, value="wall")  # wall | pass | start | end

        # Górny panel
        top = tk.Frame(self.root)
        top.pack(side=tk.TOP, fill=tk.X, padx=6, pady=6)

        tk.Label(top, text="Tryb:").pack(side=tk.LEFT)
        ttk.Radiobutton(top, text="Ściana", value="wall",  variable=self.mode).pack(side=tk.LEFT)
        ttk.Radiobutton(top, text="Przejście", value="pass", variable=self.mode).pack(side=tk.LEFT)
        ttk.Radiobutton(top, text="Start", value="start",   variable=self.mode).pack(side=tk.LEFT)
        ttk.Radiobutton(top, text="Meta",  value="end",     variable=self.mode).pack(side=tk.LEFT)

        ttk.Button(top, text="Nowy", command=self.new_dialog).pack(side=tk.LEFT, padx=8)
        ttk.Button(top, text="Wyczyść", command=self.clear_all).pack(side=tk.LEFT)
        ttk.Button(top, text="Wypełnij", command=self.fill_all).pack(side=tk.LEFT)
        ttk.Button(top, text="Zapisz ASCII", command=self.save_ascii).pack(side=tk.LEFT, padx=8)
        ttk.Button(top, text="Wczytaj ASCII", command=self.load_ascii).pack(side=tk.LEFT)
        ttk.Button(top, text="Uruchom solver (main.py)", command=self.run_solver).pack(side=tk.RIGHT)

        # Status
        self.status = tk.StringVar(master=self.root,
                                   value=f"Rozmiar: {self.w}x{self.h}. Kliknij na planszy, aby edytować.")
        tk.Label(self.root, textvariable=self.status, anchor="w").pack(side=tk.BOTTOM, fill=tk.X, padx=6, pady=4)

        # Canvas
        self.canvas = tk.Canvas(self.root,
                                width=self.w * self.cell,
                                height=self.h * self.cell,
                                bg="#222222", highlightthickness=0)
        self.canvas.pack(side=tk.TOP, padx=6, pady=6)

        # Rysowanie i zdarzenia
        self.draw_all()
        self.canvas.bind("<Button-1>", self.on_click_left)
        self.canvas.bind("<B1-Motion>", self.on_drag_left)
        self.canvas.bind("<Button-3>", self.on_click_right)  # PPM: szybki toggle ściana/przejście

        # Skróty klawiaturowe (opcjonalnie)
        self.root.bind("w", lambda e: self.mode.set("wall"))
        self.root.bind("p", lambda e: self.mode.set("pass"))
        self.root.bind("s", lambda e: self.mode.set("start"))
        self.root.bind("m", lambda e: self.mode.set("end"))

        self.root.mainloop()

    # ====== Rysowanie ======
    def draw_cell(self, y, x):
        x0 = x * self.cell
        y0 = y * self.cell
        x1 = x0 + self.cell
        y1 = y0 + self.cell

        val = self.grid[y][x]
        fill = COLOR_PASS if val == 1 else COLOR_WALL
        if self.start == (y, x) or self.end == (y, x):
            fill = COLOR_START  # ten sam kolor dla S i E

        self.canvas.create_rectangle(x0, y0, x1, y1, fill=fill, outline=GRID_LINE)

    def draw_all(self):
        self.canvas.delete("all")
        for y in range(self.h):
            for x in range(self.w):
                self.draw_cell(y, x)

    # ====== Mapowanie zdarzeń na komórkę ======
    def cell_from_event(self, event):
        x = event.x // self.cell
        y = event.y // self.cell
        if 0 <= x < self.w and 0 <= y < self.h:
            return y, x
        return None

    # ====== Akcje rysujące ======
    def apply_mode_to(self, y, x):
        m = self.mode.get()
        if m == "wall":
            # ustaw ścianę; jeśli nadpisujesz S lub E – usuń je
            self.grid[y][x] = 0
            if self.start == (y, x):
                self.start = None
            if self.end == (y, x):
                self.end = None
            self.draw_cell(y, x)
            return

        if m == "pass":
            self.grid[y][x] = 1
            self.draw_cell(y, x)
            return

        if m == "start":
            # Nie pozwól na nałożenie na Metę
            if self.end == (y, x):
                self.status.set("To pole jest Metą — najpierw przesuń Metę.")
                return
            # przenieś Start w nowe miejsce (gwarancja tylko jednego S)
            if self.start and self.start != (y, x):
                py, px = self.start
                self.draw_cell(py, px)
            self.grid[y][x] = 1
            self.start = (y, x)
            self.draw_cell(y, x)
            self.status.set(f"Start przeniesiony na ({y}, {x})")
            return

        if m == "end":
            # Nie pozwól na nałożenie na Start
            if self.start == (y, x):
                self.status.set("To pole jest Startem — najpierw przesuń Start.")
                return
            # przenieś Metę w nowe miejsce (gwarancja tylko jednej E)
            if self.end and self.end != (y, x):
                py, px = self.end
                self.draw_cell(py, px)
            self.grid[y][x] = 1
            self.end = (y, x)
            self.draw_cell(y, x)
            self.status.set(f"Meta przeniesiona na ({y}, {x})")
            return

    def on_click_left(self, event):
        pos = self.cell_from_event(event)
        if pos:
            y, x = pos
            self.apply_mode_to(y, x)
            self.status.set(f"Klik: ({y}, {x}) tryb={self.mode.get()}")

    def on_drag_left(self, event):
        # W trybie Start/Meta przeciąganie jest zablokowane (unikamy „rozsmarowania”)
        if self.mode.get() not in ("wall", "pass"):
            return
        pos = self.cell_from_event(event)
        if pos:
            y, x = pos
            self.apply_mode_to(y, x)

    def on_click_right(self, event):
        # PPM: szybki toggle ściana <-> przejście
        pos = self.cell_from_event(event)
        if pos:
            y, x = pos
            self.mode.set("pass" if self.grid[y][x] == 0 else "wall")
            self.apply_mode_to(y, x)

    # ====== Operacje globalne ======
    def clear_all(self):
        self.grid = [[0 for _ in range(self.w)] for _ in range(self.h)]
        self.start = None
        self.end = None
        self.draw_all()
        self.status.set("Wyczyszczono planszę.")

    def fill_all(self):
        self.grid = [[1 for _ in range(self.w)] for _ in range(self.h)]
        if self.start:
            sy, sx = self.start
            self.grid[sy][sx] = 1
        if self.end:
            ey, ex = self.end
            self.grid[ey][ex] = 1
        self.draw_all()
        self.status.set("Wypełniono przejściami.")

    def new_dialog(self):
        nw = simpledialog.askinteger("Nowy labirynt", "Szerokość (komórki):",
                                     initialvalue=self.w, minvalue=5, maxvalue=999, parent=self.root)
        if nw is None:
            return
        nh = simpledialog.askinteger("Nowy labirynt", "Wysokość (komórki):",
                                     initialvalue=self.h, minvalue=5, maxvalue=999, parent=self.root)
        if nh is None:
            return
        self.w, self.h = nw, nh
        self.clear_all()
        self.canvas.config(width=self.w * self.cell, height=self.h * self.cell)
        self.status.set(f"Rozmiar: {self.w}x{self.h}")

    # ====== Zapis/Wczytanie ASCII ======
    def save_ascii(self):
        if not self.start or not self.end:
            messagebox.showwarning("Brak S/E", "Ustaw Start i Metę przed zapisem.", parent=self.root)
            return

        path = filedialog.asksaveasfilename(
            title="Zapisz labirynt (ASCII)",
            defaultextension=".txt",
            filetypes=[("Tekst ASCII", "*.txt"), ("Wszystkie pliki", "*.*")],
            parent=self.root
        )
        if not path:
            return
        try:
            with open(path, "w", encoding="utf-8") as f:
                for y in range(self.h):
                    row = []
                    for x in range(self.w):
                        if (y, x) == self.start:
                            row.append('S')
                        elif (y, x) == self.end:
                            row.append('E')
                        else:
                            row.append('.' if self.grid[y][x] == 1 else '#')
                    f.write(''.join(row) + "\n")
            self.status.set(f"Zapisano: {path}")
        except Exception as e:
            messagebox.showerror("Błąd zapisu", str(e), parent=self.root)

    def load_ascii(self):
        path = filedialog.askopenfilename(
            title="Wczytaj labirynt (ASCII)",
            filetypes=[("Tekst ASCII", "*.txt"), ("Wszystkie pliki", "*.*")],
            parent=self.root
        )
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                lines = [line.rstrip("\n") for line in f.readlines()]
            h = len(lines)
            w = len(lines[0]) if h > 0 else 0
            grid = []
            start = None
            end = None
            for y in range(h):
                row_chars = list(lines[y])
                if len(row_chars) != w:
                    raise ValueError("Niespójna długość wierszy w pliku.")
                row = []
                for x, ch in enumerate(row_chars):
                    if ch == '#':
                        row.append(0)
                    elif ch == '.':
                        row.append(1)
                    elif ch == 'S':
                        row.append(1); start = (y, x)
                    elif ch == 'E':
                        row.append(1); end = (y, x)
                    else:
                        row.append(0)
                grid.append(row)

            self.w, self.h = w, h
            self.grid = grid
            self.start = start
            self.end = end
            self.canvas.config(width=self.w * self.cell, height=self.h * self.cell)
            self.draw_all()
            self.status.set(f"Wczytano: {path} (rozmiar {self.w}x{self.h})")
        except Exception as e:
            messagebox.showerror("Błąd wczytania", str(e), parent=self.root)

    # ====== Integracja z solverem ======
    def run_solver(self):
        if not self.start or not self.end:
            messagebox.showwarning("Brak S/E", "Ustaw Start i Metę przed uruchomieniem solvera.", parent=self.root)
            return

        temp_path = filedialog.asksaveasfilename(
            title="Zapisz tymczasowy ASCII (do solvera)",
            initialfile="created_maze.txt",
            defaultextension=".txt",
            filetypes=[("Tekst ASCII", "*.txt")],
            parent=self.root
        )
        if not temp_path:
            return

        try:
            with open(temp_path, "w", encoding="utf-8") as f:
                for y in range(self.h):
                    row = []
                    for x in range(self.w):
                        if (y, x) == self.start:
                            row.append('S')
                        elif (y, x) == self.end:
                            row.append('E')
                        else:
                            row.append('.' if self.grid[y][x] == 1 else '#')
                    f.write(''.join(row) + "\n")
        except Exception as e:
            messagebox.showerror("Błąd zapisu", str(e), parent=self.root)
            return

        main_path = filedialog.askopenfilename(
            title="Wskaż plik main.py (solver)",
            filetypes=[("Python", "*.py"), ("Wszystkie pliki", "*.*")],
            parent=self.root
        )
        if not main_path:
            return

        algo = tk.simpledialog.askstring("Algorytm", "Wybierz algorytm: bfs / dfs / astar",
                                         initialvalue="bfs", parent=self.root)
        if not algo or algo.lower() not in ("bfs", "dfs", "astar"):
            algo = "bfs"

        try:
            delay_str = tk.simpledialog.askstring("Animacja", "Opóźnienie (sekundy), np. 0.02 (0=bez pauz):",
                                                  initialvalue="0.02", parent=self.root)
            delay = float(delay_str) if delay_str is not None else 0.02
        except:
            delay = 0.02

        try:
            cmd = [sys.executable, main_path, "--algo", algo, "--from-file", temp_path, "--delay", str(delay)]
            subprocess.Popen(cmd, shell=False)
            self.status.set(f"Uruchomiono solver: {' '.join(cmd)}")
            messagebox.showinfo("Solver", "Solver został uruchomiony w osobnym oknie/konsoli.", parent=self.root)
        except Exception as e:
            messagebox.showerror("Błąd uruchomienia", str(e), parent=self.root)


if __name__ == "__main__":
    # Okienko startowe – pytamy o rozmiar
    root = tk.Tk()
    root.withdraw()
    w = simpledialog.askinteger("Maze Creator", "Szerokość (komórki):",
                                initialvalue=31, minvalue=5, maxvalue=999, parent=root)
    h = simpledialog.askinteger("Maze Creator", "Wysokość (komórki):",
                                initialvalue=31, minvalue=5, maxvalue=999, parent=root)
    root.destroy()
    if w is None or h is None:
        w, h = 31, 31
    MazeCreator(width=w, height=h, cell=24)
