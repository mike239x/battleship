from Ui import trace_game
from pickle import dump, load
from battleship import mini_battle, sample_Q, Dict

filename_fmt = "{}/run-{:>08}.trc"


def trace_game_to_file(mini_game, run_id, directory="."):
    trace = [(states[0].copy(), probed[0].copy())
             for states, probed in trace_game(mini_game)]
    with open(filename_fmt.format(directory, run_id), "wb") as outfile:
        dump(trace, outfile)


def load_trace(run_id, directory="."):
    with open(filename_fmt.format(directory, run_id), "rb") as infile:
        return load(infile)


def create_training_set(get_agent, ships, rules, directory="."):
    for idx, s in enumerate(ships):
        mini_game = mini_battle(get_agent(), s, rules)
        trace_game_to_file(mini_game, idx, directory)


def train_from_set(training_set, agent, sample=sample_Q):
    def replay():
        for state, _ in training_set:
            yield Dict(**state)
    sample(replay(), agent.train)


if __name__ == "__main__":
    def test_create_set():
        from battleship import DefaultRules, place_ships, RandomAgent, SuperAgent, load_ships

        DefaultRules.illegal_moves = []
        DefaultRules.max_turns = 100

        def get_agent():
            return RandomAgent(load_ships("ships/00000118.pos"))

        a = get_agent()
        _, s = place_ships(a.ships)

        create_training_set(get_agent, [s] * 10,
                            DefaultRules, directory="training")

    def test_run_set():
        from battleship import SuperAgent
        agent = SuperAgent()
        for i in range(10):
            train_from_set(load_trace(i, "training"), agent, sample_Q)


    test_create_set()
    test_run_set()