
import argparse
import os
import sys

from maze_generator import random_perfect_maze, add_loops, from_ascii_file
from solver import bfs, dfs, astar, find_k_paths_dfs
from viz import plot_maze, animate_maze


FROM_FILE_PATH: str = r""


def parse_size(size_str: str):
    """Parse '31x31' -> (31, 31). Validates positive integers."""
    parts = size_str.lower().split('x')
    if len(parts) != 2:
        raise ValueError("Size must be in WxH format, e.g., 31x31")
    w = int(parts[0]); h = int(parts[1])
    if w <= 0 or h <= 0:
        raise ValueError("Width and height must be positive.")
    return w, h


def load_maze(args):
    """
    Returns (grid, start, end) and a source description.
    Priority:
      1) --from-file <path>
      2) FROM_FILE_PATH (if non-empty and exists)
      3) --use-created (created_maze.txt in CWD)
      4) random generator (size/seed/loops)
    """
    # 1) CLI: --from-file
    if args.from_file:
        path = args.from_file
        if not os.path.exists(path):
            raise FileNotFoundError(f"File not found: {path}")
        grid, start, end = from_ascii_file(path)
        source = f"ASCII: {os.path.abspath(path)}"
        return grid, start, end, source

    # 2) Constant FROM_FILE_PATH (may be empty)
    if isinstance(FROM_FILE_PATH, str) and FROM_FILE_PATH.strip():
        path = FROM_FILE_PATH.strip()
        if not os.path.exists(path):
            print(f"[WARN] FROM_FILE_PATH points to a non-existent file: {path}. Continuing...")
        else:
            grid, start, end = from_ascii_file(path)
            source = f"ASCII: {os.path.abspath(path)}"
            return grid, start, end, source

    # 3) Shortcut: --use-created (look for 'created_maze.txt' in current directory)
    if args.use_created:
        default_path = os.path.join(os.getcwd(), "created_maze.txt")
        if os.path.exists(default_path):
            grid, start, end = from_ascii_file(default_path)
            source = f"ASCII: {os.path.abspath(default_path)}"
            return grid, start, end, source
        else:
            print(f"[INFO] --use-created given, but {default_path} does not exist. Falling back to generator.")

    # 4) Fallback: random generator
    w, h = parse_size(args.size)
    grid, start, end = random_perfect_maze(width=w, height=h, seed=args.seed)
    if args.loops > 0.0:
        add_loops(grid, probability=args.loops)
    source = f"Generator {w}x{h}, loops={args.loops}, seed={args.seed}"
    return grid, start, end, source


def pick_algorithm(name, grid, start, end):
    """Pick and run an algorithm. Returns visited_order, parents, path, title."""
    if name == "bfs":
        visited_order, parents, path = bfs(grid, start, end)
        title = "BFS: exploration and shortest path"
    elif name == "dfs":
        visited_order, parents, path = dfs(grid, start, end)
        title = "DFS: exploration (not always shortest)"
    elif name == "astar":
        visited_order, parents, path = astar(grid, start, end)
        title = "A*: exploration and shortest path"
    else:
        raise ValueError(f"Unknown algorithm: {name}")
    return visited_order, parents, path, title


def main():
    parser = argparse.ArgumentParser(description="Maze solving with animation/preview")
    parser.add_argument("--algo", choices=["bfs", "dfs", "astar"], default="bfs",
                        help="Algorithm to use")
    parser.add_argument("--size", type=str, default="21x21",
                        help="Generator size, e.g., 21x21 (odd sizes recommended)")
    parser.add_argument("--seed", type=int, default=None,
                        help="Random seed for reproducibility")
    parser.add_argument("--loops", type=float, default=0.0,
                        help="Probability of adding loops (0.0–0.2)")
    parser.add_argument("--from-file", type=str, default=None,
                        help="Path to ASCII maze file (S/E/#/.)")
    parser.add_argument("--use-created", action="store_true",
                        help="Use 'created_maze.txt' from current directory if it exists")
    parser.add_argument("--delay", type=float, default=0.02,
                        help="Animation delay in seconds")
    parser.add_argument("--show-alt", action="store_true",
                        help="Find several alternative DFS paths and pick the shortest")
    parser.add_argument("--k", type=int, default=5,
                        help="How many alternative paths to search with DFS (used with --show-alt)")
    parser.add_argument("--no-anim", dest="no_anim", action="store_true",
                        help="Disable animation, show static plot")
    args = parser.parse_args()

    try:
        grid, start, end, source = load_maze(args)
        print(f"[INFO] Maze source -> {source}")
    except Exception as e:
        print(f"[ERROR] Failed to get maze: {e}")
        sys.exit(1)

    visited_order, parents, path, title = pick_algorithm(args.algo, grid, start, end)

    if args.show_alt:
        alt_paths = find_k_paths_dfs(grid, start, end, k=args.k)
        if alt_paths:
            best_alt = min(alt_paths, key=len)
            print(f"[INFO] DFS alternatives: {len(alt_paths)}. Shortest length: {len(best_alt)}.")
            if args.no_anim:
                plot_maze(grid, start, end, path=best_alt, visited=visited_order,
                          title=title + " + shortest alternative")
            else:
                animate_maze(grid, start, end, visited_order, best_alt,
                             title=title + " + shortest alternative selected", delay=args.delay)
            return
        else:
            print("[INFO] No alternative DFS paths found (or limit reached).")

    if path:
        print(f"Path length: {len(path)}")
    else:
        print("No path (goal unreachable).")

    if args.no_anim:
        plot_maze(grid, start, end, path=path, visited=visited_order, title=title)
    else:
        animate_maze(grid, start, end, visited_order, path, title=title, delay=args.delay)


if __name__ == "__main__":
    main()
