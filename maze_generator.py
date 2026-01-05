import random

def empty_grid(width, height):
    grid = []
    for y in range(height):
        row = []
        for x in range(width):
            row.append(0)  # wszystko ściana
        grid.append(row)
    return grid

def in_bounds(x, y, width, height):
    return 0 <= x < width and 0 <= y < height

def random_perfect_maze(width=21, height=21, seed=None):

    if seed is not None:
        random.seed(seed)

    if width % 2 == 0 or height % 2 == 0:
        raise ValueError("Szerokość i wysokość powinny być nieparzyste, np. 21x21")

    grid = empty_grid(width, height)

    # Start w komórce (1,1)
    stack = [(1, 1)]
    grid[1][1] = 1

    # Ruch o 2 komórki (pozwala zostawić „ściany” między komórkami)
    directions = [(2, 0), (-2, 0), (0, 2), (0, -2)]

    while stack:
        x, y = stack[-1]

        # znajdź sąsiadów oddalonych o 2 kratki, jeszcze nie odwiedzonych
        nbrs = []
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if in_bounds(nx, ny, width, height) and grid[ny][nx] == 0:
                nbrs.append((nx, ny, dx, dy))

        if nbrs:
            nx, ny, dx, dy = random.choice(nbrs)
            # Przetnij ścianę między (x,y) a (nx,ny)
            grid[y + dy // 2][x + dx // 2] = 1
            grid[ny][nx] = 1
            stack.append((nx, ny))
        else:
            stack.pop()

    # Upewnij się, że start i meta są przejściem
    grid[1][1] = 1
    grid[height - 2][width - 2] = 1
    return grid, (1, 1), (height - 2, width - 2)

def add_loops(grid, probability=0.05):

    height = len(grid)
    width = len(grid[0]) if height > 0 else 0

    for y in range(1, height - 1):
        for x in range(1, width - 1):
            if grid[y][x] == 0:  # ściana
                if random.random() < probability:
                    grid[y][x] = 1  # zrób przejście

def from_ascii_lines(lines):

    grid = []
    start = None
    end = None

    for y, line in enumerate(lines):
        row = []
        for x, ch in enumerate(line.rstrip('\n')):
            if ch == '#':
                row.append(0)
            elif ch == '.':
                row.append(1)
            elif ch == 'S':
                row.append(1)
                start = (y, x)
            elif ch == 'E':
                row.append(1)
                end = (y, x)
            else:
                # Dowolny inny znak traktujemy jak ścianę dla bezpieczeństwa
                row.append(0)
        grid.append(row)

    if start is None or end is None:
        raise ValueError("ASCII musi zawierać 'S' i 'E' jako start i metę")

    return grid, start, end

def from_ascii_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    return from_ascii_lines(lines)

def to_ascii_file(grid, start, end, path):
    """
    Zapis do pliku ASCII (ułatwia ręczną edycję).
    """
    height = len(grid)
    width = len(grid[0]) if height > 0 else 0

    lines = []
    for y in range(height):
        row_chars = []
        for x in range(width):
            if (y, x) == start:
                row_chars.append('S')
            elif (y, x) == end:
                row_chars.append('E')
            else:
                row_chars.append('.' if grid[y][x] == 1 else '#')
        lines.append(''.join(row_chars))

    with open(path, 'w', encoding='utf-8') as f:
        for line in lines:
            f.write(line + '\n')
