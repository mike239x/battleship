__version__ = '0.1.0'

import multiprocessing
import time
import zmq
import numpy as np
from enum import Enum

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
# returns a tuple (success, field) with success flag and
# numpy array with 0s for empty cells and non-zeros for other ships
# where `field == k` is the k-th ship
def place_ships(ships):
    re = np.zeros(FIELD_SIZE, dtype = np.uint8)
    success = True
    k = 1
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
        re[ship_tiles == 1] = k
        k += 1
    return (success, re)

class ActionResult(Enum):
    ILLEGAL_MOVE = -2
    REPEATING_MOVE = -1
    MISS = 0
    HIT = 1
    SUNK = 2

# probes a position `pos` of the opponent's `field`.
# previous probed positions are provided in by `probed`.
# returns ActionResult
def probe(pos, probed, field):
    x,y = pos
    if x < 0 or x >= FIELD_SIZE[0] or y < 0 or y >= FIELD_SIZE[1]:
        return ActionResult.ILLEGAL_MOVE
    if probed[y][x]:
        return ActionResult.REPEATING_MOVE
    ship_id = field[y][x]
    probed[y][x] = True
    if ship_id == 0:
        return ActionResult.MISS
    if all(probed[field == ship_id]):
        return ActionResult.SUNK
    else:
        return ActionResult.HIT

# a class to represent a player state
# `probed` keeps track of the squares which the players probes in his turns
# while `field` has all the ships
class Player:
    def __init__(self):
        self.probed = np.zeros(FIELD_SIZE, dtype=np.bool)
        self.field = np.zeros(FIELD_SIZE)

class Client:
    def __init__(self, agent):
        self.agent = agent
        # TODO idea: make a hard check on init that agent would place ships properly, if not - break immediately
    def start(self):
        self.field = agent.place_ships()
        # TODO send the ship placement to the server
        while True:
            # TODO get a msg from the server
            ...
            my_turn = True
            if my_turn:
                # TODO timeouts?
                # TODO ask the agent for a turn
                ...
                # TODO send the info to the server
                ...

class Server:
    def __init__(self, allow_illegal_moves = False, allow_repeating_moves = False):
        self.players = (Player(), Player())
        self.allow_illegal_moves = allow_illegal_moves
        self.allow_repeating_moves = allow_repeating_moves
    def start(self):
        # TODO get both players connected and get their ships dispositions
        ...
        # main game loop:
        cur = 0 # id of the active player
        while True:
            # TODO get a move from a current player and store it in (x,y)
            pos = (0,0)
            x,y = pos
            re = probe(pos, self.players[cur].probed, self.players[1-cur].field)
            if re == ActionResult.ILLEGAL_MOVE:
                if allow_illegal_moves:
                    cur = 1 - cur
                else:
                    # TODO kill the active player
                    ...
            elif re == ActionResult.REPEATING_MOVE:
                if allow_repeating_moves:
                    cur = 1 - cur
                else:
                    # TODO kill the active player
                    ...
            elif re == ActionResult.MISS:
                self.players[cur].probed[y][x] = True
                cur = 1 - cur
            elif re == ActionResult.HIT:
                self.players[cur].probed[y][x] = True
            elif re == ActionResult.SUNK:
                self.players[cur].probed[y][x] = True
                if all(self.players[cur].probed[self.players[1-cur].field > 0]):
                    # TODO active player won
                    ...
            # TODO broadcast updates
            ...
        # end of the main game loop
        # TODO gracefully shutdown? or keep going?

class Agent:
    # init the board and do whatever else you want to do at the start
    def init():
        pass
    # place your ships
    def place_ships():
        return [((0,0), False) * 10]
    # chose your next move given the current state
    def make_a_move():
        pass
