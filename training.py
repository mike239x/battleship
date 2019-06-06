from battleship import *
from Ui import run_on_console

agent = SuperAgent()
agent.model_load('superagent_weights')

def callback(*args):
    agent.train(*args)

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
    for _ in range(10**1):
        _, field = place_ships(load_random_ships())
        agent.exploration_rate = 0.2
        g = mini_battle(agent, field, soft_rules)
        sample_Q(g, callback, discount = 0.5)
        agent.field *= 0
        g = mini_battle(SmartAgent(), field, soft_rules)
        sample_Q(g, callback, discount = 0.5)
    agent.exploration_rate = 0.0
    agent.verbose = True
    print()
    g = mini_battle(agent, field)
    run(g)
    agent.verbose = False
    agent.field *= 0
    agent.model_save('superagent_weights')

