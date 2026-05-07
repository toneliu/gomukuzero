import pytest
import numpy as np
import sys
sys.path.insert(0, '/workspace/gomoku_zero')

from app.game.self_play import SelfPlay
from app.models.gomoku_net import GomokuNet

@pytest.fixture
def simple_net():
    net = GomokuNet(board_size=9, num_channels=16, num_res_blocks=2)
    net.eval()
    return net

def test_self_play_single_game(simple_net):
    sp = SelfPlay(simple_net, board_size=9, simulations=20)
    game_data = sp.play_game()
    
    assert 'states' in game_data
    assert 'policies' in game_data
    assert 'values' in game_data
    assert len(game_data['states']) == len(game_data['policies'])
    assert game_data['board_size'] == 9
    assert game_data['winner'] in [1, -1, 0]

def test_self_play_multiple_games(simple_net):
    sp = SelfPlay(simple_net, board_size=9, simulations=20)
    games = sp.play_games(num_games=3)
    
    assert len(games) == 3
    for game in games:
        assert 'states' in game
        assert game['board_size'] == 9
