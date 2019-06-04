import battleship

import pickle
from random import randint


class RandomAgent(battleship.Agent):
    def __init__(self, ships_filename, find_new=False):
        with open(ships_filename, "rb") as positions:
            self._ships = pickle.load(positions)
            self._attempts = []
            self._find_new = find_new

    def ships(self):
        return self._ships

    def make_a_move(self):
        max_x, max_y = 10, 10
        x, y = randint(0, max_x-1), randint(0, max_y-1)
        while (x,y) in self._attempts:
            x, y = randint(0, max_x-1), randint(0, max_y-1)
        if self._find_new:
            self._attempts.append((x, y))
        return x, y

    # called after the move was made
    def give(self, response):
        # print(response)
        pass

    # called at the end of the game
    def finish(self, result):
        # print(result)
        pass
