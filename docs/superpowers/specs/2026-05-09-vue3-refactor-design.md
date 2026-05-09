# GomokuZero Vue 3 重构设计文档

## 📅 日期：2026-05-09

## 🎯 项目背景

将 GomokuZero 前端从原生 JavaScript 重构为 Vue 3 Composition API，提升代码可维护性和开发体验。

## 📁 目标项目结构

```
gomoku_zero/
├── frontend/                    # 新建前端目录
│   ├── vite.config.js         # Vite 配置
│   ├── package.json           # 前端依赖
│   ├── index.html             # Vue 入口
│   └── src/
│       ├── main.js            # Vue 初始化
│       ├── App.vue            # 根组件
│       ├── api/
│       │   ├── game.js        # 游戏 API
│       │   ├── training.js    # 训练 API
│       │   └── data.js        # 数据 API
│       ├── components/
│       │   ├── GameBoard.vue      # 棋盘组件
│       │   ├── GameControls.vue    # 对弈控制
│       │   ├── TrainingPanel.vue  # 训练面板
│       │   ├── DataViewer.vue     # 数据查看
│       │   ├── VictoryModal.vue   # 胜利弹窗
│       │   └── TabNav.vue         # 导航栏
│       ├── composables/
│       │   ├── useGame.js         # 游戏逻辑
│       │   ├── useTraining.js     # 训练逻辑
│       │   └── useBoard.js        # 棋盘渲染
│       └── styles/
│           └── main.css           # 全局样式
└── app/
    └── main.py               # FastAPI 后端（不变）
```

## 🏗️ 架构设计

### 1. 根组件 App.vue
- 管理全局状态（当前Tab）
- 提供全局布局
- 包含 TabNav 导航组件

### 2. 功能模块组件

#### GameBoard.vue
- 职责：棋盘绘制和交互
- 技术：Canvas + 响应式设计
- Props: boardSize, board, lastMove, policyMap
- Events: @click-cell

#### GameControls.vue
- 职责：对弈控制面板
- 内容：模型选择、棋盘尺寸、玩家颜色、开始/新游戏按钮
- 状态：gameState, availableModels

#### TrainingPanel.vue
- 职责：训练配置和状态显示
- 内容：设备选择、训练参数、进度显示
- 状态：trainingProgress, deviceStatus

#### DataViewer.vue
- 职责：查看模型和历史记录
- 内容：模型列表、对局历史、回放功能
- 状态：models, history

#### VictoryModal.vue
- 职责：游戏结束胜利提示
- Props: show, winner, playerColor
- Events: @close

#### TabNav.vue
- 职责：页面导航
- 内容：对弈、训练、数据标签
- Events: @change-tab

### 3. Composables（逻辑复用）

#### useGame.js
```javascript
// 游戏状态管理
export function useGame() {
  // 状态
  const gameId = ref(null)
  const board = ref([])
  const boardSize = ref(15)
  const playerColor = ref('black')
  const isMyTurn = ref(false)
  const gameOver = ref(false)

  // 方法
  const startGame = async (size, color, modelSize) => {...}
  const makeMove = async (row, col) => {...}
  const getGameState = async () => {...}

  return { gameId, board, boardSize, playerColor, isMyTurn, gameOver, startGame, makeMove, getGameState }
}
```

#### useTraining.js
```javascript
// 训练状态管理
export function useTraining() {
  // 状态
  const isTraining = ref(false)
  const device = ref('cpu')
  const progress = reactive({
    iteration: 0,
    games: 0,
    loss: 0
  })

  // 方法
  const startTraining = async (config) => {...}
  const stopTraining = async () => {...}

  return { isTraining, device, progress, startTraining, stopTraining }
}
```

#### useBoard.js
```javascript
// 棋盘渲染逻辑
export function useBoard(canvasRef, boardSize) {
  // 状态
  const cellSize = ref(0)

  // 方法
  const resize = () => {...}
  const drawBoard = (board) => {...}
  const setLastMove = (move) => {...}
  const setPolicyMap = (probabilities) => {...}
  const getCellFromEvent = (event) => {...}

  return { cellSize, resize, drawBoard, setLastMove, setPolicyMap, getCellFromEvent }
}
```

### 4. API 模块

#### api/game.js
```javascript
import axios from 'axios'

export const gameAPI = {
  startGame: (boardSize, playerColor, modelSize) =>
    axios.post('/api/game/start', { board_size: boardSize, player_color: playerColor, model_size: modelSize }),

  makeMove: (gameId, position) =>
    axios.post('/api/game/move', { game_id: gameId, position }),

  getGameState: (gameId) =>
    axios.get(`/api/game/state/${gameId}`)
}
```

#### api/training.js
```javascript
import axios from 'axios'

export const trainingAPI = {
  startTraining: (config) =>
    axios.post('/api/training/start', config),

  stopTraining: () =>
    axios.post('/api/training/stop')
}
```

#### api/data.js
```javascript
import axios from 'axios'

export const dataAPI = {
  getModels: () => axios.get('/api/data/models'),
  getHistory: () => axios.get('/api/data/history'),
  getGameDetails: (gameId) => axios.get(`/api/data/game/${gameId}`)
}
```

## 🔄 数据流

```
用户操作 → Vue 组件 → API 调用 → FastAPI
                              ↓
FastAPI → API 返回 → Vue 响应式状态 → 组件重新渲染
```

## ✨ 主要改进

1. **更好的状态管理** - Vue 3 reactive/ref
2. **代码组织清晰** - 组件化、模块化、Composables
3. **维护性提升** - 清晰的文件结构
4. **开发体验** - Vite HMR、热更新
5. **性能优化** - Virtual DOM、按需加载

## 📦 技术栈

- Vue 3.4+ (Composition API)
- Vite 5
- Axios (HTTP 客户端)
- 原生 CSS (复用现有样式)

## ✅ 实施步骤

1. 初始化 Vite + Vue 3 项目
2. 创建项目目录结构
3. 实现 API 模块
4. 实现 Composables
5. 实现各个 Vue 组件
6. 集成所有组件到 App.vue
7. 配置 Vite 代理（API 转发到 FastAPI）
8. 测试和调试
9. 清理旧的前端文件

## 🎯 成功标准

- 所有现有功能正常工作
- 代码组织清晰、可维护
- 开发体验流畅
- 无明显性能问题
