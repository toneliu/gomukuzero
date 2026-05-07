# GomokuZero 五子棋自对弈训练系统实现计划

**Goal:** 实现类似AlphaGo Zero的五子棋自对弈训练系统，支持多种棋盘尺寸、Web界面和模型训练。

**Architecture:** 
- 后端采用Python + PyTorch + FastAPI模块化架构
- 前端使用HTML5 Canvas响应式Web界面
- 核心算法：ResNet神经网络 + MCTS蒙特卡洛树搜索
- 自对弈生成训练数据，周期性训练优化模型

**Tech Stack:** Python 3.8+ / PyTorch / FastAPI / HTML5 Canvas / WebSocket

---

## 文件结构

```
gomoku_zero/
├── app/
│   ├── __init__.py
│   ├── main.py                      # FastAPI应用入口
│   ├── config.py                    # 配置管理
│   ├── models/
│   │   ├── __init__.py
│   │   ├── gomoku_net.py            # 神经网络模型定义
│   │   └── model_manager.py         # 模型加载/保存管理
│   ├── game/
│   │   ├── __init__.py
│   │   ├── board.py                 # 棋盘逻辑（胜利检测等）
│   │   ├── mcts.py                  # MCTS搜索算法
│   │   └── self_play.py             # 自对弈数据生成
│   ├── training/
│   │   ├── __init__.py
│   │   ├── trainer.py               # 训练器
│   │   └── data_buffer.py           # 训练数据缓冲区
│   └── api/
│       ├── __init__.py
│       ├── game_api.py              # 对弈相关API
│       ├── training_api.py          # 训练相关API
│       └── data_api.py              # 数据查看API
├── static/
│   ├── css/style.css                # 样式文件
│   └── js/
│       ├── board.js                 # 棋盘绘制组件
│       ├── game.js                  # 对弈逻辑
│       └── app.js                   # 主应用逻辑
├── templates/
│   └── index.html                   # 主页面
├── models/                          # 保存的模型权重
├── training_data/                   # 训练数据
├── logs/                            # 日志文件
├── tests/
│   ├── __init__.py
│   ├── test_board.py                # 棋盘逻辑测试
│   ├── test_neural_network.py       # 神经网络测试
│   ├── test_mcts.py                 # MCTS测试
│   └── test_training.py             # 训练测试
├── requirements.txt
└── README.md
```

---

## 阶段一：核心游戏逻辑和神经网络（Day 1-2）

### 任务 1: 项目初始化和配置

**Files:**
- Create: `gomoku_zero/requirements.txt`
- Create: `gomoku_zero/app/__init__.py`
- Create: `gomoku_zero/app/config.py`

- [ ] **Step 1: 创建项目目录结构和依赖文件**

```txt
# requirements.txt
torch>=1.9.0
numpy>=1.21.0
fastapi>=0.68.0
uvicorn>=0.15.0
websockets>=9.1
python-multipart>=0.0.5
pydantic>=1.8.0
```

```python
# app/config.py
from dataclasses import dataclass
from typing import List

@dataclass
class Config:
    BOARD_SIZES: List[int] = None
    DEFAULT_BOARD_SIZE: int = 9
    HISTORY_LEN: int = 4
    
    # 神经网络配置
    NUM_CHANNELS: int = 128
    NUM_RES_BLOCKS: int = 10
    
    # MCTS配置
    MCTS_SIMULATIONS: int = 200
    C_PUCT: float = 1.5
    DIRICHLET_ALPHA: float = 0.03
    FPU_REDUCTION: float = 0.25
    
    # 训练配置
    BATCH_SIZE: int = 128
    LEARNING_RATE: float = 0.01
    LR_DECAY: float = 0.9
    WEIGHT_DECAY: float = 1e-4
    
    # 自对弈配置
    SELF_PLAY_GAMES: int = 500
    TEMPERATURE: float = 1.0
    
    def __post_init__(self):
        if self.BOARD_SIZES is None:
            self.BOARD_SIZES = [9, 11, 13, 15, 19]

CONFIG = Config()
```

- [ ] **Step 2: 创建models/__init__.py**

```python
# app/models/__init__.py
from .gomoku_net import GomokuNet
from .model_manager import ModelManager

__all__ = ['GomokuNet', 'ModelManager']
```

- [ ] **Step 3: 创建game/__init__.py**

```python
# app/game/__init__.py
from .board import Board
from .mcts import MCTS
from .self_play import SelfPlay

__all__ = ['Board', 'MCTS', 'SelfPlay']
```

- [ ] **Step 4: 创建training/__init__.py**

```python
# app/training/__init__.py
from .trainer import Trainer
from .data_buffer import DataBuffer

__all__ = ['Trainer', 'DataBuffer']
```

- [ ] **Step 5: 创建api/__init__.py**

```python
# app/api/__init__.py
```

- [ ] **Step 6: 提交代码**

```bash
git add requirements.txt app/
git commit -m "feat: 初始化项目结构和配置"
```

---

### 任务 2: 棋盘逻辑实现

**Files:**
- Create: `gomoku_zero/app/game/board.py`
- Create: `gomoku_zero/tests/test_board.py`

- [ ] **Step 1: 编写棋盘逻辑测试**

```python
# tests/test_board.py
import pytest
import numpy as np
import sys
sys.path.insert(0, 'gomoku_zero')

from app.game.board import Board

def test_board_initialization():
    board = Board(size=9)
    assert board.size == 9
    assert board.current_player == 1
    assert board.board.shape == (9, 9)
    assert board.get_valid_moves() == [(i, j) for i in range(9) for j in range(9)]

def test_place_stone():
    board = Board(size=9)
    board.place_stone(4, 4)
    assert board.board[4, 4] == 1
    assert board.current_player == -1

def test_win_detection_horizontal():
    board = Board(size=9)
    for i in range(5):
        board.place_stone(i, 4)
        if i < 4:
            board.place_stone(0, 0)
    assert board.is_game_over()
    assert board.winner == 1

def test_win_detection_vertical():
    board = Board(size=9)
    for i in range(5):
        board.place_stone(4, i)
        if i < 4:
            board.place_stone(0, 0)
    assert board.is_game_over()
    assert board.winner == 1

def test_win_detection_diagonal():
    board = Board(size=9)
    for i in range(5):
        board.place_stone(i, i)
        if i < 4:
            board.place_stone(0, 0)
    assert board.is_game_over()
    assert board.winner == 1

def test_get_state():
    board = Board(size=9)
    board.place_stone(4, 4)
    state = board.get_state()
    assert state.shape == (4, 9, 9)
    assert state[0, 4, 4] == 1

def test_multiple_sizes():
    for size in [9, 11, 13, 15, 19]:
        board = Board(size=size)
        assert board.size == size
        assert len(board.get_valid_moves()) == size * size
```

- [ ] **Step 2: 运行测试验证失败**

```bash
cd /workspace
pytest tests/test_board.py -v
```

Expected: FAIL - Board class not defined

- [ ] **Step 3: 实现棋盘逻辑**

```python
# app/game/board.py
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
```

- [ ] **Step 4: 运行测试验证通过**

```bash
pytest tests/test_board.py -v
```

Expected: All tests PASS

- [ ] **Step 5: 提交代码**

```bash
git add tests/test_board.py app/game/board.py
git commit -m "feat: 实现棋盘逻辑（胜利检测、落子等）"
```

---

### 任务 3: 神经网络模型实现

**Files:**
- Create: `gomoku_zero/app/models/gomoku_net.py`
- Create: `gomoku_zero/tests/test_neural_network.py`

- [ ] **Step 1: 编写神经网络测试**

```python
# tests/test_neural_network.py
import pytest
import torch
import numpy as np
import sys
sys.path.insert(0, 'gomoku_zero')

from app.models.gomoku_net import GomokuNet

def test_network_output_shape_9x9():
    net = GomokuNet(board_size=9, num_channels=64, num_res_blocks=5)
    state = torch.randn(1, 9, 9, 9)
    policy, value = net(state)
    assert policy.shape == (1, 81)
    assert value.shape == (1, 1)

def test_network_output_shape_15x15():
    net = GomokuNet(board_size=15, num_channels=64, num_res_blocks=5)
    state = torch.randn(1, 9, 15, 15)
    policy, value = net(state)
    assert policy.shape == (1, 225)
    assert value.shape == (1, 1)

def test_policy_sum_to_one():
    net = GomokuNet(board_size=9, num_channels=64, num_res_blocks=5)
    state = torch.randn(1, 9, 9, 9)
    policy, _ = net(state)
    assert torch.isclose(policy.sum(dim=1), torch.ones(1), atol=1e-5)

def test_value_range():
    net = GomokuNet(board_size=9, num_channels=64, num_res_blocks=5)
    state = torch.randn(1, 9, 9, 9)
    _, value = net(state)
    assert torch.all(value >= -1) and torch.all(value <= 1)

def test_batch_processing():
    net = GomokuNet(board_size=9, num_channels=64, num_res_blocks=5)
    state = torch.randn(32, 9, 9, 9)
    policy, value = net(state)
    assert policy.shape == (32, 81)
    assert value.shape == (32, 1)

def test_gradient_flow():
    net = GomokuNet(board_size=9, num_channels=64, num_res_blocks=5)
    state = torch.randn(4, 9, 9, 9, requires_grad=True)
    policy, value = net(state)
    loss = policy.sum() + value.sum()
    loss.backward()
    assert state.grad is not None
    assert all(p.grad is not None for p in net.parameters() if p.requires_grad)
```

- [ ] **Step 2: 运行测试验证失败**

```bash
pytest tests/test_neural_network.py -v
```

Expected: FAIL - GomokuNet not defined

- [ ] **Step 3: 实现神经网络**

```python
# app/models/gomoku_net.py
import torch
import torch.nn as nn
import torch.nn.functional as F

class ResidualBlock(nn.Module):
    def __init__(self, num_channels: int):
        super().__init__()
        self.conv1 = nn.Conv2d(num_channels, num_channels, 3, padding=1, bias=False)
        self.bn1 = nn.BatchNorm2d(num_channels)
        self.conv2 = nn.Conv2d(num_channels, num_channels, 3, padding=1, bias=False)
        self.bn2 = nn.BatchNorm2d(num_channels)
    
    def forward(self, x):
        residual = x
        x = F.relu(self.bn1(self.conv1(x)))
        x = self.bn2(self.conv2(x))
        x = F.relu(x + residual)
        return x

class GomokuNet(nn.Module):
    def __init__(self, board_size: int = 9, num_channels: int = 128, 
                 num_res_blocks: int = 10, history_len: int = 4):
        super().__init__()
        self.board_size = board_size
        self.num_channels = num_channels
        self.history_len = history_len
        
        self.input_conv = nn.Sequential(
            nn.Conv2d(history_len * 2 + 1, num_channels, 3, padding=1, bias=False),
            nn.BatchNorm2d(num_channels),
            nn.ReLU()
        )
        
        self.residual_blocks = nn.ModuleList([
            ResidualBlock(num_channels) for _ in range(num_res_blocks)
        ])
        
        self.policy_head = nn.Sequential(
            nn.Conv2d(num_channels, 32, 1, bias=False),
            nn.BatchNorm2d(32),
            nn.ReLU(),
        )
        self.policy_head_fc = nn.Linear(32 * board_size * board_size, board_size * board_size)
        
        self.value_head = nn.Sequential(
            nn.Conv2d(num_channels, 32, 1, bias=False),
            nn.BatchNorm2d(32),
            nn.ReLU(),
        )
        self.value_head_fc = nn.Sequential(
            nn.Linear(32 * board_size * board_size, 256),
            nn.ReLU(),
            nn.Linear(256, 1),
            nn.Tanh()
        )
    
    def forward(self, x):
        if x.dim() == 3:
            x = x.unsqueeze(0)
        
        x = self.input_conv(x)
        
        for block in self.residual_blocks:
            x = block(x)
        
        policy = self.policy_head(x)
        policy = policy.view(policy.size(0), -1)
        policy = self.policy_head_fc(policy)
        policy = F.softmax(policy, dim=1)
        
        value = self.value_head(x)
        value = value.view(value.size(0), -1)
        value = self.value_head_fc(value)
        
        return policy, value
    
    def get_policy(self, state):
        policy, _ = self.forward(state)
        return policy
    
    def get_value(self, state):
        _, value = self.forward(state)
        return value
```

- [ ] **Step 4: 运行测试验证通过**

```bash
pytest tests/test_neural_network.py -v
```

Expected: All tests PASS

- [ ] **Step 5: 创建模型管理器**

```python
# app/models/model_manager.py
import torch
import os
from pathlib import Path
from typing import Optional
from .gomoku_net import GomokuNet
from app.config import CONFIG

class ModelManager:
    def __init__(self, models_dir: str = "models"):
        self.models_dir = Path(models_dir)
        self.models_dir.mkdir(exist_ok=True)
    
    def get_model_path(self, board_size: int, model_type: str = "best") -> Path:
        return self.models_dir / f"model_{board_size}x{board_size}_{model_type}.pth"
    
    def save_model(self, model: GomokuNet, board_size: int, model_type: str = "best"):
        path = self.get_model_path(board_size, model_type)
        torch.save({
            'model_state_dict': model.state_dict(),
            'board_size': board_size,
            'num_channels': model.num_channels,
            'num_res_blocks': model.num_res_blocks,
            'history_len': model.history_len
        }, path)
        return path
    
    def load_model(self, board_size: int, model_type: str = "best") -> Optional[GomokuNet]:
        path = self.get_model_path(board_size, model_type)
        if not path.exists():
            return None
        
        checkpoint = torch.load(path)
        model = GomokuNet(
            board_size=checkpoint['board_size'],
            num_channels=checkpoint['num_channels'],
            num_res_blocks=checkpoint['num_res_blocks'],
            history_len=checkpoint['history_len']
        )
        model.load_state_dict(checkpoint['model_state_dict'])
        return model
    
    def create_new_model(self, board_size: int) -> GomokuNet:
        return GomokuNet(
            board_size=board_size,
            num_channels=CONFIG.NUM_CHANNELS,
            num_res_blocks=CONFIG.NUM_RES_BLOCKS,
            history_len=CONFIG.HISTORY_LEN
        )
    
    def list_models(self) -> dict:
        models = {}
        for path in self.models_dir.glob("model_*_best.pth"):
            try:
                checkpoint = torch.load(path)
                size = checkpoint['board_size']
                models[size] = {
                    'path': str(path),
                    'board_size': size,
                    'num_channels': checkpoint['num_channels'],
                    'num_res_blocks': checkpoint['num_res_blocks']
                }
            except:
                pass
        return models
```

- [ ] **Step 6: 更新models/__init__.py**

```python
# app/models/__init__.py
from .gomoku_net import GomokuNet
from .model_manager import ModelManager

__all__ = ['GomokuNet', 'ModelManager']
```

- [ ] **Step 7: 提交代码**

```bash
git add tests/test_neural_network.py app/models/gomoku_net.py app/models/model_manager.py
git commit -m "feat: 实现神经网络模型（GomokuNet + ModelManager）"
```

---

### 任务 4: MCTS蒙特卡洛树搜索实现

**Files:**
- Create: `gomoku_zero/app/game/mcts.py`
- Create: `gomoku_zero/tests/test_mcts.py`

- [ ] **Step 1: 编写MCTS测试**

```python
# tests/test_mcts.py
import pytest
import torch
import numpy as np
import sys
sys.path.insert(0, 'gomoku_zero')

from app.game.board import Board
from app.game.mcts import MCTS
from app.models.gomoku_net import GomokuNet

@pytest.fixture
def simple_net():
    net = GomokuNet(board_size=9, num_channels=32, num_res_blocks=2)
    net.eval()
    return net

def test_mcts_initialization(simple_net):
    board = Board(size=9)
    mcts = MCTS(board, simple_net, simulations=100)
    assert mcts.simulations == 100
    assert mcts.board is board
    assert mcts.root is not None

def test_mcts_single_simulation(simple_net):
    board = Board(size=9)
    mcts = MCTS(board, simple_net, simulations=1)
    mcts.search()
    assert mcts.root.children

def test_mcts_get_policy(simple_net):
    board = Board(size=9)
    mcts = MCTS(board, simple_net, simulations=100)
    policy = mcts.get_policy(temperature=1.0)
    assert policy.shape == (81,)
    assert np.isclose(policy.sum(), 1.0)

def test_mcts_best_move(simple_net):
    board = Board(size=9)
    mcts = MCTS(board, simple_net, simulations=100)
    best_move = mcts.get_best_move()
    assert best_move in [(r, c) for r in range(9) for c in range(9)]

def test_mcts_update_root(simple_net):
    board = Board(size=9)
    mcts = MCTS(board, simple_net, simulations=100)
    mcts.search()
    best_move = mcts.get_best_move()
    board.place_stone(*best_move)
    mcts.update_root(best_move)
    assert mcts.board is board

def test_mcts_considers_all_valid_moves(simple_net):
    board = Board(size=9)
    mcts = MCTS(board, simple_net, simulations=200)
    mcts.search()
    valid_moves = board.get_valid_moves()
    policy = mcts.get_policy()
    for i, (r, c) in enumerate([(r, c) for r in range(9) for c in range(9)]):
        if (r, c) in valid_moves:
            assert policy[i] >= 0
```

- [ ] **Step 2: 运行测试验证失败**

```bash
pytest tests/test_mcts.py -v
```

Expected: FAIL - MCTS not defined

- [ ] **Step 3: 实现MCTS**

```python
# app/game/mcts.py
import numpy as np
import torch
from typing import Dict, Tuple, Optional, List
from .board import Board
from app.config import CONFIG

class Node:
    def __init__(self, prior: float, board: Board, move: Optional[Tuple[int, int]] = None):
        self.board = board.copy() if board else None
        self.move = move
        self.prior = prior
        self.children: Dict[Tuple[int, int], Node] = {}
        self.visit_count = 0
        self.value_sum = 0.0
        self.is_expanded = False
    
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
        self.root = Node(prior=1.0, board=board)
        self.root_expanded = False
    
    def search(self) -> float:
        for _ in range(self.simulations):
            node = self._select(self.root)
            value = self._expand_and_evaluate(node)
            self._backup(node, value)
        return self.root.get_value()
    
    def _select(self, node: Node) -> Node:
        while node.is_expanded:
            valid_moves = self.board.get_valid_moves() if node == self.root else node.board.get_valid_moves()
            
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
            
            temp_board = node.board.copy() if node.board else self.board.copy()
            temp_board.place_stone(*best_move)
            node = node.children[best_move]
            node.board = temp_board
        
        return node
    
    def _expand_and_evaluate(self, node: Node) -> float:
        if node.board.is_game_over():
            winner = node.board.get_winner()
            return float(winner) if node.board.current_player == self.BLACK else -float(winner)
        
        state = self._get_state(node.board)
        
        with torch.no_grad():
            policy_logits, value = self.network(state)
        
        policy = torch.softmax(policy_logits, dim=1).squeeze(0).numpy()
        value = value.item()
        
        valid_moves = node.board.get_valid_moves()
        move_indices = [r * node.board.size + c for r, c in valid_moves]
        
        if node == self.root and not self.root_expanded:
            noise = np.random.dirichlet([CONFIG.DIRICHLET_ALPHA] * len(valid_moves))
            for i, move in enumerate(valid_moves):
                node.children[move] = Node(
                    prior=0.75 * policy[move_indices[i]] + 0.25 * noise[i],
                    board=None
                )
            self.root_expanded = True
        else:
            for i, move in enumerate(valid_moves):
                node.children[move] = Node(
                    prior=policy[move_indices[i]],
                    board=None
                )
        
        node.is_expanded = True
        return value
    
    def _backup(self, node: Node, value: float):
        current = node
        while current is not None:
            current.visit_count += 1
            current.value_sum += value
            value = -value
            current = getattr(current, 'parent', None)
    
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
            self.root = new_root
        else:
            self.root = Node(prior=1.0, board=self.board)
            self.root_expanded = False
    
    @property
    def BLACK(self):
        return Board.BLACK
    
    @property
    def WHITE(self):
        return Board.WHITE
```

- [ ] **Step 4: 运行测试验证通过**

```bash
pytest tests/test_mcts.py -v
```

Expected: All tests PASS

- [ ] **Step 5: 提交代码**

```bash
git add tests/test_mcts.py app/game/mcts.py
git commit -m "feat: 实现MCTS蒙特卡洛树搜索算法"
```

---

### 任务 5: 自对弈数据生成

**Files:**
- Create: `gomoku_zero/app/game/self_play.py`
- Create: `gomoku_zero/tests/test_self_play.py`

- [ ] **Step 1: 编写自对弈测试**

```python
# tests/test_self_play.py
import pytest
import numpy as np
import torch
import sys
sys.path.insert(0, 'gomoku_zero')

from app.game.board import Board
from app.game.self_play import SelfPlay
from app.models.gomoku_net import GomokuNet

@pytest.fixture
def simple_net():
    net = GomokuNet(board_size=9, num_channels=32, num_res_blocks=2)
    net.eval()
    return net

def test_self_play_single_game(simple_net):
    sp = SelfPlay(simple_net, board_size=9, simulations=50)
    game_data = sp.play_game()
    
    assert 'states' in game_data
    assert 'policies' in game_data
    assert 'values' in game_data
    assert len(game_data['states']) == len(game_data['policies'])
    assert game_data['board_size'] == 9

def test_self_play_multiple_games(simple_net):
    sp = SelfPlay(simple_net, board_size=9, simulations=50)
    games = sp.play_games(num_games=3)
    
    assert len(games) == 3
    for game in games:
        assert 'states' in game
        assert game['board_size'] == 9

def test_game_ends_properly(simple_net):
    sp = SelfPlay(simple_net, board_size=9, simulations=30)
    game_data = sp.play_game()
    
    assert game_data['winner'] in [1, -1, 0]
    assert game_data['game_length'] > 0
```

- [ ] **Step 2: 运行测试验证失败**

```bash
pytest tests/test_self_play.py -v
```

Expected: FAIL - SelfPlay not defined

- [ ] **Step 3: 实现自对弈模块**

```python
# app/game/self_play.py
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
        
        while not board.is_game_over():
            mcts.search()
            
            policy = mcts.get_policy(temperature=self.temperature)
            states.append(board.get_state())
            policies.append(policy)
            
            best_move = mcts.get_best_move()
            if best_move is None:
                break
            
            move_history.append(best_move)
            board.place_stone(*best_move)
            mcts.update_root(best_move)
        
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
    
    def save_game(self, game_data: Dict, filepath: str):
        np.savez_compressed(
            filepath,
            states=np.array(game_data['states'], dtype=object),
            policies=np.array(game_data['policies'], dtype=object),
            values=np.array(game_data['values']),
            winner=game_data['winner'],
            board_size=game_data['board_size'],
            game_length=game_data['game_length']
        )
    
    def load_game(self, filepath: str) -> Dict:
        data = np.load(filepath, allow_pickle=True)
        return {
            'states': list(data['states']),
            'policies': list(data['policies']),
            'values': list(data['values']),
            'winner': int(data['winner']),
            'board_size': int(data['board_size']),
            'game_length': int(data['game_length'])
        }
```

- [ ] **Step 4: 运行测试验证通过**

```bash
pytest tests/test_self_play.py -v
```

Expected: All tests PASS

- [ ] **Step 5: 提交代码**

```bash
git add tests/test_self_play.py app/game/self_play.py
git commit -m "feat: 实现自对弈数据生成模块"
```

---

### 任务 6: 训练器实现

**Files:**
- Create: `gomoku_zero/app/training/data_buffer.py`
- Create: `gomoku_zero/app/training/trainer.py`
- Create: `gomoku_zero/tests/test_training.py`

- [ ] **Step 1: 编写训练相关测试**

```python
# tests/test_training.py
import pytest
import torch
import numpy as np
import sys
sys.path.insert(0, 'gomoku_zero')

from app.game.board import Board
from app.models.gomoku_net import GomokuNet
from app.training.data_buffer import DataBuffer
from app.training.trainer import Trainer

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
    for _ in range(20):
        buffer.add_game({
            'states': [np.random.randn(9, 9, 9) for _ in range(5)],
            'policies': [np.random.rand(81) for _ in range(5)],
            'values': [np.random.choice([-1, 1]) for _ in range(5)]
        })
    
    states, policies, values = buffer.sample(batch_size=32)
    assert len(states) == 32
    assert len(policies) == 32
    assert len(values) == 32

def test_trainer_initialization():
    net = GomokuNet(board_size=9, num_channels=32, num_res_blocks=2)
    trainer = Trainer(net, board_size=9)
    assert trainer.board_size == 9
    assert trainer.optimizer is not None

def test_trainer_single_step():
    net = GomokuNet(board_size=9, num_channels=32, num_res_blocks=2)
    trainer = Trainer(net, board_size=9)
    
    states = torch.randn(4, 9, 9, 9)
    policies = torch.randn(4, 81)
    values = torch.randn(4, 1)
    
    loss = trainer.train_step(states, policies, values)
    assert isinstance(loss, float)
    assert loss >= 0
```

- [ ] **Step 2: 运行测试验证失败**

```bash
pytest tests/test_training.py -v
```

Expected: FAIL - DataBuffer and Trainer not defined

- [ ] **Step 3: 实现数据缓冲区**

```python
# app/training/data_buffer.py
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
```

- [ ] **Step 4: 实现训练器**

```python
# app/training/trainer.py
import torch
import torch.nn as nn
import torch.optim as optim
from typing import List
import numpy as np

class Trainer:
    def __init__(self, network, board_size: int, 
                 learning_rate: float = 0.01,
                 weight_decay: float = 1e-4,
                 l2_reg: float = 1e-4):
        self.network = network
        self.board_size = board_size
        self.l2_reg = l2_reg
        
        self.optimizer = optim.Adam(
            network.parameters(),
            lr=learning_rate,
            weight_decay=weight_decay
        )
        
        self.scheduler = optim.lr_scheduler.StepLR(
            self.optimizer,
            step_size=10,
            gamma=0.9
        )
    
    def train_step(self, states: torch.Tensor, target_policies: torch.Tensor, 
                   target_values: torch.Tensor) -> float:
        self.network.train()
        
        self.optimizer.zero_grad()
        
        policies, values = self.network(states)
        
        policy_loss = -torch.mean(
            target_policies * torch.log(policies + 1e-8)
        )
        
        value_loss = torch.mean((values - target_values) ** 2)
        
        l2_loss = sum(
            torch.sum(param ** 2) for param in self.network.parameters()
        )
        
        total_loss = policy_loss + value_loss + self.l2_reg * l2_loss
        
        total_loss.backward()
        
        torch.nn.utils.clip_grad_norm_(self.network.parameters(), 1.0)
        
        self.optimizer.step()
        
        return total_loss.item()
    
    def eval_step(self, states: torch.Tensor, target_policies: torch.Tensor,
                  target_values: torch.Tensor) -> dict:
        self.network.eval()
        
        with torch.no_grad():
            policies, values = self.network(states)
            
            policy_loss = -torch.mean(
                target_policies * torch.log(policies + 1e-8)
            )
            
            value_loss = torch.mean((values - target_values) ** 2)
            
            policy_acc = torch.mean(
                (torch.argmax(policies, dim=1) == torch.argmax(target_policies, dim=1)).float()
            )
        
        return {
            'policy_loss': policy_loss.item(),
            'value_loss': value_loss.item(),
            'policy_accuracy': policy_acc.item()
        }
    
    def train_on_batch(self, states: np.ndarray, policies: np.ndarray, 
                      values: np.ndarray, epochs: int = 1) -> List[float]:
        states_tensor = torch.from_numpy(states).float()
        policies_tensor = torch.from_numpy(policies).float()
        values_tensor = torch.from_numpy(values).float()
        
        losses = []
        for _ in range(epochs):
            loss = self.train_step(states_tensor, policies_tensor, values_tensor)
            losses.append(loss)
        
        return losses
    
    def step(self):
        self.scheduler.step()
        return self.scheduler.get_last_lr()[0]
    
    def save_checkpoint(self, path: str, iteration: int):
        torch.save({
            'iteration': iteration,
            'model_state_dict': self.network.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'scheduler_state_dict': self.scheduler.state_dict()
        }, path)
    
    def load_checkpoint(self, path: str):
        checkpoint = torch.load(path)
        self.network.load_state_dict(checkpoint['model_state_dict'])
        self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        self.scheduler.load_state_dict(checkpoint['scheduler_state_dict'])
        return checkpoint['iteration']
```

- [ ] **Step 5: 运行测试验证通过**

```bash
pytest tests/test_training.py -v
```

Expected: All tests PASS

- [ ] **Step 6: 提交代码**

```bash
git add tests/test_training.py app/training/data_buffer.py app/training/trainer.py
git commit -m "feat: 实现训练器和数据缓冲区"
```

---

## 阶段二：Web API服务（Day 3-4）

### 任务 7: FastAPI后端实现

**Files:**
- Create: `gomoku_zero/app/main.py`
- Create: `gomoku_zero/app/api/game_api.py`
- Create: `gomoku_zero/app/api/training_api.py`
- Create: `gomoku_zero/app/api/data_api.py`

- [ ] **Step 1: 创建FastAPI主应用**

```python
# app/main.py
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import os

from app.api import game_api, training_api, data_api
from app.config import CONFIG

app = FastAPI(title="GomokuZero", description="AlphaGo Zero风格五子棋自对弈训练系统")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(game_api.router, prefix="/api/game", tags=["game"])
app.include_router(training_api.router, prefix="/api/training", tags=["training"])
app.include_router(data_api.router, prefix="/api/data", tags=["data"])

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
static_dir = os.path.join(BASE_DIR, "static")
templates_dir = os.path.join(BASE_DIR, "templates")

if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

templates = Jinja2Templates(directory=templates_dir)

@app.get("/")
async def root():
    return {"message": "GomokuZero API", "version": "1.0.0"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

- [ ] **Step 2: 创建对弈API**

```python
# app/api/game_api.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from app.game.board import Board
from app.game.mcts import MCTS
from app.models.model_manager import ModelManager
from app.config import CONFIG
import uuid

router = APIRouter()

model_manager = ModelManager()
active_games = {}

class StartGameRequest(BaseModel):
    board_size: int = 9
    model_type: str = "best"
    player_color: str = "black"

class StartGameResponse(BaseModel):
    game_id: str
    board_size: int
    player_color: str
    ai_color: str

class MoveRequest(BaseModel):
    game_id: str
    position: List[int]

class MoveResponse(BaseModel):
    valid: bool
    game_over: bool
    winner: Optional[int] = None
    ai_position: Optional[List[int]] = None

class GameStateResponse(BaseModel):
    game_id: str
    board: List[List[int]]
    current_player: str
    last_move: Optional[List[int]]
    ai_probabilities: Optional[List[float]]

@router.post("/start", response_model=StartGameResponse)
async def start_game(request: StartGameRequest):
    if request.board_size not in CONFIG.BOARD_SIZES:
        raise HTTPException(status_code=400, detail="不支持的棋盘尺寸")
    
    network = model_manager.load_model(request.board_size, request.model_type)
    if network is None:
        network = model_manager.create_new_model(request.board_size)
    
    game_id = str(uuid.uuid4())
    board = Board(size=request.board_size)
    
    if request.player_color == "black":
        player_color = Board.BLACK
        ai_color = Board.WHITE
    else:
        player_color = Board.WHITE
        ai_color = Board.BLACK
    
    active_games[game_id] = {
        'board': board,
        'network': network,
        'player_color': player_color,
        'ai_color': ai_color,
        'mcts': None
    }
    
    return StartGameResponse(
        game_id=game_id,
        board_size=request.board_size,
        player_color=request.player_color,
        ai_color="white" if ai_color == Board.WHITE else "black"
    )

@router.post("/move", response_model=MoveResponse)
async def make_move(request: MoveRequest):
    if request.game_id not in active_games:
        raise HTTPException(status_code=404, detail="游戏不存在")
    
    game = active_games[request.game_id]
    board = game['board']
    
    if board.is_game_over():
        return MoveResponse(
            valid=False,
            game_over=True,
            winner=board.get_winner()
        )
    
    if board.current_player != game['player_color']:
        return MoveResponse(valid=False, game_over=False, winner=None)
    
    row, col = request.position
    if not board.place_stone(row, col):
        return MoveResponse(valid=False, game_over=False, winner=None)
    
    if board.is_game_over():
        return MoveResponse(
            valid=True,
            game_over=True,
            winner=board.get_winner()
        )
    
    mcts = MCTS(board, game['network'], simulations=CONFIG.MCTS_SIMULATIONS)
    mcts.search()
    ai_move = mcts.get_best_move()
    
    if ai_move:
        board.place_stone(*ai_move)
        game['mcts'] = mcts
    
    return MoveResponse(
        valid=True,
        game_over=board.is_game_over(),
        winner=board.get_winner() if board.is_game_over() else None,
        ai_position=list(ai_move) if ai_move else None
    )

@router.get("/state/{game_id}", response_model=GameStateResponse)
async def get_game_state(game_id: str):
    if game_id not in active_games:
        raise HTTPException(status_code=404, detail="游戏不存在")
    
    game = active_games[game_id]
    board = game['board']
    
    ai_probs = None
    if game['mcts']:
        ai_probs = game['mcts'].get_policy().tolist()
    
    return GameStateResponse(
        game_id=game_id,
        board=board.board.tolist(),
        current_player="black" if board.current_player == Board.BLACK else "white",
        last_move=game['mcts'].root.move if game['mcts'] and game['mcts'].root.move else None,
        ai_probabilities=ai_probs
    )

@router.delete("/{game_id}")
async def end_game(game_id: str):
    if game_id in active_games:
        del active_games[game_id]
    return {"message": "游戏已结束"}
```

- [ ] **Step 3: 创建训练API**

```python
# app/api/training_api.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from app.models.model_manager import ModelManager
from app.training.trainer import Trainer
from app.training.data_buffer import DataBuffer
from app.game.self_play import SelfPlay
from app.config import CONFIG
import torch
import threading
import json
from datetime import datetime

router = APIRouter()

model_manager = ModelManager()

training_state = {
    'running': False,
    'board_size': 9,
    'iteration': 0,
    'games_completed': 0,
    'loss': 0.0,
    'thread': None
}

class StartTrainingRequest(BaseModel):
    board_size: int = 9
    games_per_iteration: int = 100
    mcts_simulations: int = 200
    train_epochs: int = 10

class TrainingStatusResponse(BaseModel):
    running: bool
    board_size: int
    iteration: int
    games_completed: int
    loss: float

class StopResponse(BaseModel):
    message: str

@router.post("/start")
async def start_training(request: StartTrainingRequest):
    global training_state
    
    if training_state['running']:
        raise HTTPException(status_code=400, detail="训练已在进行中")
    
    if request.board_size not in CONFIG.BOARD_SIZES:
        raise HTTPException(status_code=400, detail="不支持的棋盘尺寸")
    
    training_state['running'] = True
    training_state['board_size'] = request.board_size
    training_state['iteration'] = 0
    training_state['games_completed'] = 0
    
    def training_loop():
        network = model_manager.load_model(request.board_size)
        if network is None:
            network = model_manager.create_model(request.board_size)
        
        trainer = Trainer(network, request.board_size)
        data_buffer = DataBuffer(board_size=request.board_size)
        
        iteration = 0
        while training_state['running']:
            iteration += 1
            training_state['iteration'] = iteration
            
            sp = SelfPlay(network, board_size=request.board_size, 
                        simulations=request.mcts_simulations)
            
            games_batch = sp.play_games(request.games_per_iteration)
            for game in games_batch:
                data_buffer.add_game(game)
                training_state['games_completed'] += 1
            
            if data_buffer.size() >= request.train_epochs * 32:
                states, policies, values = data_buffer.sample(batch_size=32)
                states_tensor = torch.from_numpy(states).float()
                policies_tensor = torch.from_numpy(policies).float()
                values_tensor = torch.from_numpy(values).float()
                
                loss = trainer.train_step(states_tensor, policies_tensor, values_tensor)
                training_state['loss'] = loss
            
            if iteration % 10 == 0:
                model_manager.save_model(network, request.board_size, "best")
    
    training_state['thread'] = threading.Thread(target=training_loop)
    training_state['thread'].start()
    
    return {"message": "训练已开始", "board_size": request.board_size}

@router.get("/status", response_model=TrainingStatusResponse)
async def get_training_status():
    return TrainingStatusResponse(**training_state)

@router.post("/stop", response_model=StopResponse)
async def stop_training():
    global training_state
    training_state['running'] = False
    if training_state['thread']:
        training_state['thread'].join()
    return StopResponse(message="训练已停止")

@router.get("/history")
async def get_training_history():
    return {"iterations": training_state['iteration'], "games": training_state['games_completed']}
```

- [ ] **Step 4: 创建数据API**

```python
# app/api/data_api.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from app.models.model_manager import ModelManager
from app.config import CONFIG
import os
from pathlib import Path

router = APIRouter()

model_manager = ModelManager()

class ModelInfo(BaseModel):
    board_size: int
    num_channels: int
    num_res_blocks: int
    path: str

class ModelListResponse(BaseModel):
    models: List[ModelInfo]

@router.get("/models", response_model=ModelListResponse)
async def list_models():
    models = model_manager.list_models()
    return ModelListResponse(
        models=[
            ModelInfo(**model) for model in models.values()
        ]
    )

@router.get("/models/{board_size}/info")
async def get_model_info(board_size: int):
    models = model_manager.list_models()
    if board_size not in models:
        raise HTTPException(status_code=404, detail="模型不存在")
    return models[board_size]

@router.get("/config/sizes")
async def get_board_sizes():
    return {"sizes": CONFIG.BOARD_SIZES, "default": CONFIG.DEFAULT_BOARD_SIZE}

@router.get("/config/training")
async def get_training_config():
    return {
        "mcts_simulations": CONFIG.MCTS_SIMULATIONS,
        "batch_size": CONFIG.BATCH_SIZE,
        "learning_rate": CONFIG.LEARNING_RATE,
        "num_channels": CONFIG.NUM_CHANNELS,
        "num_res_blocks": CONFIG.NUM_RES_BLOCKS
    }
```

- [ ] **Step 5: 提交代码**

```bash
git add app/main.py app/api/*.py
git commit -m "feat: 实现FastAPI后端服务"
```

---

## 阶段三：Web前端界面（Day 5-6）

### 任务 8: HTML/CSS/JavaScript前端

**Files:**
- Create: `gomoku_zero/templates/index.html`
- Create: `gomoku_zero/static/css/style.css`
- Create: `gomoku_zero/static/js/board.js`
- Create: `gomoku_zero/static/js/game.js`
- Create: `gomoku_zero/static/js/app.js`

- [ ] **Step 1: 创建HTML主页面**

```html
<!-- templates/index.html -->
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>GomokuZero - 五子棋AI训练系统</title>
    <link rel="stylesheet" href="/static/css/style.css">
</head>
<body>
    <div class="container">
        <header>
            <h1>🎯 GomokuZero</h1>
            <p class="subtitle">AlphaGo Zero 风格五子棋自对弈训练系统</p>
        </header>
        
        <nav class="tab-nav">
            <button class="tab-btn active" data-tab="game">🎮 对弈</button>
            <button class="tab-btn" data-tab="training">⚙️ 训练</button>
            <button class="tab-btn" data-tab="data">📊 数据</button>
        </nav>
        
        <main>
            <!-- 对弈页面 -->
            <section id="game-section" class="tab-content active">
                <div class="game-controls">
                    <div class="control-group">
                        <label for="board-size">棋盘尺寸:</label>
                        <select id="board-size">
                            <option value="9">9×9</option>
                            <option value="11">11×11</option>
                            <option value="13">13×13</option>
                            <option value="15" selected>15×15</option>
                        </select>
                    </div>
                    <div class="control-group">
                        <label for="player-color">执棋:</label>
                        <select id="player-color">
                            <option value="black">黑棋（先手）</option>
                            <option value="white">白棋（后手）</option>
                        </select>
                    </div>
                    <button id="start-game-btn" class="btn btn-primary">开始对弈</button>
                </div>
                
                <div class="game-area">
                    <div class="board-container">
                        <canvas id="game-board"></canvas>
                        <div id="game-info" class="game-info">
                            <div id="status-message">点击"开始对弈"开始游戏</div>
                            <div id="win-rate" class="win-rate"></div>
                        </div>
                    </div>
                    <div id="policy-overlay" class="policy-overlay"></div>
                </div>
                
                <div id="game-actions" class="game-actions hidden">
                    <button id="new-game-btn" class="btn btn-secondary">新游戏</button>
                    <button id="undo-btn" class="btn btn-secondary">悔棋</button>
                </div>
            </section>
            
            <!-- 训练页面 -->
            <section id="training-section" class="tab-content">
                <div class="training-controls">
                    <div class="control-group">
                        <label for="train-board-size">棋盘尺寸:</label>
                        <select id="train-board-size">
                            <option value="9" selected>9×9 (推荐入门)</option>
                            <option value="11">11×11</option>
                            <option value="13">13×13</option>
                            <option value="15">15×15</option>
                        </select>
                    </div>
                    <div class="control-group">
                        <label for="games-per-iter">每轮自对弈局数:</label>
                        <input type="number" id="games-per-iter" value="100" min="10" max="500">
                    </div>
                    <div class="control-group">
                        <label for="mcts-sim">MCTS模拟次数:</label>
                        <input type="number" id="mcts-sim" value="200" min="50" max="1000">
                    </div>
                    <div class="control-group">
                        <label for="train-epochs">训练轮数:</label>
                        <input type="number" id="train-epochs" value="10" min="1" max="100">
                    </div>
                </div>
                
                <div class="training-actions">
                    <button id="start-training-btn" class="btn btn-primary">开始训练</button>
                    <button id="stop-training-btn" class="btn btn-danger hidden">停止训练</button>
                </div>
                
                <div id="training-status" class="training-status hidden">
                    <h3>训练进度</h3>
                    <div class="progress-bar">
                        <div id="progress-fill" class="progress-fill"></div>
                    </div>
                    <div class="stats-grid">
                        <div class="stat-item">
                            <span class="stat-label">迭代次数</span>
                            <span id="stat-iteration" class="stat-value">0</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-label">完成局数</span>
                            <span id="stat-games" class="stat-value">0</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-label">当前损失</span>
                            <span id="stat-loss" class="stat-value">0.00</span>
                        </div>
                    </div>
                </div>
            </section>
            
            <!-- 数据页面 -->
            <section id="data-section" class="tab-content">
                <h2>📦 已训练模型</h2>
                <div id="model-list" class="model-list">
                    <p class="loading">加载中...</p>
                </div>
                
                <h2>📈 训练统计</h2>
                <div id="training-stats" class="training-stats">
                    <div class="stat-card">
                        <h4>总训练局数</h4>
                        <p id="total-games">-</p>
                    </div>
                    <div class="stat-card">
                        <h4>训练迭代</h4>
                        <p id="total-iterations">-</p>
                    </div>
                </div>
            </section>
        </main>
    </div>
    
    <div id="notification" class="notification hidden"></div>
    
    <script src="/static/js/board.js"></script>
    <script src="/static/js/game.js"></script>
    <script src="/static/js/app.js"></script>
</body>
</html>
```

- [ ] **Step 2: 创建CSS样式**

```css
/* static/css/style.css */
:root {
    --primary-color: #4CAF50;
    --secondary-color: #2196F3;
    --danger-color: #f44336;
    --bg-color: #f5f5f5;
    --text-color: #333;
    --border-radius: 8px;
}

* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    min-height: 100vh;
    color: var(--text-color);
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
}

header {
    text-align: center;
    margin-bottom: 30px;
    color: white;
}

header h1 {
    font-size: 2.5rem;
    margin-bottom: 10px;
}

.subtitle {
    font-size: 1.1rem;
    opacity: 0.9;
}

.tab-nav {
    display: flex;
    gap: 10px;
    margin-bottom: 20px;
    background: white;
    padding: 10px;
    border-radius: var(--border-radius);
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.tab-btn {
    flex: 1;
    padding: 12px 20px;
    border: none;
    background: transparent;
    cursor: pointer;
    font-size: 1rem;
    border-radius: var(--border-radius);
    transition: all 0.3s;
}

.tab-btn.active {
    background: var(--primary-color);
    color: white;
}

.tab-btn:hover:not(.active) {
    background: rgba(76, 175, 80, 0.1);
}

.tab-content {
    display: none;
    background: white;
    padding: 30px;
    border-radius: var(--border-radius);
    box-shadow: 0 4px 20px rgba(0,0,0,0.15);
}

.tab-content.active {
    display: block;
}

.control-group {
    margin-bottom: 15px;
}

.control-group label {
    display: block;
    margin-bottom: 5px;
    font-weight: 500;
}

.control-group select,
.control-group input {
    width: 100%;
    padding: 10px;
    border: 1px solid #ddd;
    border-radius: var(--border-radius);
    font-size: 1rem;
}

.btn {
    padding: 12px 30px;
    border: none;
    border-radius: var(--border-radius);
    font-size: 1rem;
    cursor: pointer;
    transition: all 0.3s;
}

.btn-primary {
    background: var(--primary-color);
    color: white;
}

.btn-primary:hover {
    background: #45a049;
}

.btn-secondary {
    background: #ddd;
    color: #333;
}

.btn-danger {
    background: var(--danger-color);
    color: white;
}

.hidden {
    display: none !important;
}

.game-area {
    display: flex;
    flex-direction: column;
    align-items: center;
    margin: 30px 0;
}

.board-container {
    position: relative;
}

#game-board {
    background: #DEB887;
    border: 2px solid #8B4513;
    border-radius: 4px;
    cursor: pointer;
}

.game-info {
    text-align: center;
    margin-top: 15px;
    font-size: 1.1rem;
}

.win-rate {
    margin-top: 10px;
    font-size: 1.5rem;
    font-weight: bold;
    color: var(--primary-color);
}

.policy-overlay {
    position: absolute;
    top: 0;
    left: 0;
    pointer-events: none;
}

.game-controls,
.training-controls {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 15px;
    margin-bottom: 20px;
}

.game-actions {
    display: flex;
    gap: 10px;
    justify-content: center;
}

.training-status {
    margin-top: 30px;
}

.progress-bar {
    height: 20px;
    background: #e0e0e0;
    border-radius: 10px;
    overflow: hidden;
    margin: 15px 0;
}

.progress-fill {
    height: 100%;
    background: linear-gradient(90deg, var(--primary-color), var(--secondary-color));
    width: 0%;
    transition: width 0.3s;
}

.stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 15px;
    margin-top: 20px;
}

.stat-item {
    background: #f9f9f9;
    padding: 15px;
    border-radius: var(--border-radius);
    text-align: center;
}

.stat-label {
    display: block;
    color: #666;
    font-size: 0.9rem;
    margin-bottom: 5px;
}

.stat-value {
    display: block;
    font-size: 1.5rem;
    font-weight: bold;
    color: var(--primary-color);
}

.model-list {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
    gap: 15px;
    margin: 20px 0;
}

.model-card {
    background: #f9f9f9;
    padding: 20px;
    border-radius: var(--border-radius);
    border-left: 4px solid var(--primary-color);
}

.model-card h4 {
    margin-bottom: 10px;
}

.model-card p {
    font-size: 0.9rem;
    color: #666;
}

.stat-card {
    background: white;
    padding: 20px;
    border-radius: var(--border-radius);
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.notification {
    position: fixed;
    bottom: 20px;
    right: 20px;
    padding: 15px 25px;
    background: var(--primary-color);
    color: white;
    border-radius: var(--border-radius);
    box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    animation: slideIn 0.3s ease;
}

@keyframes slideIn {
    from {
        transform: translateX(100%);
        opacity: 0;
    }
    to {
        transform: translateX(0);
        opacity: 1;
    }
}

@media (max-width: 768px) {
    .container {
        padding: 10px;
    }
    
    header h1 {
        font-size: 1.8rem;
    }
    
    .tab-content {
        padding: 15px;
    }
    
    #game-board {
        max-width: 90vw;
        max-height: 60vh;
    }
    
    .control-group select,
    .control-group input {
        font-size: 16px;
    }
}
```

- [ ] **Step 3: 创建棋盘组件**

```javascript
// static/js/board.js
class BoardRenderer {
    constructor(canvas, size = 15) {
        this.canvas = canvas;
        this.ctx = canvas.getContext('2d');
        this.size = size;
        this.cellSize = 30;
        this.board = Array(size).fill().map(() => Array(size).fill(0));
        this.lastMove = null;
        this.policyMap = null;
        this.highlightedCells = [];
    }
    
    setSize(size) {
        this.size = size;
        this.board = Array(size).fill().map(() => Array(size).fill(0));
        this.lastMove = null;
        this.policyMap = null;
        this.highlightedCells = [];
    }
    
    resize(containerWidth) {
        const maxSize = Math.min(containerWidth, 600);
        this.cellSize = Math.floor(maxSize / this.size);
        const canvasSize = this.cellSize * this.size;
        
        const dpr = window.devicePixelRatio || 1;
        this.canvas.width = canvasSize * dpr;
        this.canvas.height = canvasSize * dpr;
        this.canvas.style.width = `${canvasSize}px`;
        this.canvas.style.height = `${canvasSize}px`;
        this.ctx.scale(dpr, dpr);
        
        this.draw();
    }
    
    setBoard(board) {
        this.board = board;
        this.draw();
    }
    
    setLastMove(move) {
        this.lastMove = move;
        this.draw();
    }
    
    setPolicyMap(policy) {
        if (!policy) {
            this.policyMap = null;
            this.draw();
            return;
        }
        
        this.policyMap = [];
        for (let i = 0; i < this.size; i++) {
            this.policyMap[i] = [];
            for (let j = 0; j < this.size; j++) {
                const idx = i * this.size + j;
                if (this.board[i][j] === 0 && policy[idx] > 0.01) {
                    this.policyMap[i][j] = policy[idx];
                } else {
                    this.policyMap[i][j] = 0;
                }
            }
        }
        this.draw();
    }
    
    clearPolicyMap() {
        this.policyMap = null;
        this.draw();
    }
    
    draw() {
        const ctx = this.ctx;
        const cs = this.cellSize;
        
        ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        
        ctx.fillStyle = '#DEB887';
        ctx.fillRect(0, 0, cs * this.size, cs * this.size);
        
        ctx.strokeStyle = '#8B4513';
        ctx.lineWidth = 1;
        
        for (let i = 0; i < this.size; i++) {
            ctx.beginPath();
            ctx.moveTo(cs / 2, cs / 2 + i * cs);
            ctx.lineTo(cs * (this.size - 0.5), cs / 2 + i * cs);
            ctx.stroke();
            
            ctx.beginPath();
            ctx.moveTo(cs / 2 + i * cs, cs / 2);
            ctx.lineTo(cs / 2 + i * cs, cs * (this.size - 0.5));
            ctx.stroke();
        }
        
        if (this.policyMap) {
            const maxProb = Math.max(...this.policyMap.flat().filter(v => v > 0));
            for (let i = 0; i < this.size; i++) {
                for (let j = 0; j < this.size; j++) {
                    if (this.policyMap[i][j] > 0) {
                        const alpha = 0.3 + 0.7 * (this.policyMap[i][j] / maxProb);
                        ctx.fillStyle = `rgba(76, 175, 80, ${alpha})`;
                        ctx.beginPath();
                        ctx.arc(cs / 2 + j * cs, cs / 2 + i * cs, cs * 0.4, 0, Math.PI * 2);
                        ctx.fill();
                    }
                }
            }
        }
        
        for (let i = 0; i < this.size; i++) {
            for (let j = 0; j < this.size; j++) {
                if (this.board[i][j] !== 0) {
                    const gradient = ctx.createRadialGradient(
                        cs / 2 + j * cs - cs * 0.1,
                        cs / 2 + i * cs - cs * 0.1,
                        0,
                        cs / 2 + j * cs,
                        cs / 2 + i * cs,
                        cs * 0.4
                    );
                    
                    if (this.board[i][j] === 1) {
                        gradient.addColorStop(0, '#333');
                        gradient.addColorStop(1, '#000');
                    } else {
                        gradient.addColorStop(0, '#fff');
                        gradient.addColorStop(1, '#ccc');
                    }
                    
                    ctx.fillStyle = gradient;
                    ctx.beginPath();
                    ctx.arc(cs / 2 + j * cs, cs / 2 + i * cs, cs * 0.4, 0, Math.PI * 2);
                    ctx.fill();
                    
                    if (this.lastMove && this.lastMove[0] === i && this.lastMove[1] === j) {
                        ctx.strokeStyle = '#f44336';
                        ctx.lineWidth = 2;
                        ctx.beginPath();
                        ctx.arc(cs / 2 + j * cs, cs / 2 + i * cs, cs * 0.35, 0, Math.PI * 2);
                        ctx.stroke();
                    }
                }
            }
        }
    }
    
    getCellFromEvent(event) {
        const rect = this.canvas.getBoundingClientRect();
        const x = event.clientX - rect.left;
        const y = event.clientY - rect.top;
        
        const cs = this.cellSize;
        const col = Math.round((x - cs / 2) / cs);
        const row = Math.round((y - cs / 2) / cs);
        
        if (row >= 0 && row < this.size && col >= 0 && col < this.size) {
            return [row, col];
        }
        return null;
    }
}
```

- [ ] **Step 4: 创建游戏逻辑**

```javascript
// static/js/game.js
class GomokuGame {
    constructor() {
        this.gameId = null;
        this.boardSize = 15;
        this.playerColor = 'black';
        this.isMyTurn = false;
        this.gameOver = false;
    }
    
    async startGame(boardSize, playerColor) {
        this.boardSize = boardSize;
        this.playerColor = playerColor;
        this.isMyTurn = (playerColor === 'black');
        this.gameOver = false;
        
        try {
            const response = await fetch('/api/game/start', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    board_size: boardSize,
                    player_color: playerColor
                })
            });
            
            const data = await response.json();
            this.gameId = data.game_id;
            
            return { success: true, data };
        } catch (error) {
            console.error('Start game error:', error);
            return { success: false, error: error.message };
        }
    }
    
    async makeMove(row, col) {
        if (!this.gameId || !this.isMyTurn || this.gameOver) {
            return { success: false, reason: 'Not your turn' };
        }
        
        try {
            const response = await fetch('/api/game/move', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    game_id: this.gameId,
                    position: [row, col]
                })
            });
            
            const data = await response.json();
            return { success: data.valid, data };
        } catch (error) {
            console.error('Make move error:', error);
            return { success: false, error: error.message };
        }
    }
    
    async getGameState() {
        if (!this.gameId) return null;
        
        try {
            const response = await fetch(`/api/game/state/${this.gameId}`);
            return await response.json();
        } catch (error) {
            console.error('Get state error:', error);
            return null;
        }
    }
    
    async endGame() {
        if (!this.gameId) return;
        
        try {
            await fetch(`/api/game/${this.gameId}`, { method: 'DELETE' });
        } catch (error) {
            console.error('End game error:', error);
        }
        
        this.gameId = null;
    }
}
```

- [ ] **Step 5: 创建主应用逻辑**

```javascript
// static/js/app.js
let boardRenderer;
let game;
let pollInterval;

document.addEventListener('DOMContentLoaded', () => {
    initApp();
});

function initApp() {
    const canvas = document.getElementById('game-board');
    boardRenderer = new BoardRenderer(canvas, 15);
    
    const container = document.querySelector('.board-container');
    boardRenderer.resize(container.clientWidth - 40);
    
    window.addEventListener('resize', () => {
        boardRenderer.resize(container.clientWidth - 40);
    });
    
    canvas.addEventListener('click', handleBoardClick);
    
    initTabs();
    initGameControls();
    initTrainingControls();
    initDataView();
}

function initTabs() {
    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');
    
    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const tabId = btn.dataset.tab;
            
            tabBtns.forEach(b => b.classList.remove('active'));
            tabContents.forEach(c => c.classList.remove('active'));
            
            btn.classList.add('active');
            document.getElementById(`${tabId}-section`).classList.add('active');
            
            if (tabId === 'game') {
                const container = document.querySelector('.board-container');
                boardRenderer.resize(container.clientWidth - 40);
            }
        });
    });
}

function initGameControls() {
    const startBtn = document.getElementById('start-game-btn');
    const newGameBtn = document.getElementById('new-game-btn');
    
    startBtn.addEventListener('click', startNewGame);
    newGameBtn.addEventListener('click', startNewGame);
    
    document.getElementById('undo-btn').addEventListener('click', () => {
        showNotification('悔棋功能开发中');
    });
}

async function startNewGame() {
    const boardSize = parseInt(document.getElementById('board-size').value);
    const playerColor = document.getElementById('player-color').value;
    
    game = new GomokuGame();
    boardRenderer.setSize(boardSize);
    
    const container = document.querySelector('.board-container');
    boardRenderer.resize(container.clientWidth - 40);
    
    const result = await game.startGame(boardSize, playerColor);
    
    if (result.success) {
        document.getElementById('status-message').textContent = '游戏开始！';
        document.getElementById('game-actions').classList.remove('hidden');
        boardRenderer.clearPolicyMap();
        
        updateGameState();
    } else {
        showNotification('启动游戏失败: ' + result.error);
    }
}

async function handleBoardClick(event) {
    if (!game || game.gameOver) return;
    
    const cell = boardRenderer.getCellFromEvent(event);
    if (!cell) return;
    
    const [row, col] = cell;
    
    if (game.board[row]?.[col] !== 0) {
        showNotification('该位置已有棋子');
        return;
    }
    
    const result = await game.makeMove(row, col);
    
    if (result.success) {
        updateGameState();
        
        if (result.data.game_over) {
            game.gameOver = true;
            game.isMyTurn = false;
            handleGameOver(result.data.winner);
        }
    }
}

async function updateGameState() {
    if (!game || !game.gameId) return;
    
    const state = await game.getGameState();
    if (!state) return;
    
    boardRenderer.setBoard(state.board);
    
    if (state.last_move) {
        boardRenderer.setLastMove(state.last_move);
    }
    
    if (state.ai_probabilities) {
        boardRenderer.setPolicyMap(state.ai_probabilities);
    }
    
    game.board = state.board;
    
    const statusMsg = document.getElementById('status-message');
    if (state.current_player === game.playerColor) {
        statusMsg.textContent = '轮到你了';
        game.isMyTurn = true;
    } else {
        statusMsg.textContent = 'AI思考中...';
        game.isMyTurn = false;
        setTimeout(updateGameState, 500);
    }
}

function handleGameOver(winner) {
    boardRenderer.clearPolicyMap();
    
    let message;
    if (winner === 0) {
        message = '平局！';
    } else if ((winner === 1 && game.playerColor === 'black') || 
               (winner === -1 && game.playerColor === 'white')) {
        message = '🎉 恭喜获胜！';
    } else {
        message = 'AI获胜，再接再厉！';
    }
    
    document.getElementById('status-message').textContent = message;
    showNotification(message);
}

function initTrainingControls() {
    const startBtn = document.getElementById('start-training-btn');
    const stopBtn = document.getElementById('stop-training-btn');
    
    startBtn.addEventListener('click', startTraining);
    stopBtn.addEventListener('click', stopTraining);
    
    setInterval(updateTrainingStatus, 2000);
}

async function startTraining() {
    const boardSize = parseInt(document.getElementById('train-board-size').value);
    const gamesPerIter = parseInt(document.getElementById('games-per-iter').value);
    const mctsSim = parseInt(document.getElementById('mcts-sim').value);
    const trainEpochs = parseInt(document.getElementById('train-epochs').value);
    
    try {
        const response = await fetch('/api/training/start', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                board_size: boardSize,
                games_per_iteration: gamesPerIter,
                mcts_simulations: mctsSim,
                train_epochs: trainEpochs
            })
        });
        
        const data = await response.json();
        
        document.getElementById('start-training-btn').classList.add('hidden');
        document.getElementById('stop-training-btn').classList.remove('hidden');
        document.getElementById('training-status').classList.remove('hidden');
        
        showNotification('训练已开始');
    } catch (error) {
        showNotification('启动训练失败: ' + error.message);
    }
}

async function stopTraining() {
    try {
        await fetch('/api/training/stop', { method: 'POST' });
        
        document.getElementById('start-training-btn').classList.remove('hidden');
        document.getElementById('stop-training-btn').classList.add('hidden');
        
        showNotification('训练已停止');
    } catch (error) {
        showNotification('停止训练失败: ' + error.message);
    }
}

async function updateTrainingStatus() {
    try {
        const response = await fetch('/api/training/status');
        const data = await response.json();
        
        if (data.running) {
            document.getElementById('stat-iteration').textContent = data.iteration;
            document.getElementById('stat-games').textContent = data.games_completed;
            document.getElementById('stat-loss').textContent = data.loss.toFixed(4);
        }
    } catch (error) {
        console.error('Update training status error:', error);
    }
}

async function initDataView() {
    await loadModelList();
    await loadTrainingStats();
}

async function loadModelList() {
    try {
        const response = await fetch('/api/data/models');
        const data = await response.json();
        
        const modelList = document.getElementById('model-list');
        
        if (data.models.length === 0) {
            modelList.innerHTML = '<p class="empty">暂无训练模型</p>';
            return;
        }
        
        modelList.innerHTML = data.models.map(model => `
            <div class="model-card">
                <h4>${model.board_size}×${model.board_size} 棋盘</h4>
                <p>通道数: ${model.num_channels}</p>
                <p>残差块: ${model.num_res_blocks}</p>
            </div>
        `).join('');
    } catch (error) {
        console.error('Load model list error:', error);
    }
}

async function loadTrainingStats() {
    try {
        const response = await fetch('/api/training/history');
        const data = await response.json();
        
        document.getElementById('total-games').textContent = data.games;
        document.getElementById('total-iterations').textContent = data.iterations;
    } catch (error) {
        console.error('Load training stats error:', error);
    }
}

function showNotification(message) {
    const notification = document.getElementById('notification');
    notification.textContent = message;
    notification.classList.remove('hidden');
    
    setTimeout(() => {
        notification.classList.add('hidden');
    }, 3000);
}
```

- [ ] **Step 6: 提交代码**

```bash
git add templates/index.html static/css/style.css static/js/*.js
git commit -m "feat: 实现Web前端界面"
```

---

## 阶段四：测试和部署（Day 7）

### 任务 9: 集成测试

**Files:**
- Create: `gomoku_zero/tests/test_integration.py`

- [ ] **Step 1: 编写集成测试**

```python
# tests/test_integration.py
import pytest
import sys
sys.path.insert(0, 'gomoku_zero')

from app.game.board import Board
from app.models.gomoku_net import GomokuNet
from app.models.model_manager import ModelManager
from app.game.mcts import MCTS
from app.game.self_play import SelfPlay
from app.training.trainer import Trainer
from app.training.data_buffer import DataBuffer
import torch

def test_full_training_pipeline():
    board_size = 9
    net = GomokuNet(board_size=board_size, num_channels=32, num_res_blocks=3)
    
    sp = SelfPlay(net, board_size=board_size, simulations=50)
    games = sp.play_games(num_games=5)
    
    assert len(games) == 5
    
    buffer = DataBuffer(board_size=board_size)
    for game in games:
        buffer.add_game(game)
    
    assert buffer.size() > 0
    
    trainer = Trainer(net, board_size=board_size, learning_rate=0.01)
    
    states, policies, values = buffer.sample(batch_size=16)
    states_tensor = torch.from_numpy(states).float()
    policies_tensor = torch.from_numpy(policies).float()
    values_tensor = torch.from_numpy(values).float()
    
    loss = trainer.train_step(states_tensor, policies_tensor, values_tensor)
    assert isinstance(loss, float)
    assert loss >= 0

def test_model_save_load():
    board_size = 9
    net = GomokuNet(board_size=board_size, num_channels=32, num_res_blocks=3)
    
    manager = ModelManager(models_dir="test_models")
    
    path = manager.save_model(net, board_size, "test")
    assert path.exists()
    
    loaded_net = manager.load_model(board_size, "test")
    assert loaded_net is not None
    
    state1 = net.state_dict()
    state2 = loaded_net.state_dict()
    
    for (k1, v1), (k2, v2) in zip(state1.items(), state2.items()):
        assert torch.allclose(v1, v2)
    
    import shutil
    shutil.rmtree("test_models", ignore_errors=True)

def test_game_flow():
    board_size = 9
    net = GomokuNet(board_size=board_size, num_channels=32, num_res_blocks=2)
    
    board = Board(size=board_size)
    mcts = MCTS(board, net, simulations=30)
    
    moves = []
    while not board.is_game_over():
        mcts.search()
        best_move = mcts.get_best_move()
        if best_move is None:
            break
        moves.append(best_move)
        board.place_stone(*best_move)
        mcts.update_root(best_move)
    
    assert len(moves) > 0
    assert board.is_game_over()
    assert board.get_winner() in [1, -1, 0]
```

- [ ] **Step 2: 运行集成测试**

```bash
pytest tests/test_integration.py -v
```

Expected: All tests PASS

- [ ] **Step 3: 提交代码**

```bash
git add tests/test_integration.py
git commit -m "test: 添加集成测试"
```

---

### 任务 10: 项目文档和README

**Files:**
- Create: `gomoku_zero/README.md`

- [ ] **Step 1: 创建README**

```markdown
# GomokuZero 🎯

AlphaGo Zero 风格五子棋自对弈训练系统，支持多种棋盘尺寸和Web界面。

## 特性

- 🎮 **人机对弈**：使用训练好的模型与AI对弈
- ⚙️ **自对弈训练**：基于AlphaGo Zero算法的自我博弈学习
- 📊 **实时反馈**：显示AI胜率评估和候选落点
- 📱 **响应式Web界面**：支持手机、平板和桌面浏览器
- 🏁 **多尺寸支持**：9×9, 11×11, 13×13, 15×15 棋盘

## 安装

```bash
pip install -r requirements.txt
```

## 使用

### 启动Web界面

```bash
cd app
python main.py
```

访问 http://localhost:8000

### Python API 使用

```python
from app.models.gomoku_net import GomokuNet
from app.game.mcts import MCTS
from app.game.board import Board

# 创建网络
net = GomokuNet(board_size=9, num_channels=128, num_res_blocks=10)

# 创建棋盘和MCTS
board = Board(size=9)
mcts = MCTS(board, net, simulations=200)

# AI落子
mcts.search()
best_move = mcts.get_best_move()
```

### 自对弈训练

```python
from app.game.self_play import SelfPlay
from app.training.trainer import Trainer
from app.training.data_buffer import DataBuffer
import torch

net = GomokuNet(board_size=9)
sp = SelfPlay(net, board_size=9, simulations=100)
trainer = Trainer(net, board_size=9)
buffer = DataBuffer(board_size=9)

# 自对弈生成数据
games = sp.play_games(num_games=50)
for game in games:
    buffer.add_game(game)

# 训练
states, policies, values = buffer.sample(batch_size=32)
loss = trainer.train_step(
    torch.from_numpy(states).float(),
    torch.from_numpy(policies).float(),
    torch.from_numpy(values).float()
)
```

## 项目结构

```
gomoku_zero/
├── app/
│   ├── main.py              # FastAPI应用
│   ├── config.py            # 配置
│   ├── models/              # 神经网络
│   ├── game/                # 游戏逻辑
│   ├── training/            # 训练模块
│   └── api/                 # Web API
├── static/                  # 前端资源
├── templates/               # HTML模板
├── tests/                   # 测试
└── requirements.txt
```

## 训练建议

1. **入门**：从 9×9 棋盘开始，训练1000局即可验证算法
2. **提升**：使用 11×11 或 13×13 棋盘，效果更好
3. **完整**：15×15 标准五子棋，需要更长时间训练

## 技术栈

- PyTorch - 深度学习框架
- FastAPI - Web框架
- HTML5 Canvas - 棋盘绘制

## License

MIT
```

- [ ] **Step 2: 最终测试并提交**

```bash
pytest tests/ -v --tb=short
```

- [ ] **Step 3: 提交所有更改**

```bash
git add .
git commit -m "feat: 完成GomokuZero五子棋自对弈训练系统"
```

---

## 实施检查清单

- [x] 项目结构创建
- [ ] 棋盘逻辑实现（Board类）
- [ ] 神经网络实现（GomokuNet）
- [ ] MCTS算法实现
- [ ] 自对弈模块实现
- [ ] 训练器实现
- [ ] FastAPI后端实现
- [ ] Web前端界面实现
- [ ] 集成测试
- [ ] README文档

## 预期成果

✅ 可运行的五子棋AI对弈系统  
✅ 支持多种棋盘尺寸  
✅ Web界面响应式设计  
✅ AlphaGo Zero核心算法  
✅ 从小尺寸开始的训练流程
