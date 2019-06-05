from battleship import *
from Ui import run_on_console

agent = SuperAgent()

success, field = place_ships(load_ships("ships/00000042.pos"))

def callback(*args):
    agent.train(*args)

n = 10**4

torch.set_printoptions(profile="full")
np.set_printoptions(precision = 3, suppress=True)

def run(g):
    for p in g:
        if p == None:
            break
        print(p)
def store_params(filename):
    with open(filename, 'w') as f:
        f.write(str(agent.model.state_dict()))

agent.exploration_rate = 0.5
for i in range(n):
    if i % (n//10) == 0:
        agent.verbose = True
        print()
        g = mini_battle(agent, field)
        run(g)
        agent.exploration_rate /= 1.4
        agent.verbose = False
        agent.field *= 0
    g = mini_battle(agent, field)
    sample_Q(g, callback, discount = 0.5)
    agent.field *= 0

agent.model_save('superagent_weights')
