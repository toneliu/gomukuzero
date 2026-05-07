import pytest
import torch
import numpy as np
import sys
sys.path.insert(0, '/workspace/gomoku_zero')

from app.models.gomoku_net import GomokuNet

def test_network_output_shape_9x9():
    net = GomokuNet(board_size=9, num_channels=32, num_res_blocks=3)
    state = torch.randn(1, 9, 9, 9)
    policy, value = net(state)
    assert policy.shape == (1, 81)
    assert value.shape == (1, 1)

def test_network_output_shape_15x15():
    net = GomokuNet(board_size=15, num_channels=32, num_res_blocks=3)
    state = torch.randn(1, 9, 15, 15)
    policy, value = net(state)
    assert policy.shape == (1, 225)
    assert value.shape == (1, 1)

def test_policy_sum_to_one():
    net = GomokuNet(board_size=9, num_channels=32, num_res_blocks=3)
    state = torch.randn(1, 9, 9, 9)
    policy, _ = net(state)
    assert torch.isclose(policy.sum(dim=1), torch.ones(1), atol=1e-5)

def test_value_range():
    net = GomokuNet(board_size=9, num_channels=32, num_res_blocks=3)
    state = torch.randn(1, 9, 9, 9)
    _, value = net(state)
    assert torch.all(value >= -1) and torch.all(value <= 1)

def test_batch_processing():
    net = GomokuNet(board_size=9, num_channels=32, num_res_blocks=3)
    state = torch.randn(8, 9, 9, 9)
    policy, value = net(state)
    assert policy.shape == (8, 81)
    assert value.shape == (8, 1)

def test_gradient_flow():
    net = GomokuNet(board_size=9, num_channels=32, num_res_blocks=3)
    state = torch.randn(2, 9, 9, 9, requires_grad=True)
    policy, value = net(state)
    loss = policy.sum() + value.sum()
    loss.backward()
    assert state.grad is not None
