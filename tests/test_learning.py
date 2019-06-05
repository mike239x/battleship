from battleship import *

def test_0():
    agent = SuperAgent()
    success, field = place_ships(load_ships("ships/00000118.pos"))
    print(field)
    assert success

    def callback(*args):
        agent.train(*args)

    for i in range(5):
        g = mini_battle(agent, field, DefaultRules())
        sample_Q(g, callback)

def test_1():
    agent = SuperAgent(load_ships("ships/00000118.pos"))
    agent.model_save(".test_trained_model.pt")
    agent.model_load(".test_trained_model.pt")
    import os
    os.remove(".test_trained_model.pt")

