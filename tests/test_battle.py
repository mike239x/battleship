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
        assert progress.response != Msg.ILLEGAL_MOVE
        assert progress.response != Msg.REPEATING_MOVE
        print('turn number is', progress.turn_num)
        print('player move was', progress.pos)
        print('response is', progress.response)

def test_1():
    agent1 = SmartAgent()
    agent2 = SmartAgent()
    g = battle((agent1, agent2), Rules())
    for progress in g:
        if progress == None:
            break
        assert progress.response != Msg.ILLEGAL_MOVE
        assert progress.response != Msg.REPEATING_MOVE
        print('current player id is', progress.current_player_id)
        print('turn number is', progress.turn_num)
        print('player move was', progress.pos)
        print('response is', progress.response)

def test_2():
    agent1 = SmartAgent()
    agent2 = RandomAgent()
    g = battle((agent1, agent2), Rules())
    for progress in g:
        if progress == None:
            break
        assert progress.response != Msg.ILLEGAL_MOVE
        assert progress.response != Msg.REPEATING_MOVE
        print('current player id is', progress.current_player_id)
        print('turn number is', progress.turn_num)
        print('player move was', progress.pos)
        print('response is', progress.response)
