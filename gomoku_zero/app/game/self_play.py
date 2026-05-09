import numpy as np
from typing import Dict, List
from .board import Board
from .mcts import MCTS
from app.config import CONFIG
import uuid

class SelfPlay:
    def __init__(self, network, board_size: int = 9, simulations: int = None):
        self.network = network
        self.board_size = board_size
        self.simulations = simulations or CONFIG.MCTS_SIMULATIONS
        self.temperature = CONFIG.TEMPERATURE
    
    def play_game(self) -> Dict:
        board = Board(size=self.board_size)
        mcts = MCTS(board, self.network, self.simulations)
        
        states = []
        policies = []
        move_history = []
        
        try:
            while not board.is_game_over():
                mcts.search()
                
                policy = mcts.get_policy_numpy(temperature=self.temperature)
                states.append(board.get_state(CONFIG.HISTORY_LEN))
                policies.append(policy)
                
                best_move = mcts.get_best_move()
                if best_move is None:
                    break
                
                move_history.append(best_move)
                mcts.update_root(best_move)
        finally:
            mcts.cleanup()
        
        winner = board.get_winner() if board.is_game_over() else 0
        
        values = []
        for i in range(len(move_history)):
            player = 1 if i % 2 == 0 else -1
            values.append(0)
        
        if winner != 0:
            for i in range(len(values)):
                player = 1 if i % 2 == 0 else -1
                values[i] = player * winner
        
        return {
            'game_id': str(uuid.uuid4()),
            'board_size': self.board_size,
            'states': states,
            'policies': policies,
            'values': values,
            'winner': winner,
            'game_length': len(move_history)
        }
    
    def play_games(self, num_games: int = 10) -> List[Dict]:
        games = []
        for i in range(num_games):
            game = self.play_game()
            games.append(game)
        return games
