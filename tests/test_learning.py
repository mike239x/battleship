from battleship import *

def test_0():
    agent = SuperAgent("ships/00000118.pos")
    ships = agent.ships()
    success, field = place_ships(ships)
    print(field)
    assert success

    def callback(*args):
        agent.train(*args)

    for i in range(5):
        g = mini_battle(agent, field, DefaultRules())
        sample_Q(g, callback)
