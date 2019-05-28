from battleship import *

field = np.array([
        [0, 0, 0, 3, 3, 3, 3, 0, 0, 0],
        [0, 6, 0, 0, 0, 0, 0, 0, 0, 1],
        [0, 6, 0, 0, 0, 0, 0, 5, 0, 1],
        [0, 6, 0, 0, 7, 7, 0, 5, 0, 1],
        [0, 0, 0, 0, 0, 0, 0, 5, 0, 1],
        [0, 4, 0, 8, 0, 0, 0, 0, 0, 1],
        [0, 4, 0, 8, 0, 0, 0, 0, 0, 0],
        [0, 4, 0, 0, 0, 0, 0, 0, 9, 9],
        [0, 0, 0, 2, 2, 2, 2, 0, 0, 0],
        [10, 10, 0, 0, 0, 0, 0, 0, 0, 0]
        ], dtype=np.uint8)

probed = np.zeros(FIELD_SIZE, dtype = np.bool)

def test_0():
    re = probe((-1,-1), probed, field)
    assert(re == Msg.ILLEGAL_MOVE)
    re = probe((10,10), probed, field)
    assert(re == Msg.ILLEGAL_MOVE)

def test_1():
    re = probe((0,0), probed, field)
    assert(re == Msg.MISS)
    re = probe((9,9), probed, field)
    assert(re == Msg.MISS)

def test_2():
    re = probe((4,3), probed, field)
    assert(re == Msg.HIT)

def test_3():
    probed[4,3] = True
    re = probe((5,3), probed, field)
    assert(re == Msg.SUNK)

def test_4():
    probed[4,3] = True
    probed[3,3] = True
    re = probe((4,3), probed, field)
    assert(re == Msg.REPEATING_MOVE)
    re = probe((3,3), probed, field)
    assert(re == Msg.REPEATING_MOVE)
