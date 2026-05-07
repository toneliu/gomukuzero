import pytest
import numpy as np
import sys
sys.path.insert(0, '/workspace/gomoku_zero')

from app.game.board import Board

def test_board_initialization():
    board = Board(size=9)
    assert board.size == 9
    assert board.current_player == 1
    assert board.board.shape == (9, 9)
    assert len(board.get_valid_moves()) == 81

def test_place_stone():
    board = Board(size=9)
    assert board.place_stone(4, 4) == True
    assert board.board[4, 4] == 1
    assert board.current_player == -1

def test_invalid_move():
    board = Board(size=9)
    board.place_stone(4, 4)
    assert board.place_stone(4, 4) == False

def test_win_detection_horizontal():
    board = Board(size=9)
    white_positions = [(0, 0), (0, 1), (0, 2), (0, 3)]
    for i in range(5):
        board.place_stone(i, 4)
        if i < 4:
            board.place_stone(*white_positions[i])
    assert board.is_game_over() == True
    assert board.winner == 1

def test_win_detection_vertical():
    board = Board(size=9)
    white_positions = [(0, 0), (1, 0), (2, 0), (3, 0)]
    for i in range(5):
        board.place_stone(4, i)
        if i < 4:
            board.place_stone(*white_positions[i])
    assert board.is_game_over() == True
    assert board.winner == 1

def test_win_detection_diagonal():
    board = Board(size=9)
    white_positions = [(0, 5), (1, 5), (2, 5), (3, 5)]
    for i in range(5):
        board.place_stone(i, i)
        if i < 4:
            board.place_stone(*white_positions[i])
    assert board.is_game_over() == True
    assert board.winner == 1

def test_get_state():
    board = Board(size=9)
    board.place_stone(4, 4)
    state = board.get_state()
    assert state.shape == (9, 9, 9)

def test_multiple_sizes():
    for size in [9, 11, 13, 15, 19]:
        board = Board(size=size)
        assert board.size == size
        assert len(board.get_valid_moves()) == size * size
