import numpy as np
import torch
from typing import Dict, Tuple, Optional
from .board import Board
from app.config import CONFIG

class Node:
    def __init__(self, prior: float, parent=None, move: Optional[Tuple[int, int]] = None):
        self.parent = parent
        self.move = move
        self.prior = prior
        self.children: Dict[Tuple[int, int], 'Node'] = {}
        self.visit_count = 0
        self.value_sum = 0.0
        self.is_expanded = False
        self.board_state = None
    
    def get_value(self) -> float:
        if self.visit_count == 0:
            return 0.0
        return self.value_sum / self.visit_count
    
    def get_ucb(self, parent_visits: int, c_puct: float = CONFIG.C_PUCT) -> float:
        if self.visit_count == 0:
            return float('inf')
        exploitation = self.get_value()
        exploration = c_puct * self.prior * np.sqrt(parent_visits) / (1 + self.visit_count)
        return exploitation + exploration

class MCTS:
    def __init__(self, board: Board, network, simulations: int = None):
        self.board = board
        self.network = network
        self.simulations = simulations or CONFIG.MCTS_SIMULATIONS
        self.c_puct = CONFIG.C_PUCT
        self.root = Node(prior=1.0, parent=None, move=None)
        self.root.board_state = board.copy()
    
    def search(self) -> float:
        for _ in range(self.simulations):
            node = self._select(self.root)
            value = self._expand_and_evaluate(node)
            self._backup(node, value)
        return self.root.get_value()
    
    def _select(self, node: Node) -> Node:
        while node.is_expanded:
            valid_moves = node.board_state.get_valid_moves() if node.board_state else self.board.get_valid_moves()
            
            if not valid_moves:
                return node
            
            best_move = None
            best_ucb = float('-inf')
            
            for move in valid_moves:
                if move in node.children:
                    child = node.children[move]
                    ucb = child.get_ucb(node.visit_count, self.c_puct)
                else:
                    ucb = float('inf')
                
                if ucb > best_ucb:
                    best_ucb = ucb
                    best_move = move
            
            if best_move is None:
                return node
            
            temp_board = node.board_state.copy()
            temp_board.place_stone(*best_move)
            node = node.children[best_move]
            node.board_state = temp_board
        
        return node
    
    def _expand_and_evaluate(self, node: Node) -> float:
        board = node.board_state if node.board_state else self.board
        
        if board.is_game_over():
            winner = board.get_winner()
            return float(winner) if winner else 0.0
        
        state = self._get_state(board)
        
        with torch.no_grad():
            policy_logits, value = self.network(state)
        
        policy = torch.softmax(policy_logits, dim=1).squeeze(0).numpy()
        value = value.item()
        
        valid_moves = board.get_valid_moves()
        move_indices = [r * board.size + c for r, c in valid_moves]
        
        if node == self.root and len(node.children) == 0:
            noise = np.random.dirichlet([CONFIG.DIRICHLET_ALPHA] * len(valid_moves))
            for i, move in enumerate(valid_moves):
                node.children[move] = Node(
                    prior=0.75 * policy[move_indices[i]] + 0.25 * noise[i],
                    parent=node,
                    move=move
                )
        else:
            for i, move in enumerate(valid_moves):
                if move not in node.children:
                    node.children[move] = Node(
                        prior=policy[move_indices[i]],
                        parent=node,
                        move=move
                    )
        
        node.is_expanded = True
        return value
    
    def _backup(self, node: Node, value: float):
        current = node
        while current is not None:
            current.visit_count += 1
            current.value_sum += value
            value = -value
            current = current.parent
    
    def _get_state(self, board: Board) -> torch.Tensor:
        state = board.get_state(CONFIG.HISTORY_LEN)
        state = torch.from_numpy(state).unsqueeze(0).float()
        return state
    
    def get_policy(self, temperature: float = 1.0) -> np.ndarray:
        counts = np.zeros(self.board.size * self.board.size)
        
        for move, child in self.root.children.items():
            idx = move[0] * self.board.size + move[1]
            counts[idx] = child.visit_count
        
        if temperature == 0:
            best_idx = np.argmax(counts)
            counts = np.zeros_like(counts)
            counts[best_idx] = 1.0
        else:
            counts = counts ** (1.0 / temperature)
            if counts.sum() > 0:
                counts = counts / counts.sum()
        
        return counts
    
    def get_best_move(self) -> Tuple[int, int]:
        if not self.root.children:
            valid_moves = self.board.get_valid_moves()
            if valid_moves:
                return valid_moves[np.random.randint(len(valid_moves))]
            return None
        
        best_move = None
        best_visits = -1
        
        for move, child in self.root.children.items():
            if child.visit_count > best_visits:
                best_visits = child.visit_count
                best_move = move
        
        return best_move
    
    def update_root(self, move: Tuple[int, int]):
        if move in self.root.children:
            new_root = self.root.children[move]
            new_root.parent = None
            new_root.board_state = self.board.copy()
            self.root = new_root
        else:
            self.root = Node(prior=1.0, parent=None, move=None)
            self.root.board_state = self.board.copy()
