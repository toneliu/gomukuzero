import numpy as np
import torch
import torch.nn.functional as F
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
        
        self.device = next(network.parameters()).device
        self.board_size = board.size
        self.num_actions = board.size * board.size
        
        self.gpu_batch_size = 64
        self._init_gpu_buffers()
    
    def _init_gpu_buffers(self):
        max_buffer_size = max(self.gpu_batch_size, self.simulations)
        self.state_buffer = torch.zeros(
            max_buffer_size, CONFIG.HISTORY_LEN * 2 + 1, 
            self.board_size, self.board_size, 
            device=self.device, dtype=torch.float32
        )
        self.policy_buffer = torch.zeros(
            max_buffer_size, self.num_actions,
            device=self.device, dtype=torch.float32
        )
        self.value_buffer = torch.zeros(
            max_buffer_size,
            device=self.device, dtype=torch.float32
        )
        self.policy_workspace = torch.zeros(
            self.gpu_batch_size, self.num_actions,
            device=self.device, dtype=torch.float32
        )
    
    def _get_state(self, board: Board) -> torch.Tensor:
        state = board.get_state(CONFIG.HISTORY_LEN)
        return torch.from_numpy(state).float()
    
    def search(self) -> float:
        batch_size = self.gpu_batch_size
        num_full_batches = self.simulations // batch_size
        remainder = self.simulations % batch_size
        
        for _ in range(num_full_batches):
            self._gpu_batch_search(batch_size)
        
        if remainder > 0:
            self._gpu_batch_search(remainder)
        
        return self.root.get_value()
    
    def _gpu_batch_search(self, batch_size: int):
        nodes_batch = []
        states_batch = []
        boards_batch = []
        
        for _ in range(batch_size):
            node = self._select(self.root)
            board = node.board_state if node.board_state else self.board
            nodes_batch.append(node)
            boards_batch.append(board)
            states_batch.append(self._get_state(board))
        
        for i, state in enumerate(states_batch):
            self.state_buffer[i] = state
        
        with torch.no_grad():
            policy_logits, values = self.network(self.state_buffer[:batch_size])
        
        policies = F.softmax(policy_logits, dim=1)
        self.policy_workspace[:batch_size] = policies
        
        for i, (node, board) in enumerate(zip(nodes_batch, boards_batch)):
            value = values[i].cpu().item()
            
            if board.is_game_over():
                winner = board.get_winner()
                value = float(winner) if winner else 0.0
            
            self._expand_node(node, self.policy_workspace[i], value, board)
        
        for i, node in enumerate(nodes_batch):
            self._backup(node, values[i].cpu().item())
    
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
    
    def _expand_node(self, node: Node, policy: torch.Tensor, value: float, board: Board):
        valid_moves = board.get_valid_moves()
        move_indices = [r * board.size + c for r, c in valid_moves]
        
        policy_np = policy.cpu().numpy()
        
        if node == self.root and len(node.children) == 0:
            noise = np.random.dirichlet([CONFIG.DIRICHLET_ALPHA] * len(valid_moves))
            for i, move in enumerate(valid_moves):
                node.children[move] = Node(
                    prior=0.75 * policy_np[move_indices[i]] + 0.25 * noise[i],
                    parent=node,
                    move=move
                )
        else:
            for i, move in enumerate(valid_moves):
                if move not in node.children:
                    node.children[move] = Node(
                        prior=policy_np[move_indices[i]],
                        parent=node,
                        move=move
                    )
        
        node.is_expanded = True
    
    def _backup(self, node: Node, value: float):
        current = node
        while current is not None:
            current.visit_count += 1
            current.value_sum += value
            value = -value
            current = current.parent
    
    def get_policy(self, temperature: float = 1.0) -> torch.Tensor:
        counts = np.zeros(self.num_actions)
        
        for move, child in self.root.children.items():
            idx = move[0] * self.board_size + move[1]
            counts[idx] = child.visit_count
        
        counts_tensor = torch.from_numpy(counts).float().to(self.device)
        
        if temperature == 0:
            best_idx = torch.argmax(counts_tensor)
            counts_tensor = torch.zeros_like(counts_tensor)
            counts_tensor[best_idx] = 1.0
        else:
            counts_tensor = counts_tensor ** (1.0 / temperature)
            if counts_tensor.sum() > 0:
                counts_tensor = counts_tensor / counts_tensor.sum()
        
        return counts_tensor
    
    def get_policy_numpy(self, temperature: float = 1.0) -> np.ndarray:
        policy = self.get_policy(temperature)
        return policy.cpu().numpy()
    
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
