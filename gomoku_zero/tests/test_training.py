import pytest
import torch
import numpy as np
import sys
sys.path.insert(0, '/workspace/gomoku_zero')

from app.training.data_buffer import DataBuffer
from app.training.trainer import Trainer
from app.models.gomoku_net import GomokuNet

def test_data_buffer_add():
    buffer = DataBuffer(board_size=9)
    buffer.add_game({
        'states': [np.random.randn(9, 9, 9) for _ in range(10)],
        'policies': [np.random.rand(81) for _ in range(10)],
        'values': [np.random.choice([-1, 1]) for _ in range(10)]
    })
    assert buffer.size() == 10

def test_data_buffer_sample():
    buffer = DataBuffer(board_size=9)
    for _ in range(5):
        buffer.add_game({
            'states': [np.random.randn(9, 9, 9) for _ in range(5)],
            'policies': [np.random.rand(81) for _ in range(5)],
            'values': [np.random.choice([-1, 1]) for _ in range(5)]
        })
    
    states, policies, values = buffer.sample(batch_size=10)
    assert len(states) == 10
    assert len(policies) == 10
    assert len(values) == 10

def test_trainer_initialization():
    net = GomokuNet(board_size=9, num_channels=16, num_res_blocks=2)
    trainer = Trainer(net, board_size=9)
    assert trainer.board_size == 9
    assert trainer.optimizer is not None

def test_trainer_single_step():
    net = GomokuNet(board_size=9, num_channels=16, num_res_blocks=2)
    trainer = Trainer(net, board_size=9)
    
    states = torch.randn(4, 9, 9, 9)
    policies = torch.randn(4, 81)
    values = torch.randn(4, 1)
    
    loss = trainer.train_step(states, policies, values)
    assert isinstance(loss, float)
    assert loss >= 0
