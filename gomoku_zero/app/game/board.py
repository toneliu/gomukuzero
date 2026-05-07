import numpy as np
from typing import List, Tuple, Optional
import copy

class Board:
    EMPTY = 0
    BLACK = 1
    WHITE = -1
    
    def __init__(self, size: int = 9):
        self.size = size
        self.board = np.zeros((size, size), dtype=np.int8)
        self.current_player = self.BLACK
        self.history = []
        self.winner = None
        self.game_over = False
    
    def place_stone(self, row: int, col: int) -> bool:
        if self.game_over:
            return False
        if self.board[row, col] != self.EMPTY:
            return False
        
        self.board[row, col] = self.current_player
        self.history.append((row, col))
        
        if self._check_win(row, col):
            self.game_over = True
            self.winner = self.current_player
        elif len(self.get_valid_moves()) == 0:
            self.game_over = True
            self.winner = 0
        
        self.current_player = -self.current_player
        return True
    
    def _check_win(self, row: int, col: int) -> bool:
        player = self.board[row, col]
        directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
        
        for dr, dc in directions:
            count = 1
            for i in range(1, 5):
                r, c = row + dr * i, col + dc * i
                if 0 <= r < self.size and 0 <= c < self.size and self.board[r, c] == player:
                    count += 1
                else:
                    break
            
            for i in range(1, 5):
                r, c = row - dr * i, col - dc * i
                if 0 <= r < self.size and 0 <= c < self.size and self.board[r, c] == player:
                    count += 1
                else:
                    break
            
            if count >= 5:
                return True
        
        return False
    
    def get_valid_moves(self) -> List[Tuple[int, int]]:
        if self.game_over:
            return []
        return [(r, c) for r in range(self.size) for c in range(self.size) 
                if self.board[r, c] == self.EMPTY]
    
    def get_state(self, history_len: int = 4) -> np.ndarray:
        state = np.zeros((history_len * 2 + 1, self.size, self.size), dtype=np.float32)
        
        for i, (r, c) in enumerate(self.history[-history_len:]):
            if i % 2 == 0:
                state[i * 2, r, c] = 1
            else:
                state[i * 2 + 1, r, c] = 1
        
        if len(self.history) % 2 == 0:
            state[-1, :, :] = 1
        
        return state
    
    def copy(self):
        new_board = Board(self.size)
        new_board.board = self.board.copy()
        new_board.current_player = self.current_player
        new_board.history = self.history.copy()
        new_board.winner = self.winner
        new_board.game_over = self.game_over
        return new_board
    
    def is_game_over(self) -> bool:
        return self.game_over
    
    def get_winner(self) -> Optional[int]:
        return self.winner
    
    def reset(self):
        self.board = np.zeros((self.size, self.size), dtype=np.int8)
        self.current_player = self.BLACK
        self.history = []
        self.winner = None
        self.game_over = False
