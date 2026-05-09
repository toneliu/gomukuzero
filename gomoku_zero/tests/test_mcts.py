import pytest
import torch
import numpy as np
import sys
sys.path.insert(0, '/workspace/gomoku_zero')

from app.game.board import Board
from app.game.mcts import MCTS
from app.models.gomoku_net import GomokuNet

@pytest.fixture
def simple_net():
    net = GomokuNet(board_size=9, num_channels=16, num_res_blocks=2)
    net.eval()
    return net

def test_mcts_initialization(simple_net):
    board = Board(size=9)
    mcts = MCTS(board, simple_net, simulations=10)
    assert mcts.simulations == 10
    assert mcts.board is board
    assert mcts.root is not None

def test_mcts_single_simulation(simple_net):
    board = Board(size=9)
    mcts = MCTS(board, simple_net, simulations=1)
    mcts.search()
    assert len(mcts.root.children) > 0

def test_mcts_get_policy(simple_net):
    board = Board(size=9)
    mcts = MCTS(board, simple_net, simulations=10)
    mcts.search()
    policy = mcts.get_policy_numpy(temperature=1.0)
    assert policy.shape == (81,)
    assert np.isclose(policy.sum(), 1.0)

def test_mcts_best_move(simple_net):
    board = Board(size=9)
    mcts = MCTS(board, simple_net, simulations=10)
    mcts.search()
    best_move = mcts.get_best_move()
    assert best_move is not None
    assert isinstance(best_move, tuple)
    assert len(best_move) == 2
