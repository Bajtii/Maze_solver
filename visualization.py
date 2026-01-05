import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap

CAMP = ListedColormap([
    (0, 0, 0),        # 0 - ściana
    (1, 1, 1),        # 1 - przejście
    (0.3, 0.5, 0.9),  # 2 - frontier (tu nieużywane)
    (1.0, 0.9, 0.4),  # 3 - odwiedzone
    (0.2, 0.8, 0.2),  # 4 - finalna ścieżka
    (0.9, 0.2, 0.2),  # 5 - start/meta
])

def plot_maze(grid, start=None, end=None, path=None, visited=None,
              title="Labirynt", show=True, save=None, ax=None):
    """
    Statyczny podgląd labiryntu. Jeśli podasz visited/path, zostaną zaznaczone.
    """
    h = len(grid)
    w = len(grid[0]) if h > 0 else 0
    state = np.array(grid, dtype=np.int16)

    if visited:
        for (y, x) in visited:
            if 0 <= y < h and 0 <= x < w and state[y][x] == 1:
                state[y][x] = 3
    if path:
        for (y, x) in path:
            if 0 <= y < h and 0 <= x < w and state[y][x] in (1, 3):
                state[y][x] = 4
    if start:
        sy, sx = start
        state[sy][sx] = 5
    if end:
        ey, ex = end
        state[ey][ex] = 5

    created_fig = False
    if ax is None:
        scale = max(4, min(10, max(h, w) / 4))
        fig, ax = plt.subplots(figsize=(scale, scale))
        created_fig = True

    im = ax.imshow(state, cmap=CAMP, vmin=0, vmax=5)
    ax.set_title(title)
    ax.set_xticks([]); ax.set_yticks([])
    ax.set_xticks(np.arange(-.5, w, 1), minor=True)
    ax.set_yticks(np.arange(-.5, h, 1), minor=True)
    ax.grid(which='minor', color=(0.8, 0.8, 0.8, 0.5), linewidth=0.3)
    ax.tick_params(which='both', bottom=False, left=False)

    if save:
        plt.savefig(save, bbox_inches='tight', dpi=200)
    if show and created_fig:
        plt.show()
    return im

def animate_maze(grid, start, end, visited_order, final_path,
                 title="Animacja algorytmu", delay=0.03, show=True):
    """
    Prosta animacja krokowa: najpierw eksploracja visited_order, potem final_path.
    """
    h = len(grid)
    w = len(grid[0]) if h > 0 else 0

    state = np.array(grid, dtype=np.int16)
    sy, sx = start
    ey, ex = end
    state[sy][sx] = 5
    state[ey][ex] = 5

    scale = max(4, min(10, max(h, w) / 4))
    fig, ax = plt.subplots(figsize=(scale, scale))
    im = ax.imshow(state, cmap=CAMP, vmin=0, vmax=5)
    ax.set_title(title)
    ax.set_xticks([]); ax.set_yticks([])
    ax.set_xticks(np.arange(-.5, w, 1), minor=True)
    ax.set_yticks(np.arange(-.5, h, 1), minor=True)
    ax.grid(which='minor', color=(0.8, 0.8, 0.8, 0.5), linewidth=0.3)
    ax.tick_params(which='both', bottom=False, left=False)
    plt.show(block=False)

    # Eksploracja
    for (y, x) in visited_order:
        if (y, x) not in (start, end) and state[y][x] == 1:
            state[y][x] = 3
            im.set_data(state)
            plt.pause(delay)

    for (y, x) in final_path:
        if (y, x) not in (start, end):
            state[y][x] = 4
            im.set_data(state)
            plt.pause(delay)

    if show:
        plt.show()

def print_maze_ascii(grid, start=None, end=None):
    """
    Tekstowy podgląd labiryntu w konsoli:
    '#' - ściana, '.' - przejście, 'S' - start, 'E' - meta
    """
    h = len(grid)
    w = len(grid[0]) if h > 0 else 0
    for y in range(h):
        row = []
        for x in range(w):
            if start and (y, x) == start:
                row.append('S')
            elif end and (y, x) == end:
                row.append('E')
            else:
                row.append('.' if grid[y][x] == 1 else '#')
        print(''.join(row))
