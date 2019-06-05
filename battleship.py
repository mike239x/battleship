__version__ = '0.1.0'

from multiprocessing import Process
import pickle
import time
import zmq
import numpy as np
from enum import Enum
from scipy.ndimage.morphology import binary_dilation
from random import randint, getrandbits, shuffle
from skimage.measure import label
from copy import deepcopy
from itertools import count
import torch
from torch import nn

######################################################################################################################
# some constants

FIELD_SIZE = (10,10) # width, height
FIELD_HEIGHT, FIELD_WIDTH = FIELD_SIZE
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
    YOU_LOST = 8
    YOU_WON = 9

class DefaultRules:
    illegal_moves = [Msg.ILLEGAL_MOVE, Msg.REPEATING_MOVE]
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
    # TODO use enumerate here
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

def load_ships(filename):
    with open(filename, 'rb') as f:
        ships = pickle.load(f)
    return ships

def save_ships(filename):
    with open(self.filename, 'wb') as f:
        ships = pickle.dump(f)

def load_random_ships():
    ... # TODO

def probe(pos, probed, field):
    '''probes a position `pos` of the opponent's `field`.
    previous probed positions are provided in by `probed`.
    returns a message: ILLEGAL_MOVE, REPEATING_MOVE, MISS, HIT or SUNK
    '''
    x,y = pos
    if x < 0 or x >= FIELD_SIZE[0] or y < 0 or y >= FIELD_SIZE[1]:
        return Msg.ILLEGAL_MOVE
    if probed[y,x]:
        return Msg.REPEATING_MOVE
    ship_id = field[y,x]
    probed[y,x] = True
    if ship_id == 0:
        return Msg.MISS
    if all(probed[field == ship_id]):
        return Msg.SUNK
    else:
        return Msg.HIT

class Agent:
    '''a template for an agent class'''
    # make a move:
    def make_a_move(self):
        raise NotImplementedError
    # called after the move was made
    def give(self, response):
        raise NotImplementedError

class Dict(dict):
    def __init__(self, **kwargs):
        super().__init__(kwargs)
        self.__dict__ = self

def mini_battle(player, field, rules = DefaultRules()):
    probed = np.zeros(FIELD_SIZE, dtype = np.bool)
    for turn_num in count():
        pos = player.make_a_move()
        x,y = pos
        # TODO give it X seconds for thinking
        response = probe(pos, probed, field)
        player.give(response)
        if response != Msg.ILLEGAL_MOVE:
            probed[y,x] = True
        yield Dict(turn_num = turn_num, pos = pos, response = response)
        if response in rules.illegal_moves or turn_num == rules.max_turns:
            yield Dict(turn_num = turn_num, pos = pos, response = Msg.YOU_LOST)
            break
        if all(probed[field > 0]):
            yield Dict(turn_num = turn_num, pos = pos, response = Msg.YOU_WON)
            break
    while True:
        yield None

def battle(players, rules = DefaultRules()):
    '''play the game between two agents'''
    games = []
    success, field = place_ships(players[0].ships)
    if success:
        games.append(mini_battle(players[1], field, rules))
    success, field = place_ships(players[1].ships)
    if success:
        games.append(mini_battle(players[0], field, rules ))
    finished = [False] * len(games)
    cur = 0 # id of the active game
    while True:
        progress = next(games[cur])
        if progress == None:
            # TODO kill current game
            finished[cur] = True
            if all(finished): # if playing till first one win/lose which `all` to `any`
                break
            cur = (cur+1) % len(games)
            continue
        else:
            yield Dict(current_player_id = cur, **progress)
            if progress.response not in [Msg.HIT, Msg.SUNK]:
                cur = (cur+1) % len(games)
    while True:
        yield None

######################################################################################################################
# networking

#  class RemoteAgent(Agent):
#      def __init__(self, socket):
#          self.socket = socket
#      # generate a ship placement
#      def ships(self):
#          self.socket.send(pickle.dumps(Msg.PLACE_SHIPS))
#          ships = pickle.loads(self.socket.recv())
#          return ships
#      # make a move:
#      def make_a_move(self):
#          self.socket.send(pickle.dumps(Msg.YOUR_TURN))
#          move = pickle.loads(self.recv())
#          return move
#      # called after the move was made
#      def give(self, response):
#          self.socket.send(pickle.dumps(response))
#      # called at the end of the game
#      def finish(self, result):
#          self.socket.send(pickle.dumps(response))

#  def play_remotely(agent, port):
#      socket = zmq.Context().socket(zmq.PAIR)
#      socket.connect(port)
#      while True:
#          msg = socket.recv()
#          if msg == Msg.PLACE_SHIPS:
#              ships = agent.ships()
#              socket.send(pickle.dumps(ships))
#          elif msg == Msg.YOUR_TURN:
#              pos = agent.make_a_move()
#              socket.send(pickle.dumps(pos))
#              msg = socket.recv()
#              response = pickle.loads(msg)
#              agent.give(response)
#              socket.send(Msg.CONFIRMED)
#          elif msg == Msg.YOU_LOST:
#              socket.send(Msg.CONFIRMED)
#              break
#          elif msg == Msg.YOU_WON:
#              socket.send(Msg.CONFIRMED)
#              break

######################################################################################################################
# misc

class SmartAgent(Agent):
    '''a sophisticated algorithm'''
    def __init__(self, ships = None):
        self.field = np.zeros(FIELD_SIZE)
        self.ships_tiles_uncovered = 0
        self.anchor = (-1,-1)
        self.dir = (0,0)
        self.good_moves = []
        self.ships = ships
    # make a move:
    def make_a_move(self):
        if self.ships_tiles_uncovered == 0:
            # search for another ship
            # randomly choose a new point following a checkerboard pattern:
            while True:
                x = randint(0, FIELD_WIDTH - 1)
                y = 2 * randint(0, FIELD_HEIGHT/2 - 1) # requires field height to be divisable by 2
                if x % 2 == 1:
                    y += 1
                if self.field[y,x] == 0:
                    break
        else:
            if self.ships_tiles_uncovered == 1:
                # choose a direction in which to go on with shooting:
                l_max = 0
                for dx,dy in [(0,1),(1,0),(0,-1),(-1,0)]:
                    x,y = self.anchor
                    for l in count():
                        x+=dx
                        y+=dy
                        if x not in range(FIELD_WIDTH) or y not in range(FIELD_HEIGHT):
                            break
                        if self.field[y,x] != 0:
                            break
                    if l > l_max:
                        l_max = l
                        self.dir = (dx,dy)
            x,y = self.good_moves[-1]
            dx,dy = self.dir
            x += dx
            y += dy
            if x not in range(FIELD_WIDTH) or y not in range(FIELD_HEIGHT) or self.field[y,x] != 0:
                # change direction and start from anchor
                dx = -dx
                dy = -dy
                self.dir = (dx,dy)
                x,y = self.anchor
                x += dx
                y += dy
        self.good_moves.append((x,y))
        return self.good_moves[-1]
    # called after the move was made
    def give(self, response):
        x,y = self.good_moves[-1]
        if response == Msg.MISS:
            self.field[y,x] = -1
            self.good_moves.pop()
        if response == Msg.SUNK:
            self.field[y,x] = 1
            sunk_ship = np.zeros(FIELD_SIZE, dtype = np.bool)
            for x,y in self.good_moves:
                sunk_ship[y,x] = True
            surrondings = binary_dilation(sunk_ship)
            self.field[surrondings] = -1
            self.field[sunk_ship] = 1
            self.ships_tiles_uncovered = 0
            self.good_moves = []
        if response == Msg.HIT:
            if self.ships_tiles_uncovered == 0:
                self.anchor = (x,y)
                self.dir = (0,0)
            self.field[y,x] = 1
            self.ships_tiles_uncovered += 1

class RandomAgent(Agent):
    '''a not so sophisticated algorithm'''
    def __init__(self, ships = None):
        self.field = np.zeros(FIELD_SIZE)
        self.good_moves = []
        self.ships = ships
    # make a move:
    def make_a_move(self):
        # search for another ship
        # randomly choose a new point following a checkerboard pattern:
        while True:
            x = randint(0, FIELD_WIDTH - 1)
            y = randint(0, FIELD_HEIGHT - 1)
            if self.field[y,x] == 0:
                break
        self.good_moves.append((x,y))
        return self.good_moves[-1]
    # called after the move was made
    def give(self, response):
        x,y = self.good_moves[-1]
        if response == Msg.MISS:
            self.field[y,x] = -1
        if response == Msg.SUNK or response == Msg.HIT:
            self.field[y,x] = 1
        self.good_moves.pop()

def update_visible_ships(visible, pos, response):
    x,y = pos
    if response == Msg.MISS:
        visible[y,x] = 1
    elif response == Msg.HIT:
        visible[y,x] = 2
    elif response == Msg.SUNK:
        visible[y,x] = 2
        ships = label(visible, background = 0)
        visible[ships == ships[y,x]] = 3
    return visible

def sample_Q(minigame, callback, discount = 0.02):
    field = np.zeros(FIELD_SIZE)
    fields = [deepcopy(field)]
    actions = []
    rewards = []
    reward_ = {}
    reward_[Msg.SUNK] = 1
    reward_[Msg.HIT] = 1
    reward_[Msg.MISS] = 0
    reward_[Msg.REPEATING_MOVE] = -10
    reward_[Msg.ILLEGAL_MOVE] = -100
    for progress in minigame:
        if progress.response in ( Msg.YOU_WON, Msg.YOU_LOST ):
            break
        update_visible_ships(field, progress.pos, progress.response)
        fields.append(deepcopy(field))
        actions.append(progress.pos)
        rewards.append(reward_[progress.response])
    fields.pop()
    return_ = 0
    actions.reverse()
    fields.reverse()
    rewards.reverse()
    for action, field, reward in zip(actions, fields, rewards):
        return_ *= 1.0 - discount
        return_ += reward
        callback(field, action, return_)

class SuperAgent(Agent):
    '''an agent driven by inhuman ambitions'''
    def __init__(self, ships = None):
        self.field = np.zeros(FIELD_SIZE, dtype = np.float32)
        self.ships = ships
        n_in, n_h, n_out = 100, 40, 100
        self.model = nn.Sequential(
                         nn.Linear(n_in, n_h),
                         nn.ReLU(),
                         nn.Linear(n_h, n_out),
                         nn.ReLU())
    def model_load(self, path):
        self.model.load_state_dict(torch.load(path))
        self.model.eval()
    def model_save(self, path):
        torch.save(self.model.state_dict(), path)
    # train agent
    def train(self, field, action, return_):
        returns_ = self.model(torch.from_numpy(field.flatten().astype(np.float32)))
        x, y = action
        criterion = torch.nn.MSELoss()
        loss = criterion(returns_[y*FIELD_WIDTH + x], torch.from_numpy(np.array([return_], dtype = np.float32)))
        optimizer = torch.optim.SGD(self.model.parameters(), lr=0.01)
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
    # make a move:
    def make_a_move(self):
        returns_ = self.model(torch.from_numpy(self.field.flatten())).detach().numpy()
        pos = np.unravel_index(returns_.argmax(), FIELD_SIZE)
        self.last_move = pos
        return pos
    # called after the move was made
    def give(self, response):
        update_visible_ships(self.field, self.last_move, response)

