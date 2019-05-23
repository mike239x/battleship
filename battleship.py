__version__ = '0.1.0'

from multiprocessing import Process
import pickle
import time
import zmq
import numpy as np
from enum import Enum
from scipy.ndimage.morphology import binary_dilation

######################################################################################################################
# some constants

FIELD_SIZE = (10,10) # width, height
SHIP_SIZES = [5,4,4,3,3,3,2,2,2,2]

class Msg(Enum):
    ILLEGAL_MOVE = -2
    REPEATING_MOVE = -1
    MISS = 0
    HIT = 1
    SUNK = 2
    WON = 3
    LOST = 4
    CONFIRMED = 5
    PLACE_SHIPS = 6
    YOUR_TURN = 7

class DefaultRules:
    allow_illegal_moves = False
    allow_repeating_moves = True
    max_turns = 100

######################################################################################################################
# game machanics

def place_ships(ships):
    '''place the ships on the battlefield
    input: list in form [((x,y), HOR), ...]
    where (x,y) is the position of the top-left corner of the ship
    (the top-left corner of the field has coords (0,0))
    and HOR and a boolean indicating if the ship of positioned horizontally or not
    return: a tuple (success, field) with success flag and
    numpy array with 0s for empty cells and non-zeros for other ships
    where `field == k` is the k-th ship
    '''
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

def probe(pos, probed, field):
    '''probes a position `pos` of the opponent's `field`.
    previous probed positions are provided in by `probed`.
    returns a message: ILLEGAL_MOVE, REPEATING_MOVE, MISS, HIT or SUNK
    '''
    x,y = pos
    if x < 0 or x >= FIELD_SIZE[0] or y < 0 or y >= FIELD_SIZE[1]:
        return Msg.ILLEGAL_MOVE
    if probed[y][x]:
        return Msg.REPEATING_MOVE
    ship_id = field[y][x]
    probed[y][x] = True
    if ship_id == 0:
        return Msg.MISS
    if all(probed[field == ship_id]):
        return Msg.SUNK
    else:
        return Msg.HIT

class Agent:
    '''a template for an agent class'''
    # generate a ship placement
    def ships(self):
        raise NotImplementedError
    # make a move:
    def make_a_move(self):
        raise NotImplementedError
    # called after the move was made
    def give(self, response):
        raise NotImplementedError
    # called at the end of the game
    def finish(self, result):
        raise NotImplementedError

def battle(player0, player1, rules):
    '''play the game between two agents'''
    players = (player0, player1)
    probed = tuple(np.zeros(FIELD_SIZE, dtype = np.bool) for _ in range(2))
    ships = tuple(np.zeros(FIELD_SIZE) for _ in range(2))
    success, ships[0] = place_ships(player0.ships())
    if not success:
        return
    success, ships[1] = place_ships(player1.ships())
    if not success:
        return
    cur = 0 # id of the active player
    turn_num = 0
    while turn_num != rules.max_turns:
        x,y = players[cur].make_a_move()
        # TODO give it X seconds for thinking
        response = probe(pos, probed[cur], ships[1-cur])
        players[cur].give(response)
        if response == Msg.ILLEGAL_MOVE:
            cur = 1 - cur
            if not rules.allow_illegal_moves:
                break
        elif response == Msg.REPEATING_MOVE:
            cur = 1 - cur
            if not rules.allow_repeating_moves:
                break
        elif response == Msg.MISS:
            probed[cur][y][x] = True
            cur = 1 - cur
        elif response == Msg.HIT:
            probed[cur][y][x] = True
        elif response == Msg.SUNK:
            probed[cur][y][x] = True
            if all(probed[cur][ships[1-cur] > 0]):
                break
        # TODO broadcast updates into outer space?
        turn_num += 1
    # end of the main game loop
    players[cur].finish(Msg.WON)
    players[1-cur].finish(Msg.LOST)
    # TODO shall we somehow play till the end after one of the players finished?

######################################################################################################################
# networking

class RemoteAgent(Agent):
    def __init__(self, socket):
        self.socket = socket
    # generate a ship placement
    def ships(self):
        self.socket.send(pickle.dumps(Msg.PLACE_SHIPS))
        ships = pickle.loads(self.socket.recv())
        return ships
    # make a move:
    def make_a_move(self):
        self.socket.send(pickle.dumps(Msg.YOUR_TURN))
        move = pickle.loads(self.recv())
        return move
    # called after the move was made
    def give(self, response):
        self.socket.send(pickle.dumps(response))
        # self.recv()
    # called at the end of the game
    def finish(self, result):
        self.socket.send(pickle.dumps(response))
        # self.recv()

class Server:
    pass # TODO

# TODO
class Client:
    def __init__(self, agent, socket):
        self.agent = agent
        self.socket = socket

    def start(self):
        #TODO do something with ports
        port = "tcp://127.0.0.1:5555"
        self.socket = zmq.Context.socket(zmq.PAIR)
        self.socket.connect(port)
        self.force_stop()
        self.process = Process(target = self.run, args = ())
        self.process.start()

    def force_stop(self):
        if self.process != None:
            self.process.terminate()

    def run(self):
        # main game loop:
        while True:
            # TODO get a msg from the server
            msg = self.socket.recv()
            if msg == Msg.YOUR_TURN:
                # TODO spawn a separate process for that?
                pos = self.agent.make_a_move()
                data = pickle.dumps(pos)
                self.socket.send(data)
                msg = self.socket.recv()
                data = pickle.loads(msg)
                # TODO inform agent about the result
                self.socket.send(Msg.CONFIRMED)
            elif msg == Msg.YOU_LOST:
                self.socket.send(Msg.CONFIRMED)
            elif msg == Msg.YOU_WON:
                self.socket.send(Msg.CONFIRMED)
        # end of the main game loop

######################################################################################################################
# misc
