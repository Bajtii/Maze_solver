import argparse
import os
import sys

from maze_generator import random_perfect_maze, add_loops, from_ascii_file
from solver import bfs, dfs, astar, find_k_paths_dfs
from viz import plot_maze, animate_maze


FROM_FILE_PATH: str = r""

def parse_size(size_str: str):
    """
    Parsuje np. '31x31' -> (31, 31). Waliduje dodatnie liczby całkowite.
    """
    parts = size_str.lower().split('x')
    if len(parts) != 2:
        raise ValueError("Rozmiar powinien być w formacie WxH, np. 31x31")
    w = int(parts[0]); h = int(parts[1])
    if w <= 0 or h <= 0:
        raise ValueError("Rozmiary muszą być dodatnie.")
    return w, h

def load_maze(args):

    # 1) CLI: --from-file
    if args.from_file:
        path = args.from_file
        if not os.path.exists(path):
            raise FileNotFoundError(f"Nie znaleziono pliku: {path}")
        grid, start, end = from_ascii_file(path)
        source = f"ASCII: {os.path.abspath(path)}"
        return grid, start, end, source

    # 2) Stała FROM_FILE_PATH (może być pusty string)
    if isinstance(FROM_FILE_PATH, str) and FROM_FILE_PATH.strip():
        path = FROM_FILE_PATH.strip()
        if not os.path.exists(path):
            print(f"[WARN] FROM_FILE_PATH wskazuje na nieistniejący plik: {path}. Przechodzę dalej...")
        else:
            grid, start, end = from_ascii_file(path)
            source = f"ASCII: {os.path.abspath(path)}"
            return grid, start, end, source

    # 3) Skrót: --use-created (szukamy 'created_maze.txt' w bieżącym katalogu)
    if args.use_created:
        default_path = os.path.join(os.getcwd(), "created_maze.txt")
        if os.path.exists(default_path):
            grid, start, end = from_ascii_file(default_path)
            source = f"ASCII: {os.path.abspath(default_path)}"
            return grid, start, end, source
        else:
            print(f"[INFO] --use-created podane, ale {default_path} nie istnieje. Przechodzę na generator.")

    # 4) Fallback: generator losowy
    w, h = parse_size(args.size)
    grid, start, end = random_perfect_maze(width=w, height=h, seed=args.seed)
    if args.loops > 0.0:
        add_loops(grid, probability=args.loops)
    source = f"Generator {w}x{h}, loops={args.loops}, seed={args.seed}"
    return grid, start, end, source

def pick_algorithm(name, grid, start, end):
    """
    Wybór algorytmu i uruchomienie. Zwraca visited_order, parents, path, title.
    """
    if name == "bfs":
        visited_order, parents, path = bfs(grid, start, end)
        title = "BFS: eksploracja i najkrótsza ścieżka"
    elif name == "dfs":
        visited_order, parents, path = dfs(grid, start, end)
        title = "DFS: eksploracja (nie zawsze najkrótsza)"
    elif name == "astar":
        visited_order, parents, path = astar(grid, start, end)
        title = "A*: eksploracja i najkrótsza ścieżka"
    else:
        raise ValueError(f"Nieznany algorytm: {name}")
    return visited_order, parents, path, title

def main():
    parser = argparse.ArgumentParser(description="Rozwiązywanie labiryntu z animacją / podglądem")
    parser.add_argument("--algo", choices=["bfs", "dfs", "astar"], default="bfs",
                        help="Wybór algorytmu")
    parser.add_argument("--size", type=str, default="21x21",
                        help="Rozmiar generatora, np. 21x21 (zalecane nieparzyste)")
    parser.add_argument("--seed", type=int, default=None,
                        help="Losowe ziarno (reprodukowalność)")
    parser.add_argument("--loops", type=float, default=0.0,
                        help="Prawdopodobieństwo dodania pętli (0.0–0.2)")
    parser.add_argument("--from-file", type=str, default=None,
                        help="Ścieżka do pliku ASCII z labiryntem (S/E/#/.)")
    parser.add_argument("--use-created", action="store_true",
                        help="Użyj pliku 'created_maze.txt' z bieżącego katalogu, jeśli istnieje")
    parser.add_argument("--delay", type=float, default=0.02,
                        help="Opóźnienie animacji (sekundy)")
    parser.add_argument("--show-alt", action="store_true",
                        help="Znajdź kilka alternatywnych ścieżek DFS i wybierz najkrótszą")
    parser.add_argument("--k", type=int, default=5,
                        help="Ile alternatywnych ścieżek szukać DFS-em (gdy --show-alt)")
    parser.add_argument("--no-anim", dest="no_anim", action="store_true",
                        help="Bez animacji, pokaz statyczny")
    args = parser.parse_args()

    # Wczytaj/generuj labirynt
    try:
        grid, start, end, source = load_maze(args)
        print(f"[INFO] Źródło labiryntu -> {source}")
    except Exception as e:
        print(f"[BŁĄD] Nie udało się uzyskać labiryntu: {e}")
        sys.exit(1)

    # Uruchom wybrany algorytm
    visited_order, parents, path, title = pick_algorithm(args.algo, grid, start, end)

    # Opcjonalnie: alternatywne ścieżki i wybór najkrótszej
    if args.show_alt:
        alt_paths = find_k_paths_dfs(grid, start, end, k=args.k)
        if alt_paths:
            best_alt = min(alt_paths, key=len)
            print(f"[INFO] Alternatywy DFS: {len(alt_paths)}. Najkrótsza ma długość {len(best_alt)}.")
            if args.no_anim:
                plot_maze(grid, start, end, path=best_alt, visited=visited_order,
                          title=title + " + najkrótsza alternatywa")
            else:
                animate_maze(grid, start, end, visited_order, best_alt,
                             title=title + " + wybór najkrótszej alternatywy", delay=args.delay)
            return
        else:
            print("[INFO] Nie znaleziono alternatywnych ścieżek DFS (lub osiągnięto limit).")

    # Standardowe wyjście (dla wybranego algorytmu)
    if path:
        print(f"Długość ścieżki: {len(path)}")
    else:
        print("Brak ścieżki (meta nieosiągalna).")

    if args.no_anim:
        plot_maze(grid, start, end, path=path, visited=visited_order, title=title)
    else:
        animate_maze(grid, start, end, visited_order, path, title=title, delay=args.delay)

if __name__ == "__main__":
    main()
