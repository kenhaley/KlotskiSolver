from collections import defaultdict
import pygame as pg
import os
import sys
import pickle


LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
MOVE_DICT = {
    "L": (0, -1),
    "R": (0, 1),
    "U": (-1, 0),
    "D": (1, 0),
    "L2": (0, -2),
    "R2": (0, 2),
    "U2": (-2, 0),
    "D2": (2, 0),
}
BACKDICT = {"D": "U", "U": "D", "L": "R", "R": "L", "D2": "U2", "U2": "D2", "L2": "R2", "R2": "L2"}
# Used in backtrack() to reverse move.


""" simple version..."""
setup_string = """
......
..AA..
..AA..
.BC  .
......
"""
goal = (2, 2)  # winning location for A tile (upper left)


""" Simple version 2..."""
setup_string = """
......
. AA .
.DAAE.
.FBCG.
......
"""
goal = (2, 2)  # winning location for A tile (upper left)


""" Difficult version """
setup_string = """
......
.BAAC.
.BAAC.
.DEEH.
.DFGH.
.I  J.
......
"""
goal = (4, 2)  # winning location for A tile (upper left)


tiles = {}
current_path = []
dead_ends = []
move_list = []
stack_depth = 0


class Tile:
    def __init__(self, id: str, r: str, c: str, h: str, w: str):
        self.id = id
        self.r = r
        self.c = c
        self.h = h
        self.w = w
        if id == "A":
            self.color = "RED"
        else:
            self.color = (200, 150, 100)

    def __str__(self):
        return self.id + ":" + self.picture()

    def __repr__(self):
        return f"Tile('{self.id}',{self.r},{self.c},{self.h},{self.w})"

    def picture(self) -> str:
        """ includes the id """
        return f"{self.id}.{self.r}.{self.c}.{self.h}.{self.w}"

    def anon_picture(self) -> str:
        """ excludes the id """
        return f"{self.r}.{self.c}.{self.h}.{self.w}"


class Board:
    def __init__(self, setup_array):
        self.tile_loc = defaultdict(list)
        self.arr = []
        for i, row in enumerate(setup_array):
            self.arr.append([])
            for j, cell in enumerate(row):
                self.arr[i].append(cell)
                if cell in LETTERS:
                    self.tile_loc[cell].append((i, j))
        # Drawing/animation specs:
        self.cell_size = 100
        self.cell_spacing = 20
        self.height = len(self.arr) - 2
        self.width = len(self.arr[0]) - 2
        self.frame_height = self.cell_size * self.height + self.cell_spacing * (self.height)
        self.frame_width = self.cell_size * self.width + self.cell_spacing * (self.width)
        return

    def draw(self):
        for row in self.arr:
            for cell in row:
                print(cell, end=" ")
            print()


class Vertex:
    """
    For BFS.  Treating each board position (state) as a vertex in a Graph
    """

    # def __init__(self, id: int, parent_id: int, dir:str, state: str, a_loc: tuple):
    def __init__(self, id: int, parent_id: int, tile_id: str, dir: str, state: str, pickled: str):
        self.id = id
        self.parent_id = parent_id
        self.tile_id = tile_id
        self.dir = dir  # direction to get here from parent
        self.state = state
        self.pickled = pickled  # pickled tuple of (board, tiles)
        # self.a_loc = a_loc  # (row, col) of the A-tile upper left


def is_move_legal(tile: Tile, dir: str) -> bool:
    """
    Check to see if this is a legal move--not blocked by border or other tiles.
    """
    brd = board.arr
    dr, dc = MOVE_DICT[dir]
    try:
        if dc != 0:  # horizontal move...
            for row in range(tile.r, tile.r + tile.h):
                if dc in (1, 2):  # right (either 1 or 2 cells)
                    if brd[row][tile.c + tile.w] != " ":
                        return False
                elif dc in (-1, -2):  # left (either 1 or 2 cells)
                    if brd[row][tile.c - 1] != " ":
                        return False
                if dc == 2:  # right 2 cells
                    if brd[row][tile.c + tile.w + 1] != " ":
                        return False
                elif dc == -2:  # left 2 cells
                    if brd[row][tile.c - 2] != " ":
                        return False
        else:  # vertical move...
            for col in range(tile.c, tile.c + tile.w):
                if dr in (1, 2):  # down (either 1 or 2 cells)
                    if brd[tile.r + tile.h][col] != " ":
                        return False
                elif dr in (-1, -2):  # up (either 1 or 2 cells)
                    if brd[tile.r - 1][col] != " ":
                        return False
                if dr == 2:  # down 2 cells
                    if brd[tile.r + tile.h + 1][col] != " ":
                        return False
                elif dr == -2:  # up 2 cells
                    if brd[tile.r - 2][col] != " ":
                        return False
    except IndexError:
        return False
    return True


def make_move(tile: Tile, dir: str):
    """
    update tile and board to reflect this move
    """
    dr, dc = MOVE_DICT[dir]
    tile.c += dc
    tile.r += dr
    # erase tile on board...
    for row in range(len(board.arr)):
        for col in range(len(board.arr[0])):
            if board.arr[row][col] == tile.id:
                board.arr[row][col] = " "
    # place tile in new location on board...
    for row in range(tile.r, tile.r + tile.h):
        for col in range(tile.c, tile.c + tile.w):
            board.arr[row][col] = tile.id


def state() -> str:
    """
    Returns a string that reflects the state of the board.
    Used to detect if it's been seen/visited before
    """
    # excludes the tile_id (e.g., if two identically shaped tiles swap positions, that's the same state)
    temp = [tile.anon_picture() for _, tile in tiles.items()]
    return "|".join(x for x in sorted(temp))


def solve_DFS():
    # Depth-first search (non-recursive)
    dir = None
    back_dir = None
    while True:
        for id, tile in tiles.items():
            for dir in ("U", "D", "L", "R"):
                if not is_move_legal(tile, dir):
                    continue
                make_move(tile, dir)
                back_dir = BACKDICT[dir]
                cur_state = state()
                if id == "A" and (tile.r, tile.c) == goal:
                    current_path.append(cur_state)
                    move_list.append((tile.id, dir))
                    return True  # solution found!
                if cur_state in current_path or cur_state in dead_ends:
                    make_move(tile, back_dir)  # move back
                else:
                    current_path.append(cur_state)
                    move_list.append((tile.id, dir))
                    return False  # tell caller to keep going from the new position
        # at this point we've detected a dead end...
        dead_ends.append(state())
        last_id, last_dir = move_list.pop()
        make_move(tiles[last_id], BACKDICT[last_dir])
        current_path.pop()
        return False  # keep going


def solve_BFS():
    """
    From Wikipedia Breadth First Search algorithm...
    1  procedure BFS(G, root) is
    2      let Q be a queue
    3      label root as explored
    4      Q.enqueue(root)
    5      while Q is not empty do
    6          v := Q.dequeue()
    7          if v is the goal then
    8              return v
    9          for all edges from v to w in G.adjacentEdges(v) do
    10              if w is not labeled as explored then
    11                  label w as explored
    12                  Q.enqueue(w)
    """

    global initial_state, board, tiles

    verts = {}  # dictionary of vertices; keys assigned are 0,1,2,3...
    # verts[0] is the root (initial state)
    t = tiles["A"]
    pickled = pickle.dumps((board, tiles))

    verts[0] = v = Vertex(0, None, "", "", initial_state, pickled)
    next_v_id = 0
    """ let Q be a queue """  # see below
    """ label root as explored"""
    explored = {v.state}  # using set for fast searching...
    """ Q.enqueue(root) """
    Q = [v]
    """ while Q is not empty do """
    while len(Q) > 0:
        """ v := Q.dequeue()"""
        v = Q.pop(0)
        # now we have to set the board and tiles to match what's in v...
        board, tiles = pickle.loads(v.pickled)
        """ if v is the goal then """
        t = tiles["A"]
        if (t.r, t.c) == goal:
            """ return v """
            return (
                verts,
                v.id,
            )  # we return the verts dict, and the id of the vertex that reached the goal.
        """ for all edges from v to w in G.adjacentEdges(v) do """
        for tile_id, tile in tiles.items():
            for dir in ("U", "D", "L", "R", "U2", "D2", "L2", "R2"):
                if is_move_legal(tile, dir):
                    make_move(tile, dir)
                    cur_state = state()
                    """ if w is not labeled as explored then """
                    if cur_state not in explored:
                        """ label w as explored """
                        next_v_id += 1
                        pickled = pickle.dumps((board, tiles))
                        verts[next_v_id] = w = Vertex(
                            next_v_id, v.id, tile_id, dir, cur_state, pickled
                        )
                        explored.add(cur_state)
                        """ Q.enqueue(w) """
                        Q.append(w)
                    make_move(tile, BACKDICT[dir])  # move back
    return None


def main():
    global board, tiles, initial_state
    os.chdir(sys.path[0])  # make current dir = folder containing this script
    setup_array = [x for x in setup_string.split("\n") if x.strip() != ""]  # dropping empty lines

    h = len(setup_array)
    w = len(setup_array[0])
    board = Board(setup_array)

    # Create tiles...
    for id in LETTERS:
        if x := board.tile_loc.get(id):
            upper_left, lower_right = x[0], x[-1]
            r, c = upper_left
            h, w = lower_right[0] - r + 1, lower_right[1] - c + 1
            tiles[id] = Tile(id, r, c, h, w)

    board.draw()
    init_pickle = pickle.dumps((board, tiles))
    ### Depth first... ###############
    # initial_state = state()
    # current_path.append(initial_state)  # Initialize current_path with the initial state
    # while True:
    #     solution_found = solve_DFS()
    #     if solution_found:
    #         break
    #     if state() == initial_state:
    #         print("no solution")
    #         break
    ##################################

    ### Breadth first... #############
    initial_state = state()
    solution_found = solve_BFS()
    if solution_found:
        move_list = []
        verts, id = solution_found
        # Build the move_list from goal (v) back to parent...
        while id:
            v = verts[id]
            move_list.insert(0, (v.tile_id, v.dir))
            id = v.parent_id
        print(f"BFS Graph: {len(verts)} vertices created")
    else:
        print("no solution")
    ##################################

    if solution_found:
        print("Solution found...")
        print(f"{len(move_list)} moves.")
        dd = {
            "L": "<",
            "R": ">",
            "U": "^",
            "D": "v",
            "L2": "<<",
            "R2": ">>",
            "U2": "^^",
            "D2": "vv",
        }
        for x, y in move_list:
            print(f"{x}{dd[y]}", end=" ")
        print()
        board.draw()
        board, tiles = pickle.loads(init_pickle)
        animate_solution(board, tiles, move_list)

    print("done")


def animate_solution(board, tiles, move_list):
    global pg
    pg.init()
    # calculate screen size and draw screen and board.

    # specs...
    tile_speed = 1
    fps = 120

    # draw background & board based on board size...
    frame = pg.Rect(10, 10, board.frame_width, board.frame_height)
    screen_size = scr_w, scr_h = (board.frame_width + 20, board.frame_height + 20)
    os.environ["SDL_VIDEO_WINDOW_POS"] = f"{pg.display.Info().current_w - scr_w - 10},40"
    background = pg.Surface(screen_size)
    background.fill("BLACK")
    pg.draw.rect(background, (50, 50, 50), frame)
    pg.display.set_caption("Klotski")
    screen = pg.display.set_mode(screen_size)
    screen.blit(background, (0, 0))

    running = True
    paused = True
    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    running = False
                if event.key == pg.K_SPACE:
                    paused = not paused
        if not running:
            break
        screen.blit(background, (0, 0))
        draw_tiles(screen, board, tiles, move_list, paused, fps)
        pg.display.update()
        pg.time.Clock().tick(fps)
    pg.quit()
    return


def draw_tiles(screen, board, tiles, move_list, paused, fps):
    global pg
    # for row in range(board.height):
    #     for col in range(board.width):
    #         left = col * board.cell_size + board.cell_spacing * (col + 1)
    #         top = row * board.cell_size + board.cell_spacing * (row + 1)
    #         width = height = board.cell_size
    #         pg.draw.rect(screen, "RED", pg.Rect(left, top, width, height))

    for id, tile in tiles.items():
        col, row = tile.c - 1, tile.r - 1
        tile.pixleft = col * board.cell_size + board.cell_spacing * (col + 1)
        tile.pixtop = row * board.cell_size + board.cell_spacing * (row + 1)
        tile.pixwidth = board.cell_size * (tile.w) + board.cell_spacing * (tile.w - 1)
        tile.pixheight = board.cell_size * (tile.h) + board.cell_spacing * (tile.h - 1)
        rect = pg.Rect(tile.pixleft, tile.pixtop, tile.pixwidth, tile.pixheight)
        pg.draw.rect(screen, tile.color, rect)
    if not paused and len(move_list) > 0:
        # get next move from move list and move the tile.
        id, dir = move_list.pop(0)
        tile = tiles[id]
        if dir == "U":
            tile.r -= 1
        if dir == "D":
            tile.r += 1
        if dir == "L":
            tile.c -= 1
        if dir == "R":
            tile.c += 1
        if dir == "U2":
            tile.r -= 2
        if dir == "D2":
            tile.r += 2
        if dir == "L2":
            tile.c -= 2
        if dir == "R2":
            tile.c += 2
        num_steps = 50
        step = (board.cell_size + board.cell_spacing) / num_steps
        if dir in ("U2", "D2", "L2", "R2"):
            dir = dir[0]
            num_steps *= 2
        for i in range(num_steps):
            # erase where it is
            rect = pg.Rect(tile.pixleft, tile.pixtop, tile.pixwidth, tile.pixheight)
            pg.draw.rect(screen, (50, 50, 50), rect)
            # move one step and redraw
            if dir == "U":
                tile.pixtop -= step
            if dir == "D":
                tile.pixtop += step
            if dir == "L":
                tile.pixleft -= step
            if dir == "R":
                tile.pixleft += step
            rect = pg.Rect(tile.pixleft, tile.pixtop, tile.pixwidth, tile.pixheight)
            pg.draw.rect(screen, tile.color, rect)
            pg.display.update()
            pg.time.Clock().tick(fps)


if __name__ == "__main__":
    main()
