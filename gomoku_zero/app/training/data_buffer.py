import numpy as np
from typing import Dict, List, Tuple
import random

class DataBuffer:
    def __init__(self, board_size: int, max_size: int = 100000):
        self.board_size = board_size
        self.max_size = max_size
        self.games = []
        self.total_examples = 0
    
    def add_game(self, game_data: Dict):
        self.games.append(game_data)
        self.total_examples += len(game_data['states'])
        
        while self.total_examples > self.max_size and len(self.games) > 1:
            removed_game = self.games.pop(0)
            self.total_examples -= len(removed_game['states'])
    
    def size(self) -> int:
        return self.total_examples
    
    def sample(self, batch_size: int) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        all_states = []
        all_policies = []
        all_values = []
        
        for game in self.games:
            for i in range(len(game['states'])):
                all_states.append(game['states'][i])
                all_policies.append(game['policies'][i])
                all_values.append(game['values'][i])
        
        indices = list(range(len(all_states)))
        random.shuffle(indices)
        
        if batch_size > len(indices):
            batch_size = len(indices)
        
        batch_indices = indices[:batch_size]
        
        states = np.array([all_states[i] for i in batch_indices])
        policies = np.array([all_policies[i] for i in batch_indices])
        values = np.array([all_values[i] for i in batch_indices]).reshape(-1, 1)
        
        return states, policies, values
    
    def clear(self):
        self.games = []
        self.total_examples = 0
    
    def get_game_count(self) -> int:
        return len(self.games)
