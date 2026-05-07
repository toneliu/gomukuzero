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
cd gomoku_zero/app
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
│   │   ├── gomoku_net.py    # 神经网络模型
│   │   └── model_manager.py  # 模型管理
│   ├── game/                # 游戏逻辑
│   │   ├── board.py         # 棋盘类
│   │   ├── mcts.py          # MCTS算法
│   │   └── self_play.py     # 自对弈
│   ├── training/            # 训练模块
│   │   ├── trainer.py        # 训练器
│   │   └── data_buffer.py   # 数据缓冲区
│   └── api/                  # Web API
│       ├── game_api.py       # 对弈API
│       ├── training_api.py   # 训练API
│       └── data_api.py       # 数据API
├── static/                  # 前端资源
│   ├── css/
│   └── js/
├── templates/               # HTML模板
├── tests/                   # 测试
├── models/                  # 保存的模型
└── requirements.txt
```

## 训练建议

1. **入门**：从 9×9 棋盘开始，训练1000局即可验证算法
2. **提升**：使用 11×11 或 13×13 棋盘，效果更好
3. **完整**：15×15 标准五子棋，需要更长时间训练

## 运行测试

```bash
pytest gomoku_zero/tests/ -v
```

## 技术栈

- PyTorch - 深度学习框架
- FastAPI - Web框架
- HTML5 Canvas - 棋盘绘制
- JavaScript - 前端交互

## License

MIT
