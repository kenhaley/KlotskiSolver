import pygame as pg
import os
from classes import Tile, Board, Vertex

LETTERS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'

def animate_solution(board, tiles, move_list):
    pg.init()
    # calculate screen size and draw screen and board.

    # specs...
    tile_speed = 1
    fps = 60
    board.cell_size = 100
    board.cell_spacing = 20
    board.height = len(board.arr)-2
    board.width = len(board.arr[0])-2
    frame_height = board.cell_size * board.height + board.cell_spacing * (board.height)
    frame_width = board.cell_size * board.width + board.cell_spacing * (board.width)

    # draw background & board based on board size...
    frame = pg.Rect(10,10, frame_width, frame_height)
    screen_size = scr_w, scr_h = (frame_width + 20, frame_height + 20)
    os.environ['SDL_VIDEO_WINDOW_POS'] = f'{pg.display.Info().current_w - scr_w - 10},40'
    background = pg.Surface(screen_size)
    background.fill('BLACK')
    pg.draw.rect(background, (50,50,50), frame)
    pg.display.set_caption("Klotski")
    screen = pg.display.set_mode(screen_size)
    screen.blit(background, (0,0))



    running = True
    speed = 0 # User must press space to start.
    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    running = False
                if event.key == pg.K_SPACE:
                    speed = tile_speed - speed  # toggle speed between 0 and TILE_SPEED
                if event.key == pg.K_UP:
                    fps += 50
                    if fps > 1000:
                        fps = 1000
                if event.key == pg.K_DOWN:
                    fps -= 50
                    if fps < 1:
                        fps = 1
        if not running:
            break
        screen.blit(background, (0,0))
        draw_tiles(screen, board, tiles)
        pg.display.update()
        pg.time.Clock().tick(fps)
    pg.quit()
    return

def draw_tiles(screen, board, tiles):
    for row in range(board.height):
        for col in range(board.width):
            left = col * board.cell_size + board.cell_spacing * (col+1)
            top = row * board.cell_size + board.cell_spacing * (row+1)
            width = height = board.cell_size
            test = pg.Rect(left, top, width, height)
            pg.draw.rect(screen,"RED", test)





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
    setup_array = [x for x in setup_string.split('\n') if x.strip() != '']  # dropping empty lines

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

    move_list = [('B', 'L'), ('C', 'R'), ('A', 'D')]
    animate_solution(board, tiles, move_list)