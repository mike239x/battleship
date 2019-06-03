import battleship as bs

from random import randint, getrandbits
from itertools import count
import pickle

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

for i in count():
    filename = "{:>08}.pos".format(i)
    with open(filename, 'wb') as f:
        pickle.dump(generate_ships(), f)
    print(i)
