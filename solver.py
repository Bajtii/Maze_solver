from collections import deque
import heapq
import math

# Ruchy 4-kierunkowe
DIRS4 = [(1,0), (-1,0), (0,1), (0,-1)]

def neighbors(grid, y, x):
    h = len(grid)
    w = len(grid[0]) if h > 0 else 0
    for dy, dx in DIRS4:
        ny, nx = y + dy, x + dx
        if 0 <= ny < h and 0 <= nx < w and grid[ny][nx] == 1:
            yield (ny, nx)

def reconstruct_path(parents, start, end):
    path = []
    cur = end
    while cur != start:
        path.append(cur)
        cur = parents.get(cur)
        if cur is None:
            return []  # brak ścieżki
    path.append(start)
    path.reverse()
    return path

def bfs(grid, start, end):

    q = deque([start])
    visited = set([start])
    parents = {}
    visited_order = [start]

    while q:
        node = q.popleft()
        if node == end:
            break
        y, x = node
        for ny, nx in neighbors(grid, y, x):
            nxt = (ny, nx)
            if nxt not in visited:
                visited.add(nxt)
                parents[nxt] = node
                visited_order.append(nxt)
                q.append(nxt)

    path = reconstruct_path(parents, start, end)
    return visited_order, parents, path

def dfs(grid, start, end):

    stack = [start]
    visited = set([start])
    parents = {}
    visited_order = [start]

    while stack:
        node = stack.pop()
        if node == end:
            break
        y, x = node
        for ny, nx in neighbors(grid, y, x):
            nxt = (ny, nx)
            if nxt not in visited:
                visited.add(nxt)
                parents[nxt] = node
                visited_order.append(nxt)
                stack.append(nxt)

    path = reconstruct_path(parents, start, end)
    return visited_order, parents, path

def manhattan(a, b):
    ay, ax = a
    by, bx = b
    return abs(ay - by) + abs(ax - bx)

def astar(grid, start, end):

    open_heap = []
    g = {start: 0}
    parents = {}
    visited_order = [start]
    counter = 0
    heapq.heappush(open_heap, (manhattan(start, end), counter, start))
    closed = set()

    while open_heap:
        _, _, node = heapq.heappop(open_heap)
        if node in closed:
            continue
        closed.add(node)

        if node == end:
            break

        y, x = node
        for ny, nx in neighbors(grid, y, x):
            nxt = (ny, nx)
            tentative_g = g[node] + 1
            if tentative_g < g.get(nxt, math.inf):
                g[nxt] = tentative_g
                parents[nxt] = node
                counter += 1
                f = tentative_g + manhattan(nxt, end)
                heapq.heappush(open_heap, (f, counter, nxt))
                visited_order.append(nxt)

    path = reconstruct_path(parents, start, end)
    return visited_order, parents, path

def find_k_paths_dfs(grid, start, end, k=5, max_steps=100000):

    paths = []
    h = len(grid)
    w = len(grid[0]) if h > 0 else 0

    visited = [[False for _ in range(w)] for _ in range(h)]
    steps = 0
    path_stack = []

    def backtrack(y, x):
        nonlocal steps
        if steps > max_steps or len(paths) >= k:
            return
        steps += 1

        if (y, x) == end:
            paths.append(path_stack[:] + [(y, x)])
            return

        visited[y][x] = True
        path_stack.append((y, x))

        for ny, nx in neighbors(grid, y, x):
            if not visited[ny][nx]:
                backtrack(ny, nx)

        path_stack.pop()
        visited[y][x] = False

    sy, sx = start
    backtrack(sy, sx)
    return paths
