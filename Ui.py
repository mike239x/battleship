from battleship import Msg, update_visible_ships, load_ships
from battleship import FIELD_HEIGHT, FIELD_WIDTH, FIELD_SIZE
import skimage

import numpy as np

def trace_game(game):
    states = {}
    probed = {}

    for state in game:
        if state is None:
            break

        player_id = state.get("current_player_id", 0)
        states[player_id] = state

        response = state.response
        if response in (Msg.HIT, Msg.SUNK, Msg.MISS):
            probed[player_id] = probed.get(
                player_id, np.zeros(FIELD_SIZE, np.uint8))
            update_visible_ships(probed[player_id], state.pos, state.response)
        yield states, probed

        if state.response in (Msg.YOU_WON, Msg.YOU_LOST):
            break


def run_on_console(game, dt):
    from time import sleep

    def get_console_printer(field_size=FIELD_HEIGHT):
        active_players = [0]

        def clear_players(number_of_players):
            for _ in range(number_of_players):
                print("\033[F\x1b[2K" * (field_size+3))

        def print_player(player, trace, probed):
            turn_num = trace.get("turn_num")
            latest_result = trace.get("response")
            pos = trace.get("pos")
            print("Player {} after {} moves".format(player, turn_num))
            print("Last result: {} on {}".format(latest_result, pos))
            print(probed.astype(np.int))

        def print_players(states, probed):
            clear_players(active_players[0])
            for player_id, trace in states.items():
                print_player(player_id, trace, probed[player_id])
            active_players[0] = len(states)

        return print_players

    def finish_game():
        print("Game ended")

    printer = get_console_printer()
    for state, probed in trace_game(game):
        printer(state, probed)
        sleep(dt/1000)
    finish_game()


def run_in_qt(game, dt):
    from time import sleep
    from PyQt5.QtWidgets import QApplication
    from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton
    from PyQt5.QtGui import QPixmap, QImage
    from PyQt5.QtCore import QTimer

    app = QApplication([])
    window = QWidget()
    player = QWidget()
    layout = QVBoxLayout()
    layout_player = QHBoxLayout()
    window.setLayout(layout)
    player.setLayout(layout_player)

    p1 = QLabel()
    p2 = QLabel()
    continue_btn = QPushButton("Next step")
    run_btn = QPushButton("Run")
    pause_btn = QPushButton("Pause")

    layout_player.addWidget(p1)
    layout_player.addWidget(p2)
    layout.addWidget(player)
    layout.addWidget(continue_btn)
    layout.addWidget(run_btn)
    layout.addWidget(pause_btn)

    timer = QTimer()

    game_processor = trace_game(game)

    def plot_fields(progress, probed):
        for player, field in probed.items():
            field = field*80

            modelled_data = field.repeat(4)
            modelled_data = modelled_data.reshape(FIELD_HEIGHT, FIELD_WIDTH, 4)

            if progress[player]["response"] == Msg.YOU_LOST:
                modelled_data[:,:,0] = 0
                modelled_data[:,:,1] = 0
            if progress[player]["response"] == Msg.YOU_WON:
                modelled_data[:,:,0] = 0
                modelled_data[:,:,2] = 0

            img = QImage(modelled_data.data, field.shape[1], field.shape[0], QImage.Format_RGB32)
            pix = QPixmap(img).scaled(300,300)
            if player == 0:
                p1.setPixmap(pix)
            if player == 1:
                p2.setPixmap(pix)

    def on_next_clicked():
        try:
            progress, probed = next(game_processor)
            plot_fields(progress, probed)
        except StopIteration:
            timer.stop()

    def on_run_clicked():
        timer.start(dt)

    def on_pause_clicked():
        timer.stop()

    continue_btn.clicked.connect(on_next_clicked)
    run_btn.clicked.connect(on_run_clicked)
    pause_btn.clicked.connect(on_pause_clicked)
    timer.timeout.connect(on_next_clicked)
    window.show()
    app.exec_()


if __name__ == "__main__":
    from battleship import DefaultRules, battle, mini_battle, place_ships
    from battleship import RandomAgent, SmartAgent, SuperAgent

    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--qt", action="store_true",
                        default=False, help="Use qt ui")
    parser.add_argument("--delay", type=int, default=500,
                        help="Delay between actions [ms]")
    parser.add_argument("--agent1",
                        choices=["super",
                                 "smart",
                                 "random"],
                        default="random",
                        required=True)
    parser.add_argument("--agent2",
                        choices=["super",
                                 "smart",
                                 "random"]
                        )
    parser.add_argument("--ships", nargs="+",
                        help="Provide paths to ship files", default=[])
    args = parser.parse_args()

    if len(args.ships) < 1:
        print("Cannot find ship files")
        exit(1)
    ships1 = load_ships(args.ships[0])
    if len(args.ships) == 1:
        ships2 = ships1
    else:
        ships2 = load_ships(args.ships[1])

    if args.agent1 == "super":
        agent = SuperAgent()
    elif args.agent1 == "smart":
        agent = SmartAgent()
    elif args.agent1 == "random":
        agent = RandomAgent()
    else:
        print("No valid agent1, abort")
        exit(1)

    if args.agent2 is None:
        agent2 = None
    elif args.agent2 == "super":
        agent2 = SuperAgent()
    elif args.agent2 == "smart":
        agent2 = SmartAgent()
    elif args.agent2 == "random":
        agent2 = RandomAgent()
    else:
        agent2 = None

    agent.ships = ships1
    agent2.ships = ships2

    if agent2 is None:
        game = mini_battle(agent, ships1)
    else:
        game = battle((agent2, agent))

    if args.qt:
        run_in_qt(game, args.delay)
    else:
        run_on_console(game, args.delay)
