from battleship import *

def test_0():
# some random position
    poses = [
            ((9, 1), False),
            ((3, 8), True),
            ((3, 0), True),
            ((1, 5), False),
            ((7, 2), False),
            ((1, 1), False),
            ((4, 3), True),
            ((3, 5), False),
            ((8, 7), True),
            ((0, 9), True)]
    placement = place_ships(poses)
    assert placement[0] == True
    assert np.all(placement[1] ==
        np.array([
        [0, 0, 0, 1, 1, 1, 1, 0, 0, 0],
        [0, 1, 0, 0, 0, 0, 0, 0, 0, 1],
        [0, 1, 0, 0, 0, 0, 0, 1, 0, 1],
        [0, 1, 0, 0, 1, 1, 0, 1, 0, 1],
        [0, 0, 0, 0, 0, 0, 0, 1, 0, 1],
        [0, 1, 0, 1, 0, 0, 0, 0, 0, 1],
        [0, 1, 0, 1, 0, 0, 0, 0, 0, 0],
        [0, 1, 0, 0, 0, 0, 0, 0, 1, 1],
        [0, 0, 0, 1, 1, 1, 1, 0, 0, 0],
        [1, 1, 0, 0, 0, 0, 0, 0, 0, 0]
        ], dtype=np.uint8))

def test_1():
    poses = [
            ((0, 0), True),
            ((0, 2), True),
            ((0, 4), True),
            ((0, 6), True),
            ((0, 8), True),
            ((7, 0), True),
            ((8, 2), True),
            ((8, 4), True),
            ((8, 6), True),
            ((8, 8), True)]
    placement = place_ships(poses)
    assert placement[0] == True
    assert np.all(placement[1] ==
        np.array([
        [1, 1, 1, 1, 1, 0, 0, 1, 1, 1],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [1, 1, 1, 1, 0, 0, 0, 0, 1, 1],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [1, 1, 1, 1, 0, 0, 0, 0, 1, 1],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [1, 1, 1, 0, 0, 0, 0, 0, 1, 1],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [1, 1, 1, 0, 0, 0, 0, 0, 1, 1],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        ], dtype=np.uint8))

def test_2():
# last ship is not on the board
    poses = [
            ((0, 0), True),
            ((0, 2), True),
            ((0, 4), True),
            ((0, 6), True),
            ((0, 8), True),
            ((7, 0), True),
            ((8, 2), True),
            ((8, 4), True),
            ((8, 6), True),
            ((9, 8), True)]
    placement = place_ships(poses)
    assert placement[0] == False

def test_3():
# last ship too close to another ship
    poses = [
            ((0, 0), True),
            ((0, 2), True),
            ((0, 4), True),
            ((0, 6), True),
            ((0, 8), True),
            ((7, 0), True),
            ((8, 2), True),
            ((8, 4), True),
            ((8, 6), True),
            ((3, 9), True)]
    placement = place_ships(poses)
    assert placement[0] == False
