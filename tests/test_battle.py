from battleship import *

def test_0():
    agent = SmartAgent("ships/00000118.pos")
    ships = agent.ships()
    success, field = place_ships(ships)
    print(field)
    assert success
    g = mini_battle(agent, field, DefaultRules())
    for progress in g:
        if progress == None:
            break
        assert progress.response != Msg.ILLEGAL_MOVE
        assert progress.response != Msg.REPEATING_MOVE
        print('turn number is', progress.turn_num)
        print('player move was', progress.pos)
        print('response is', progress.response)

def test_1():
    agent1 = SmartAgent("ships/00000034.pos")
    agent2 = SmartAgent("ships/00000042.pos")
    g = battle((agent1, agent2), DefaultRules())
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
    agent1 = SmartAgent("ships/00000034.pos")
    agent2 = RandomAgent("ships/00000042.pos")
    g = battle((agent1, agent2), DefaultRules())
    for progress in g:
        if progress == None:
            break
        assert progress.response != Msg.ILLEGAL_MOVE
        assert progress.response != Msg.REPEATING_MOVE
        print('current player id is', progress.current_player_id)
        print('turn number is', progress.turn_num)
        print('player move was', progress.pos)
        print('response is', progress.response)

def test_3():
    agent1 = SuperAgent("ships/00000034.pos")
    agent2 = RandomAgent("ships/00000042.pos")
    g = battle((agent1, agent2), DefaultRules())
    for progress in g:
        if progress == None:
            break
        assert progress.response != Msg.ILLEGAL_MOVE
        print('current player id is', progress.current_player_id)
        print('turn number is', progress.turn_num)
        print('player move was', progress.pos)
        print('response is', progress.response)
