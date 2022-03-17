import pygame as pg
import os
from classes import Tile, Board, Vertex

LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


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
        step = (board.cell_size + board.cell_spacing) / 50
        for i in range(50):
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
    #
    # Testing simple case...
    #
    tiles = {}
    setup_string = """
......
..AA..
..AA..
. BC .
......
"""
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

    move_list = [("B", "L"), ("C", "R"), ("A", "D")]
    animate_solution(board, tiles, move_list)
