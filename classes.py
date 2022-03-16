from collections import defaultdict

LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


class Tile:
    def __init__(self, id: str, r: str, c: str, h: str, w: str):
        self.id = id
        self.r = r
        self.c = c
        self.h = h
        self.w = w

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
    def __init__(
        self, id: int, parent_id: int, tile_id: str, dir: str, state: str, pickled: str
    ):
        self.id = id
        self.parent_id = parent_id
        self.tile_id = tile_id
        self.dir = dir  # direction to get here from parent
        self.state = state
        self.pickled = pickled  # pickled tuple of (board, tiles)
        # self.a_loc = a_loc  # (row, col) of the A-tile upper left
