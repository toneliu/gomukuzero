import pytest
import sys
sys.path.insert(0, '/workspace/gomoku_zero')

from app.game.board import Board
from app.models.gomoku_net import GomokuNet
from app.models.model_manager import ModelManager
from app.game.mcts import MCTS
from app.game.self_play import SelfPlay
from app.training.trainer import Trainer
from app.training.data_buffer import DataBuffer
import torch
import os
import shutil

def test_full_training_pipeline():
    board_size = 9
    net = GomokuNet(board_size=board_size, num_channels=16, num_res_blocks=2)
    
    sp = SelfPlay(net, board_size=board_size, simulations=10)
    games = sp.play_games(num_games=3)
    
    assert len(games) == 3
    
    buffer = DataBuffer(board_size=board_size)
    for game in games:
        buffer.add_game(game)
    
    assert buffer.size() > 0
    
    trainer = Trainer(net, board_size=board_size, learning_rate=0.01)
    
    states, policies, values = buffer.sample(batch_size=8)
    states_tensor = torch.from_numpy(states).float()
    policies_tensor = torch.from_numpy(policies).float()
    values_tensor = torch.from_numpy(values).float()
    
    loss = trainer.train_step(states_tensor, policies_tensor, values_tensor)
    assert isinstance(loss, float)
    assert loss >= 0

def test_model_save_load():
    board_size = 9
    net = GomokuNet(board_size=board_size, num_channels=16, num_res_blocks=2)
    
    manager = ModelManager(models_dir="test_models")
    
    path = manager.save_model(net, board_size, "test")
    assert path.exists()
    
    loaded_net = manager.load_model(board_size, "test")
    assert loaded_net is not None
    
    state1 = net.state_dict()
    state2 = loaded_net.state_dict()
    
    for (k1, v1), (k2, v2) in zip(state1.items(), state2.items()):
        assert torch.allclose(v1, v2)
    
    if os.path.exists("test_models"):
        shutil.rmtree("test_models", ignore_errors=True)

def test_game_flow():
    board_size = 9
    net = GomokuNet(board_size=board_size, num_channels=16, num_res_blocks=2)
    
    board = Board(size=board_size)
    mcts = MCTS(board, net, simulations=10)
    
    moves = []
    while not board.is_game_over() and len(moves) < 40:
        mcts.search()
        best_move = mcts.get_best_move()
        if best_move is None:
            break
        moves.append(best_move)
        board.place_stone(*best_move)
        mcts.update_root(best_move)
    
    assert len(moves) > 0
    assert board.get_winner() in [1, -1, 0]
