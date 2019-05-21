__version__ = '0.1.0'

from multiprocessing import Process
import pickle
import time
import zmq
import numpy as np
from enum import Enum
from scipy.ndimage.morphology import binary_dilation

FIELD_SIZE = (10,10) # width, height
SHIP_SIZES = [5,4,4,3,3,3,2,2,2,2]

class Msg(Enum):
    ILLEGAL_MOVE = -2
    REPEATING_MOVE = -1
    MISS = 0
    HIT = 1
    SUNK = 2
    CONFIRMED = 3
    YOU_WON = 4
    YOU_LOST = 5
    YOUR_TURN = 6

######################################################################################################################

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

######################################################################################################################

class Player:
    '''a class to represent a player state
    `probed` keeps track of the squares which the players probes in his turns
    while `field` has all the ships
    '''
    def __init__(self):
        self.probed = np.zeros(FIELD_SIZE, dtype=np.bool)
        self.field = np.zeros(FIELD_SIZE)

######################################################################################################################

class Client:
    def __init__(self, agent):
        self.agent = agent
        # TODO idea: make a hard check on init that agent would place ships properly, if not - break immediately
        self.ships = agent.place_ships()
        self.field = place_ships(self.ships)
        assert(self.field[0]) # success
        self.field = self.field[1]

    def start(self):
        #TODO do something with ports
        port = "tcp://127.0.0.1:5555"
        self.socket = context.socket(zmq.PAIR)
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

class Server:
    def __init__(self, allow_illegal_moves = False, allow_repeating_moves = False):
        self.players = (Player(), Player())
        self.allow_illegal_moves = allow_illegal_moves
        self.allow_repeating_moves = allow_repeating_moves

    def start(self):
        # TODO get both players connected and get their ships dispositions
        port1 = "tcp://127.0.0.1:5555"
        port2 = "tcp://127.0.0.1:5556"
        ...
        context = zmq.Context()
        self.sockets = []
        sock = context.socket(zmq.PAIR)
        sock.bind(port1)
        self.sockets.append(sock)
        sock = context.socket(zmq.PAIR)
        sock.bind(port2)
        self.sockets.append(sock)
        self.force_stop()
        self.process = Process(target = self.run, args = ())
        self.process.start()

    def force_stop(self):
        if self.process != None:
            self.process.terminate()

    def announce_winner(self, winner):
        # write to the winner
        self.sockets[winner].send_string("You won")
        # get response
        msg = self.sockets[winner].recv()
        assert(msg == CONFIRMED)
        # write to the loser
        self.sockets[1-winner].send_string("You lost")
        # get response
        msg = self.sockets[1-winner].recv()
        assert(msg == CONFIRMED)

    def run(self):
        cur = 0 # id of the active player
        finished = False
        # main game loop:
        while not finished:
            # ask the active player for a move:
            self.sockets[cur].send_string("Your turn")
            # TODO give it X seconds for thinking
            # get its response
            msg = self.sockets[cur].recv()
            pos = pickle.loads(msg)
            x,y = pos
            re = probe(pos, self.players[cur].probed, self.players[1-cur].field)
            # reply to the player of the action result
            self.sockets[cur].send(pickle.dumps(re))
            # get comfirmation
            msg = self.sockets[cur].recv()
            assert (msg == CONFIRMED)
            if re == Msg.ILLEGAL_MOVE:
                cur = 1 - cur
                if not self.allow_illegal_moves:
                    self.announce_winner(1-cur)
                    finished = True
            elif re == Msg.REPEATING_MOVE:
                cur = 1 - cur
                if not self.allow_repeating_moves:
                    self.announce_winner(1-cur)
                    finished = True
            elif re == Msg.MISS:
                self.players[cur].probed[y][x] = True
                cur = 1 - cur
            elif re == Msg.HIT:
                self.players[cur].probed[y][x] = True
            elif re == Msg.SUNK:
                self.players[cur].probed[y][x] = True
                if all(self.players[cur].probed[self.players[1-cur].field > 0]):
                    self.announce_winner(cur)
                    finished = True
                    # TODO shall we play till the end after the first one finished?
            # TODO broadcast updates into outer space?
        # end of the main game loop

######################################################################################################################

class Agent:
    '''a template for an agent class'''
    # generate a ship placement
    def place_ships(self):
        raise NotImplementedError
    # make a move:
    def make_a_move(self):
        raise NotImplementedError
    # called after the move was made
    def respond(self, result):
        raise NotImplementedError
    # called at the end of the game
    def finish(self, result):
        raise NotImplementedError


