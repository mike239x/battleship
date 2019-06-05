from Ui import trace_game
from pickle import dump, load
from battleship import mini_battle, load_ships

filename_fmt = "{}/run-{:>08}.trc"


def trace_game_to_file(mini_game, run_id, directory="."):
    trace = [r[0].copy() for _, r in trace_game(mini_game)]
    with open(filename_fmt.format(directory, run_id), "wb") as outfile:
        dump(trace, outfile)


def load_trace(run_id, directory="."):
    with open(filename_fmt.format(directory, run_id), "rb") as infile:
        return load(infile)


def create_training_set(get_agent, ships, rules, directory="."):
    for idx, s in enumerate(ships):
        mini_game = mini_battle(get_agent(), s, rules)
        trace_game_to_file(mini_game, idx, directory)


if __name__ == "__main__":
    from battleship import DefaultRules, place_ships, RandomAgent

    DefaultRules.illegal_moves = []
    DefaultRules.max_turns = 100

    def get_agent():
        return RandomAgent(load_ships("ships/00000118.pos"))

    a = get_agent()
    _, s = place_ships(a.ships())

    create_training_set(get_agent, [s] * 10,
                        DefaultRules, directory="training")
