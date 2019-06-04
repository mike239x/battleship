import battleship as bs

from random import randint, getrandbits
from itertools import count
import pickle
import sys

def generate_ships():
    while True:
        ships = []
        for l in bs.SHIP_SIZES:
            hor = bool(getrandbits(1))
            if hor:
                x = randint(0, bs.FIELD_WIDTH-l)
                y = randint(0, bs.FIELD_HEIGHT-1)
            else:
                x = randint(0, bs.FIELD_WIDTH-1)
                y = randint(0, bs.FIELD_HEIGHT-l)
            ships.append(((x,y), hor))
        success, field = bs.place_ships(ships)
        if success:
            break
    return ships

if __name__ == '__main__':
    n = 0
    if len(sys.argv) > 1:
        n = int(sys.argv[1])
    for i in count(n):
        ships = generate_ships()
        filename = "{:>08}.pos".format(i)
        with open(filename, 'wb') as f:
            pickle.dump(ships, f)
        print(i)