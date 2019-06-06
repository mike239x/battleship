from battleship import *
from Ui import run_in_qt, run_on_console

agent1 = SuperAgent(load_random_ships())
agent1.model_load('superagent_weights')

agent2 = SuperAgent(load_random_ships())
agent2.model_load('superagent_weights')

soft_rules = DefaultRules()
soft_rules.illegal_moves.pop()

b = battle((agent1, agent2), soft_rules)

run_on_console(b, 500)
