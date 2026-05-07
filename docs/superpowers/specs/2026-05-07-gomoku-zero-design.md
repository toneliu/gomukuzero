# AlphaGo Zero 风格五子棋自对弈训练系统设计

## 项目概述

**项目名称**：GomokuZero  
**项目类型**：AlphaGo Zero 风格的自对弈强化学习系统  
**核心功能**：
- 支持多种棋盘尺寸（9×9, 11×11, 13×13, 15×15, 19×19）
- 神经网络驱动的蒙特卡洛树搜索（MCTS）
- 自对弈训练 + 模型优化
- Web 界面人机对弈（响应式，兼容手机）
- 训练数据查看与管理

**技术栈**：
- 后端：Python 3.8+ / PyTorch / FastAPI
- 前端：HTML5 / CSS3 / JavaScript（响应式设计）
- 通信：REST API + WebSocket

---

## 系统架构

```
┌─────────────────┐
│   Web Browser   │  ← 响应式界面（手机/平板/桌面）
│   (用户界面)    │
└────────┬────────┘
         │ HTTP/WebSocket
         ↓
┌─────────────────┐
│   FastAPI       │  ← API 服务
│   (后端服务)    │
├────────┬────────┤
│        │        │
↓        ↓        ↓
┌───┐ ┌─────┐ ┌──────┐
│MCTS│ │训练 │ │模型  │
│模块│ │模块 │ │推理  │
└───┘ └─────┘ └──────┘
         ↓
┌─────────────────┐
│  PyTorch 模型  │
│  (神经网络)     │
└─────────────────┘
```

---

## 核心模块设计

### 1. 神经网络模块 (`neural_network.py`)

**架构**：ResNet with 双头输出

```
输入层：动态尺寸 × 历史层数（4层：当前+3历史）
    ↓
卷积层：输入通道4 → 输出通道128
    ↓
残差块 × 10（可配置）
    │
    ├── 卷积 128→128 × 2
    ├── BatchNorm
    └── 残差连接
    │
    ↓
┌───────────────┐
│  策略头       │
│  自适应池化   │
│  全连接→225   │
│  Softmax      │
└───────────────┘
┌───────────────┐
│  价值头       │
│  自适应池化   │
│  全连接→1     │
│  Sigmoid      │
└───────────────┘
```

**特点**：
- 自适应池化支持多尺寸棋盘
- 策略头输出根据棋盘大小动态调整
- 共享特征提取层 + 独立任务头

### 2. 蒙特卡洛树搜索模块 (`mcts.py`)

**核心算法**：AlphaGo Zero PUCT

```
PUCT = Q(s,a) + U(s,a)
     = (W(s,a)/N(s,a)) + c_puct × P(s,a) × sqrt(N(s))/1+N(s,a)

其中：
- Q(s,a): 平均动作价值
- U(s,a): 探索奖励（基于先验概率）
- P(s,a): 神经网络输出的先验概率
- c_puct: 探索常数（默认1.5）
```

**搜索流程**：
1. 从根节点开始，选择最高PUCT的子节点
2. 递归直到叶节点
3. 扩展叶节点，用神经网络评估
4. 反向传播更新统计信息

### 3. 自对弈模块 (`self_play.py`)

**自对弈流程**：
```
while 游戏未结束:
    1. 运行MCTS（400次模拟）
    2. 根据π采样落子
    3. 记录 (状态, π, 奖励) 到数据缓冲区
    
游戏结束:
    存储完整对局数据
    胜者奖励 +1，败者 -1
```

**数据格式**：
```python
{
    "states": [np.array, ...],      # 每步的棋盘状态
    "policies": [np.array, ...],     # 每步的MCTS策略
    "values": [float, ...],         # 每步的终局奖励
    "board_size": int,               # 棋盘尺寸
    "game_id": str                   # 对局ID
}
```

### 4. 训练模块 (`training.py`)

**损失函数**：
```
L = (z - v)² + π·log(p) + λ||θ||²

其中：
- (z - v)²: 价值损失（均方误差）
- π·log(p): 策略损失（交叉熵）
- λ||θ||²: L2正则化
```

**训练循环**：
```
for epoch in range(num_epochs):
    1. 从自对弈数据采样batch
    2. 前向传播计算损失
    3. 反向传播更新参数
    4. 定期评估模型性能
    5. 保存最佳模型
```

---

## 前端设计

### 页面结构

**1. 主页 / 对弈页面**
- 棋盘区域（响应式居中）
- 控制面板
- AI信息栏（可选：胜率热力图、候选点）
- 操作按钮

**2. 训练控制页面**
- 训练参数设置
- 训练状态显示
- 进度条
- 暂停/继续/停止按钮

**3. 数据查看页面**
- 模型列表
- 训练历史图表
- 统计数据

### 响应式设计

**手机端（<768px）**：
- 竖屏布局
- 棋盘宽度 90vw
- 顶部工具栏
- 底部操作按钮

**平板/桌面（≥768px）**：
- 横屏布局
- 棋盘固定最大宽度
- 侧边控制面板

### 棋盘渲染

- HTML5 Canvas 绘制
- 触摸/点击事件处理
- 落子动画
- 热力图叠加显示

---

## 数据管理

### 目录结构

```
gomoku_zero/
├── models/
│   ├── model_9x9_best.pth      # 最佳模型
│   ├── model_9x9_latest.pth    # 最新模型
│   ├── model_11x11_best.pth
│   ├── model_15x15_best.pth
│   └── model_19x19_best.pth
│
├── training_data/
│   ├── data_9x9/
│   │   ├── game_001.npz
│   │   ├── game_002.npz
│   │   └── ...
│   ├── data_11x11/
│   ├── data_15x15/
│   └── data_19x19/
│
├── logs/
│   ├── training_2026-05-07.json
│   └── games_stats.json
│
├── app/
│   ├── main.py                 # FastAPI入口
│   ├── api/
│   │   ├── game.py             # 对弈API
│   │   ├── training.py         # 训练API
│   │   └── data.py             # 数据API
│   ├── game/
│   │   ├── board.py            # 棋盘逻辑
│   │   ├── neural_network.py   # 神经网络
│   │   ├── mcts.py             # MCTS搜索
│   │   └── self_play.py        # 自对弈
│   ├── training/
│   │   └── trainer.py          # 训练器
│   └── models/
│       └── gomoku_model.py      # 模型定义
│
├── static/
│   ├── css/
│   │   └── style.css
│   └── js/
│       ├── board.js            # 棋盘组件
│       ├── game.js             # 对弈逻辑
│       └── training.js         # 训练控制
│
├── templates/
│   └── index.html              # 主页面
│
└── requirements.txt
```

---

## 训练策略

### 分阶段训练

**阶段1：小棋盘入门（9×9）**
- 目标：验证算法正确性
- 训练时间：几小时（CPU可运行）
- 自对弈局数：500-1000
- MCTS模拟：200次

**阶段2：中等棋盘（11×11 / 13×13）**
- 目标：提升棋力
- 训练时间：1-2天（推荐GPU）
- 自对弈局数：2000-5000
- MCTS模拟：400次

**阶段3：标准棋盘（15×15）**
- 目标：达到较高水平
- 训练时间：1周+（需要GPU）
- 自对弈局数：10000+
- MCTS模拟：600次

**阶段4：扩展棋盘（19×19）**
- 目标：极限挑战
- 需要强大的计算资源

### 默认配置

```yaml
默认训练配置:
  board_size: 9
  self_play_games: 500
  mcts_simulations: 200
  batch_size: 128
  learning_rate: 0.01
  lr_decay: 0.9
  train_epochs: 50
  num_res_blocks: 10
  num_channels: 128
  history_len: 4
```

---

## API 设计

### 对弈 API

**POST /api/game/start**
```json
请求: { "board_size": 9, "model": "best" }
响应: { "game_id": "xxx", "player_color": "black" }
```

**POST /api/game/move**
```json
请求: { "game_id": "xxx", "position": [3, 4] }
响应: { "ai_position": [5, 6], "game_over": false }
```

**GET /api/game/state/{game_id}**
```json
响应: {
  "board": [[0,0,...], ...],
  "current_player": "black",
  "last_move": [5, 6],
  "ai_probabilities": [[...], ...]
}
```

### 训练 API

**POST /api/training/start**
```json
请求: {
  "board_size": 9,
  "games_per_iteration": 100,
  "mcts_simulations": 200,
  "train_epochs": 10
}
响应: { "training_id": "xxx", "status": "running" }
```

**GET /api/training/status**
```json
响应: {
  "status": "running",
  "iteration": 5,
  "games_completed": 450,
  "loss": 0.234,
  "accuracy": 0.76
}
```

**POST /api/training/stop**
**GET /api/training/history**

### 数据 API

**GET /api/models/list**
**GET /api/models/{size}/info**
**GET /api/training/stats**
**GET /api/games/{game_id}**

---

## 用户交互流程

```
1. 启动应用
   └── 显示主界面（Web页面）

2. 选择功能
   ├── 【对弈模式】
   │   ├── 选择棋盘尺寸
   │   ├── 选择AI模型（或默认最佳）
   │   ├── 开始对弈
   │   └── 实时显示AI思考信息
   │
   ├── 【训练模式】
   │   ├── 设置训练参数
   │   ├── 启动训练
   │   └── 监控训练进度
   │
   └── 【数据查看】
       ├── 查看模型列表
       ├── 查看训练历史
       └── 统计数据

3. 结束
   └── 可切换其他功能
```

---

## 成功标准

1. ✅ 9×9棋盘训练后，AI能正确识别基本战术（活三、冲四等）
2. ✅ Web界面在手机和桌面浏览器均可正常使用
3. ✅ 支持多种棋盘尺寸无缝切换
4. ✅ 训练过程稳定，损失函数收敛
5. ✅ 模型可保存加载，断点续训

---

## 下一步

待用户批准此设计后，将创建详细的实现计划。
