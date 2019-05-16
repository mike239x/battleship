__version__ = '0.1.0'

import multiprocessing
import time
import zmq
import numpy as np
from enum import Enum, auto

from scipy.ndimage.morphology import binary_dilation

FIELD_SIZE = (10,10) # width, height
SHIP_SIZES = [5,4,4,3,3,3,2,2,2,2]

# place the ships on the battlefield
#
# input: list in form [((x,y), HOR), ...]
# where (x,y) is the position of the top-left corner of the ship
# (the top-left corner of the field has coords (0,0))
# and HOR and a boolean indicating if the ship of positioned horizontally or not
#
# returns a tuple with success flag and
# numpy array with 0s for empty cells and 1s for ship parts
def place_ships(ships):
    re = np.zeros(FIELD_SIZE, dtype = np.uint8)
    success = True
    for i in range(len(SHIP_SIZES)):
        ship_tiles = np.zeros(FIELD_SIZE)
        x = ships[i][0][0]
        y = ships[i][0][1]
        hor = ships[i][1]
        for _ in range(SHIP_SIZES[i]):
            if x < 0 or x >= FIELD_SIZE[0] or y < 0 or y >= FIELD_SIZE[1]:
                success = False
                break
            ship_tiles[y,x] = 1
            if hor:
                x+=1
            else:
                y+=1
        if not success:
            break
        s = np.full((3,3), True)
        surround_tiles = binary_dilation(ship_tiles, structure = s)
        if not all(re[surround_tiles == 1] == 0):
            success = False
            break
        re[ship_tiles == 1] = 1
    return (success, re)

class Client:
    def __init__(self):
        pass
    def start():
        pass

class Server:
    def __init__(self):
        pass
    def start():
        pass

class World:
    def __init__(self):
        n = 10
        self.my_board = np.zeros((n,n))
        self.opponent_board = np.zeros((n,n))

class Player:
    # init the board and do whatever else you want to do at the start
    def init():
        pass
    # chose your next move given the current state
    def make_a_move():
        pass
