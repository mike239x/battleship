import os
import pickle

import battleship

for fname in os.listdir("ships"):
    with open(os.path.join("ships", fname), "rb") as infile:
        try:
            ships = pickle.load(infile)
            result, _ = battleship.place_ships(ships)
            if not result:
                print("Invalid ship configuration: ", fname, ships)
        except:
            print("Ivalid file", fname)
