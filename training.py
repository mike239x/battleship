from battleship import *
from Ui import run_on_console

agent = SuperAgent()

_, field = place_ships(load_ships("ships/00000042.pos"))

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

soft_rules = DefaultRules()
soft_rules.illegal_moves.pop()

agent.learning_rate = 0.1
while True:
    for _ in range(10**2):
        agent.exploration_rate = 0.5
        _, field = place_ships(load_random_ships())
        g = mini_battle(agent, field, soft_rules)
        sample_Q(g, callback, discount = 0.5)
        agent.field *= 0

    agent.exploration_rate = 0.0
    agent.verbose = True
    print()
    _, field = place_ships(load_random_ships())
    g = mini_battle(agent, field)
    run(g)
    agent.verbose = False
    agent.field *= 0
    agent.model_save('superagent_weights')

