from battleship import Msg
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
            x, y = state.pos
            probed[player_id] = probed.get(player_id, np.zeros((10, 10), np.uint8))
            if response == Msg.SUNK:
                probed[player_id][y, x] = 2
                ships = skimage.measure.label(probed[player_id])
                probed[player_id][ships == ships[y,x]] = 3
            elif response == Msg.HIT:
                probed[player_id][y, x] = 2
            else:
                probed[player_id][y, x] = 1
        yield states, probed

        if state.response in (Msg.YOU_WON, Msg.YOU_LOST):
            break

def run_on_console(game, dt):
    from time import sleep

    def get_console_printer(field_size=10):
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

    def plot_fields(probed):
        for p, field in probed.items():
            field = field*80
            img = QImage(field.repeat(4).data, field.shape[1], field.shape[0], QImage.Format_RGB32)
            pix = QPixmap(img)
            pix = pix.scaled(300,300)
            if p == 0:
                p1.setPixmap(pix)
            if p == 1:
                p2.setPixmap(pix)

    def on_next_clicked():
        try:
            _, probed = next(game_processor)
            plot_fields(probed)
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
    from battleship import RandomAgent, SmartAgent

    a1 = RandomAgent("ships/00000000.pos")
    a2 = SmartAgent("ships/00000118.pos")
    _, s2 = place_ships(a2.ships())

    game = battle((a1, a2), DefaultRules())
    mini_game = mini_battle(a2, s2, DefaultRules())


    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--qt", action="store_true", default=False, help="Use qt ui")
    parser.add_argument("--delay", type=int, default=500, help="Delay between actions [ms]")
    parser.add_argument("--battletype", choices=["mini", "normal"], default="mini", help="Use mini battle as default")
    args = parser.parse_args()

    our_game = game if args.battletype == "normal" else mini_game

    if args.qt:
        run_in_qt(our_game, args.delay)
    else:
        run_on_console(our_game, args.delay)

