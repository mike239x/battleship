from battleship import *

class Rules:
    illegal_moves = [Msg.ILLEGAL_MOVE, Msg.REPEATING_MOVE]
    max_turns = 100

def test_0():
    agent = SmartAgent()
    ships = agent.ships()
    success, field = place_ships(ships)
    print(field)
    assert success
    g = mini_battle(agent, field, Rules())
    for progress in g:
        if progress == None:
            break
        turn_num, response, probed = progress
        assert response != Msg.ILLEGAL_MOVE
        assert response != Msg.REPEATING_MOVE
        print(turn_num)
        print(response)
        print(probed.astype(np.int))

def test_1():
    agent1 = SmartAgent()
    agent2 = SmartAgent()
    g = battle((agent1, agent2), Rules())
    for progress in g:
        if progress == None:
            break
        current_player, turn_num, response, probed = progress
        assert response != Msg.ILLEGAL_MOVE
        assert response != Msg.REPEATING_MOVE

