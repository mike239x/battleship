from battleship import *
from Ui import run_in_qt, run_on_console

ships = load_random_ships()

agent1 = SuperAgent(ships)
agent1.model_load('superagent_weights')
agent1.exploration_rate = 0.0

agent2 = SmartAgent(ships)
#  agent2 = RandomAgent(ships)

soft_rules = DefaultRules()
soft_rules.illegal_moves.pop()

b = battle((agent1, agent2), soft_rules)

#  run_on_console(b, 500)
run_in_qt(b, 500)
