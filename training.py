from battleship import *
from Ui import run_on_console

agent = SuperAgent()

success, field = place_ships(load_ships("ships/00000042.pos"))

def callback(*args):
    agent.train(*args)

for i in range(1000):
    g = mini_battle(agent, field)
    sample_Q(g, callback)

agent.model_save('superagent_weights')

#  g = mini_battle(agent, field)
#  run_on_console(g, 500)
