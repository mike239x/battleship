from battleship import *

def sample_callback(field, action, return_):
    print('field is', field)
    print('action is', action)
    print('return is', return_)

def test_0():
    agent = SmartAgent("ships/00000118.pos")
    ships = agent.ships()
    success, field = place_ships(ships)
    print(field)
    assert success
    g = mini_battle(agent, field, DefaultRules())
    sample_Q(g, sample_callback)
