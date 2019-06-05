import battleship as bs

from random import randint, getrandbits
from itertools import count
import pickle
import sys


def get_one_ship(ship_size):
    hor = bool(getrandbits(1))
    if hor:
        x = randint(0, bs.FIELD_WIDTH-ship_size)
        y = randint(0, bs.FIELD_HEIGHT-1)
    else:
        x = randint(0, bs.FIELD_WIDTH-1)
        y = randint(0, bs.FIELD_HEIGHT-ship_size)
    return (x, y), hor


def get_occupied_fields(ship, size):
    (x, y), hor = ship
    if hor:
        return [(x+p, y) for p in range(size)]
    else:
        return [(x, y+p) for p in range(size)]


def get_blocked_fields(ship, size):
    (x, y), hor = ship
    if hor:
        result = [(x+p-1, y-1) for p in range(size+2)]
        result.extend([(x+p-1, y+1) for p in range(size+2)])
        result.extend([(x+p-1, y) for p in range(size+2)])
    else:
        result = [(x-1, y+p-1) for p in range(size+2)]
        result.extend([(x+1, y+p-1) for p in range(size+2)])
        result.extend([(x, y+p-1) for p in range(size+2)])
    return result


def is_ship_compatible(ships, new_ship):
    occupied = list()
    for idx, ship in enumerate(ships):
        occupied.extend(get_blocked_fields(ship, bs.SHIP_SIZES[idx]))
    additional = get_occupied_fields(new_ship, bs.SHIP_SIZES[len(ships)])
    return set(additional).isdisjoint(set(occupied))


def get_all_ships():
    ships = []
    ships_idx = 0
    bad_attempts = 0
    while len(ships) != len(bs.SHIP_SIZES):
        new_ship = get_one_ship(bs.SHIP_SIZES[ships_idx])
        if is_ship_compatible(ships, new_ship):
            print("Add ship", new_ship)
            ships.append(new_ship)
            bad_attempts = 0
        else:
            bad_attempts += 1
            if bad_attempts >= 10:
                print("Pop ship", new_ship)
                ships.pop()
                bad_attempts = 0
    return ships


def write_new_ships(indeces=range(0, 1), dry=False):
    for i in indeces:
        ships = get_all_ships()
        filename = "{:>08}.pos".format(i)
        if dry:
            print(ships)
        else:
            with open(filename, 'wb') as f:
                pickle.dump(ships, f)
        print("Generated {}".format(i))


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-s",
        "--start",
        help="The first index to write the file to",
        type=int,
        default=0
    )
    parser.add_argument(
        "-n",
        "--number-of-ships",
        help="Empty will generate continuesly",
        type=int
    )
    parser.add_argument(
        "-d",
        "--dry",
        help="Only print the results",
        action="store_true",
        default=False
    )

    args = parser.parse_args()

    number_generator = count(args.start) if args.number_of_ships is None else range(
        args.start, args.start + args.number_of_ships)

    write_new_ships(number_generator, args.dry)
