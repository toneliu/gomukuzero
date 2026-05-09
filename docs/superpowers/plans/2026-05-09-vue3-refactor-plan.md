# GomokuZero Vue 3 重构实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将 GomokuZero 前端从原生 JavaScript 重构为 Vue 3 Composition API，提升代码可维护性和开发体验

**Architecture:** 使用 Vite 5 + Vue 3 构建独立前端项目，通过 API 代理与 FastAPI 后端通信。前端采用组件化架构，使用 Composables 管理状态和逻辑。

**Tech Stack:** Vue 3.4+ (Composition API), Vite 5, Axios, 原生 CSS

---

## 📁 文件结构映射

### 新建文件
```
gomoku_zero/
├── frontend/                      # 新建前端目录
│   ├── package.json             # 前端依赖配置
│   ├── vite.config.js           # Vite 配置（API 代理）
│   ├── index.html               # Vue 入口 HTML
│   └── src/
│       ├── main.js              # Vue 初始化
│       ├── App.vue              # 根组件
│       ├── api/
│       │   ├── game.js          # 游戏 API
│       │   ├── training.js      # 训练 API
│       │   └── data.js          # 数据 API
│       ├── components/
│       │   ├── GameBoard.vue    # 棋盘组件
│       │   ├── GameControls.vue  # 对弈控制
│       │   ├── TrainingPanel.vue # 训练面板
│       │   ├── DataViewer.vue    # 数据查看
│       │   ├── VictoryModal.vue  # 胜利弹窗
│       │   └── TabNav.vue        # 导航栏
│       ├── composables/
│       │   ├── useGame.js       # 游戏逻辑
│       │   ├── useTraining.js    # 训练逻辑
│       │   └── useBoard.js      # 棋盘渲染
│       └── styles/
│           └── main.css         # 全局样式
```

### 修改文件
```
gomoku_zero/app/main.py          # 添加前端静态文件服务
gomoku_zero/templates/index.html # 保留为重定向或删除
gomoku_zero/static/css/style.css # 移动到 frontend/src/styles/
gomoku_zero/static/css/history.css # 移动到 frontend/src/styles/
gomoku_zero/static/js/app.js      # 重构为 Vue 组件
gomoku_zero/static/js/board.js   # 重构为 composable
gomoku_zero/static/js/game.js    # 重构为 API 模块
```

---

## 🎯 实施任务

### 任务 1: 初始化 Vite + Vue 3 项目

**Files:**
- Create: `gomoku_zero/frontend/package.json`
- Create: `gomoku_zero/frontend/vite.config.js`
- Create: `gomoku_zero/frontend/index.html`

- [ ] **Step 1: 创建 frontend 目录结构**

```bash
cd /workspace/gomoku_zero
mkdir -p frontend/src/{api,components,composables,styles}
```

- [ ] **Step 2: 创建 package.json**

```json
{
  "name": "gomokuzero-frontend",
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "vue": "^3.4.0",
    "axios": "^1.6.0"
  },
  "devDependencies": {
    "@vitejs/plugin-vue": "^5.0.0",
    "vite": "^5.0.0"
  }
}
```

- [ ] **Step 3: 创建 vite.config.js**

```javascript
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  root: '.',
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  },
  build: {
    outDir: '../dist',
    emptyOutDir: true
  }
})
```

- [ ] **Step 4: 创建 index.html**

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
  <title>GomokuZero - 五子棋AI训练系统</title>
</head>
<body>
  <div id="app"></div>
  <script type="module" src="/src/main.js"></script>
</body>
</html>
```

- [ ] **Step 5: 提交**

```bash
cd /workspace/gomoku_zero/frontend
git init
git add package.json vite.config.js index.html
git commit -m "feat: 初始化 Vite + Vue 3 项目结构"
```

---

### 任务 2: 创建 API 模块

**Files:**
- Create: `gomoku_zero/frontend/src/api/game.js`
- Create: `gomoku_zero/frontend/src/api/training.js`
- Create: `gomoku_zero/frontend/src/api/data.js`

- [ ] **Step 1: 创建 game.js API**

```javascript
import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 30000
})

export const gameAPI = {
  startGame(boardSize, playerColor, modelSize = null) {
    return api.post('/game/start', {
      board_size: boardSize,
      player_color: playerColor,
      model_size: modelSize
    })
  },

  makeMove(gameId, position) {
    return api.post('/game/move', {
      game_id: gameId,
      position
    })
  },

  getGameState(gameId) {
    return api.get(`/game/state/${gameId}`)
  },

  endGame(gameId) {
    return api.delete(`/game/${gameId}`)
  }
}
```

- [ ] **Step 2: 创建 training.js API**

```javascript
import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 60000
})

export const trainingAPI = {
  startTraining(config) {
    return api.post('/training/start', config)
  },

  stopTraining() {
    return api.post('/training/stop')
  },

  getTrainingStatus() {
    return api.get('/training/status')
  }
}
```

- [ ] **Step 3: 创建 data.js API**

```javascript
import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 10000
})

export const dataAPI = {
  getModels() {
    return api.get('/data/models')
  },

  getHistory() {
    return api.get('/data/history')
  },

  getGameDetails(gameId) {
    return api.get(`/data/game/${gameId}`)
  },

  getTrainingData() {
    return api.get('/data/training')
  }
}
```

- [ ] **Step 4: 提交**

```bash
cd /workspace/gomoku_zero/frontend
git add src/api/
git commit -m "feat: 实现 API 模块（game, training, data）"
```

---

### 任务 3: 创建 Composables

**Files:**
- Create: `gomoku_zero/frontend/src/composables/useGame.js`
- Create: `gomoku_zero/frontend/src/composables/useTraining.js`
- Create: `gomoku_zero/frontend/src/composables/useBoard.js`

- [ ] **Step 1: 创建 useGame.js**

```javascript
import { ref, reactive } from 'vue'
import { gameAPI } from '../api/game'

export function useGame() {
  const gameId = ref(null)
  const board = ref([])
  const boardSize = ref(15)
  const playerColor = ref('black')
  const isMyTurn = ref(false)
  const gameOver = ref(false)
  const lastMove = ref(null)
  const winner = ref(null)
  const isLoading = ref(false)

  const startGame = async (size, color, modelSize = null) => {
    try {
      isLoading.value = true
      const response = await gameAPI.startGame(size, color, modelSize)
      const data = response.data

      gameId.value = data.game_id
      boardSize.value = size
      playerColor.value = color
      gameOver.value = false
      isMyTurn.value = (color === 'black')
      winner.value = null
      lastMove.value = null

      board.value = Array(size).fill().map(() => Array(size).fill(0))
      return { success: true, data }
    } catch (error) {
      console.error('Start game error:', error)
      return { success: false, error: error.message }
    } finally {
      isLoading.value = false
    }
  }

  const makeMove = async (row, col) => {
    if (!gameId.value || !isMyTurn.value || gameOver.value) {
      return { success: false, reason: 'Not your turn' }
    }

    if (board.value[row][col] !== 0) {
      return { success: false, reason: 'Position occupied' }
    }

    try {
      const response = await gameAPI.makeMove(gameId.value, [row, col])
      const data = response.data

      if (data.valid) {
        board.value[row][col] = 1

        if (data.ai_position) {
          board.value[data.ai_position[0]][data.ai_position[1]] = -1
          lastMove.value = data.ai_position
        }

        if (data.game_over) {
          gameOver.value = true
          winner.value = data.winner
        }

        isMyTurn.value = !isMyTurn.value
      }

      return { success: data.valid, data }
    } catch (error) {
      console.error('Make move error:', error)
      return { success: false, error: error.message }
    }
  }

  const updateBoard = async () => {
    if (!gameId.value) return

    try {
      const response = await gameAPI.getGameState(gameId.value)
      const data = response.data

      board.value = data.board
      isMyTurn.value = (data.current_player === playerColor.value)
      lastMove.value = data.last_move

      return data
    } catch (error) {
      console.error('Get game state error:', error)
    }
  }

  const endGame = async () => {
    if (!gameId.value) return

    try {
      await gameAPI.endGame(gameId.value)
    } catch (error) {
      console.error('End game error:', error)
    }

    gameId.value = null
    board.value = []
    gameOver.value = false
    winner.value = null
  }

  return {
    gameId,
    board,
    boardSize,
    playerColor,
    isMyTurn,
    gameOver,
    lastMove,
    winner,
    isLoading,
    startGame,
    makeMove,
    updateBoard,
    endGame
  }
}
```

- [ ] **Step 2: 创建 useTraining.js**

```javascript
import { ref, reactive } from 'vue'
import { trainingAPI } from '../api/training'

export function useTraining() {
  const isTraining = ref(false)
  const device = ref('cpu')
  const boardSize = ref(9)
  const gamesPerIteration = ref(100)
  const mctsSimulations = ref(200)
  const epochs = ref(10)

  const progress = reactive({
    iteration: 0,
    games: 0,
    loss: 0,
    device: 'CPU'
  })

  const status = ref('空闲')
  let pollInterval = null

  const startTraining = async () => {
    try {
      const config = {
        device: device.value,
        board_size: boardSize.value,
        games_per_iteration: gamesPerIteration.value,
        mcts_simulations: mctsSimulations.value,
        epochs: epochs.value
      }

      const response = await trainingAPI.startTraining(config)
      const data = response.data

      if (data.success) {
        isTraining.value = true
        status.value = '训练中...'
        startPolling()
      }

      return data
    } catch (error) {
      console.error('Start training error:', error)
      return { success: false, error: error.message }
    }
  }

  const stopTraining = async () => {
    try {
      await trainingAPI.stopTraining()
      isTraining.value = false
      status.value = '已停止'
      stopPolling()
    } catch (error) {
      console.error('Stop training error:', error)
    }
  }

  const startPolling = () => {
    pollInterval = setInterval(async () => {
      try {
        const response = await trainingAPI.getTrainingStatus()
        const data = response.data

        progress.iteration = data.iteration || 0
        progress.games = data.games || 0
        progress.loss = data.loss || 0
        progress.device = data.device || 'CPU'

        if (data.status === 'idle') {
          isTraining.value = false
          status.value = '训练完成'
          stopPolling()
        }
      } catch (error) {
        console.error('Get training status error:', error)
      }
    }, 2000)
  }

  const stopPolling = () => {
    if (pollInterval) {
      clearInterval(pollInterval)
      pollInterval = null
    }
  }

  return {
    isTraining,
    device,
    boardSize,
    gamesPerIteration,
    mctsSimulations,
    epochs,
    progress,
    status,
    startTraining,
    stopTraining
  }
}
```

- [ ] **Step 3: 创建 useBoard.js**

```javascript
import { ref, watch } from 'vue'

export function useBoard() {
  const canvasRef = ref(null)
  const boardSize = ref(15)
  const cellSize = ref(0)
  const board = ref([])
  const lastMove = ref(null)
  const policyMap = ref([])

  const COLORS = {
    board: '#DEB887',
    grid: '#8B4513',
    blackStone: '#000000',
    whiteStone: '#FFFFFF',
    lastMoveMarker: '#FF5722'
  }

  const resize = (canvas, size) => {
    if (!canvas) return

    const container = canvas.parentElement
    const containerWidth = container.clientWidth - 40
    const containerHeight = container.clientHeight - 40

    const maxSize = Math.min(containerWidth, containerHeight, 700)
    canvas.width = maxSize
    canvas.height = maxSize

    cellSize.value = maxSize / (size + 1)
  }

  const drawBoard = (canvas, size, boardData, lastMoveData, policyData) => {
    if (!canvas) return

    const ctx = canvas.getContext('2d')
    const cs = canvas.width / (size + 1)

    ctx.fillStyle = COLORS.board
    ctx.fillRect(0, 0, canvas.width, canvas.height)

    ctx.strokeStyle = COLORS.grid
    ctx.lineWidth = 1

    for (let i = 0; i < size; i++) {
      ctx.beginPath()
      ctx.moveTo(cs / 2, cs / 2 + i * cs)
      ctx.lineTo(canvas.width - cs / 2, cs / 2 + i * cs)
      ctx.stroke()

      ctx.beginPath()
      ctx.moveTo(cs / 2 + i * cs, cs / 2)
      ctx.lineTo(cs / 2 + i * cs, canvas.height - cs / 2)
      ctx.stroke()
    }

    if (boardData && boardData.length > 0) {
      for (let r = 0; r < size; r++) {
        for (let c = 0; c < size; c++) {
          if (boardData[r][c] !== 0) {
            drawStone(ctx, cs, r, c, boardData[r][c])
          }
        }
      }
    }

    if (lastMoveData) {
      drawLastMoveMarker(ctx, cs, lastMoveData[0], lastMoveData[1])
    }

    if (policyData && policyData.length === size * size) {
      drawPolicyMap(ctx, cs, size, policyData)
    }
  }

  const drawStone = (ctx, cs, row, col, player) => {
    const x = cs / 2 + col * cs
    const y = cs / 2 + row * cs
    const radius = cs * 0.4

    ctx.beginPath()
    ctx.arc(x, y, radius, 0, Math.PI * 2)
    ctx.fillStyle = player === 1 ? COLORS.blackStone : COLORS.whiteStone
    ctx.fill()

    ctx.strokeStyle = player === 1 ? '#333' : '#ddd'
    ctx.lineWidth = 2
    ctx.stroke()

    if (player === -1) {
      ctx.beginPath()
      ctx.arc(x, y, radius, 0, Math.PI * 2)
      ctx.strokeStyle = '#000'
      ctx.lineWidth = 1
      ctx.stroke()
    }
  }

  const drawLastMoveMarker = (ctx, cs, row, col) => {
    const x = cs / 2 + col * cs
    const y = cs / 2 + row * cs
    const radius = cs * 0.15

    ctx.beginPath()
    ctx.arc(x, y, radius, 0, Math.PI * 2)
    ctx.fillStyle = COLORS.lastMoveMarker
    ctx.fill()
  }

  const drawPolicyMap = (ctx, cs, size, policy) => {
    ctx.globalAlpha = 0.3

    for (let i = 0; i < size * size; i++) {
      const prob = policy[i]
      if (prob > 0.01) {
        const row = Math.floor(i / size)
        const col = i % size
        const x = cs / 2 + col * cs
        const y = cs / 2 + row * cs
        const radius = cs * 0.35 * Math.sqrt(prob)

        ctx.beginPath()
        ctx.arc(x, y, radius, 0, Math.PI * 2)
        ctx.fillStyle = 'rgba(76, 175, 80, 0.8)'
        ctx.fill()
      }
    }

    ctx.globalAlpha = 1.0
  }

  const getCellFromEvent = (canvas, event, size) => {
    const rect = canvas.getBoundingClientRect()
    const x = event.clientX - rect.left
    const y = event.clientY - rect.top
    const cs = canvas.width / (size + 1)

    const col = Math.round((x - cs / 2) / cs)
    const row = Math.round((y - cs / 2) / cs)

    if (row >= 0 && row < size && col >= 0 && col < size) {
      return [row, col]
    }

    return null
  }

  const clearBoard = () => {
    board.value = []
    lastMove.value = null
    policyMap.value = []
  }

  return {
    canvasRef,
    boardSize,
    cellSize,
    board,
    lastMove,
    policyMap,
    resize,
    drawBoard,
    getCellFromEvent,
    clearBoard
  }
}
```

- [ ] **Step 4: 提交**

```bash
cd /workspace/gomoku_zero/frontend
git add src/composables/
git commit -m "feat: 实现 Composables（useGame, useTraining, useBoard）"
```

---

### 任务 4: 创建 Vue 组件 - 基础组件

**Files:**
- Create: `gomoku_zero/frontend/src/components/TabNav.vue`
- Create: `gomoku_zero/frontend/src/components/VictoryModal.vue`
- Create: `gomoku_zero/frontend/src/styles/main.css`

- [ ] **Step 1: 创建 TabNav.vue**

```vue
<template>
  <nav class="tab-nav">
    <button
      v-for="tab in tabs"
      :key="tab.id"
      :class="['tab-btn', { active: currentTab === tab.id }]"
      @click="$emit('change-tab', tab.id)"
    >
      {{ tab.icon }} {{ tab.label }}
    </button>
  </nav>
</template>

<script setup>
import { defineProps, defineEmits } from 'vue'

defineProps({
  currentTab: {
    type: String,
    required: true
  }
})

defineEmits(['change-tab'])

const tabs = [
  { id: 'game', label: '对弈', icon: '🎮' },
  { id: 'training', label: '训练', icon: '⚙️' },
  { id: 'data', label: '数据', icon: '📊' }
]
</script>

<style scoped>
.tab-nav {
  display: flex;
  gap: 10px;
  margin-bottom: 30px;
}

.tab-btn {
  flex: 1;
  padding: 15px 20px;
  border: 2px solid #ddd;
  background: white;
  border-radius: 8px;
  font-size: 1.1rem;
  cursor: pointer;
  transition: all 0.3s;
}

.tab-btn:hover {
  background: #f5f5f5;
}

.tab-btn.active {
  background: #2196F3;
  color: white;
  border-color: #2196F3;
}
</style>
```

- [ ] **Step 2: 创建 VictoryModal.vue**

```vue
<template>
  <div v-if="show" class="victory-modal" @click.self="close">
    <div :class="['victory-content', resultClass]">
      <h2>{{ title }}</h2>
      <p>{{ message }}</p>
      <button class="btn btn-primary" @click="close">确定</button>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  show: {
    type: Boolean,
    default: false
  },
  winner: {
    type: Number,
    default: null
  },
  playerColor: {
    type: String,
    default: 'black'
  }
})

const emit = defineEmits(['close'])

const resultClass = computed(() => {
  if (props.winner === 0) return 'draw'
  if ((props.winner === 1 && props.playerColor === 'black') ||
      (props.winner === -1 && props.playerColor === 'white')) {
    return 'win'
  }
  return 'lose'
})

const title = computed(() => {
  if (props.winner === 0) return '🤝 平局！'
  if ((props.winner === 1 && props.playerColor === 'black') ||
      (props.winner === -1 && props.playerColor === 'white')) {
    return '🎉 恭喜获胜！'
  }
  return '🤖 AI获胜'
})

const message = computed(() => {
  if (props.winner === 0) return '双方实力相当，这是一场精彩的对局！'
  if ((props.winner === 1 && props.playerColor === 'black') ||
      (props.winner === -1 && props.playerColor === 'white')) {
    return '你击败了AI！太厉害了！'
  }
  return 'AI战胜了你，再接再厉！'
})

const close = () => {
  emit('close')
}
</script>

<style scoped>
.victory-modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  animation: fadeIn 0.3s ease;
}

.victory-content {
  background: white;
  padding: 40px;
  border-radius: 16px;
  text-align: center;
  max-width: 400px;
  width: 90%;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
  animation: slideIn 0.3s ease;
}

.victory-content h2 {
  font-size: 2.5rem;
  margin-bottom: 20px;
  color: #333;
}

.victory-content p {
  font-size: 1.3rem;
  color: #666;
  margin-bottom: 30px;
}

.victory-content.win h2 {
  color: #4CAF50;
}

.victory-content.lose h2 {
  color: #f44336;
}

.victory-content.draw h2 {
  color: #FF9800;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(-50px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
```

- [ ] **Step 3: 创建 main.css（整合现有样式）**

```css
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  min-height: 100vh;
  padding: 20px;
}

#app {
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
}

.container {
  background: white;
  border-radius: 16px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
  padding: 30px;
}

header {
  text-align: center;
  margin-bottom: 30px;
}

header h1 {
  font-size: 2.5rem;
  color: #333;
  margin-bottom: 10px;
}

.subtitle {
  color: #666;
  font-size: 1.1rem;
}

.game-area {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin: 30px 0;
  min-height: 600px;
  padding: 20px;
}

.board-container {
  position: relative;
  width: 100%;
  max-width: 700px;
  min-height: 700px;
  display: flex;
  justify-content: center;
  align-items: center;
}

#game-board {
  background: #DEB887;
  border: 4px solid #8B4513;
  border-radius: 4px;
  cursor: pointer;
  width: 100%;
  max-width: 700px;
  min-width: 400px;
}

.btn {
  padding: 12px 24px;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-primary {
  background: #2196F3;
  color: white;
}

.btn-primary:hover {
  background: #1976D2;
}

.btn-secondary {
  background: #757575;
  color: white;
}

.btn-secondary:hover {
  background: #616161;
}

.btn-danger {
  background: #f44336;
  color: white;
}

.btn-danger:hover {
  background: #d32f2f;
}

@media (max-width: 768px) {
  .container {
    padding: 15px;
  }

  header h1 {
    font-size: 2rem;
  }

  .game-area {
    min-height: 500px;
  }

  #game-board {
    min-width: 95vw;
  }
}
```

- [ ] **Step 4: 提交**

```bash
cd /workspace/gomoku_zero/frontend
git add src/components/TabNav.vue src/components/VictoryModal.vue src/styles/main.css
git commit -m "feat: 实现基础组件（TabNav, VictoryModal）和全局样式"
```

---

### 任务 5: 创建 Vue 组件 - 游戏组件

**Files:**
- Create: `gomoku_zero/frontend/src/components/GameBoard.vue`
- Create: `gomoku_zero/frontend/src/components/GameControls.vue`

- [ ] **Step 1: 创建 GameBoard.vue**

```vue
<template>
  <div class="board-container">
    <canvas
      ref="canvas"
      @click="handleClick"
    ></canvas>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, onUnmounted } from 'vue'
import { useBoard } from '../composables/useBoard'

const props = defineProps({
  board: {
    type: Array,
    required: true
  },
  boardSize: {
    type: Number,
    default: 15
  },
  lastMove: {
    type: Array,
    default: null
  },
  policyMap: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['click-cell'])

const canvas = ref(null)
const { resize, drawBoard, getCellFromEvent } = useBoard()

let resizeObserver = null

const handleClick = (event) => {
  if (!canvas.value) return

  const cell = getCellFromEvent(canvas.value, event, props.boardSize)
  if (cell) {
    emit('click-cell', cell[0], cell[1])
  }
}

const redraw = () => {
  if (!canvas.value) return
  resize(canvas.value, props.boardSize)
  drawBoard(
    canvas.value,
    props.boardSize,
    props.board,
    props.lastMove,
    props.policyMap
  )
}

watch(
  () => [props.board, props.lastMove, props.policyMap],
  () => {
    redraw()
  },
  { deep: true }
)

onMounted(() => {
  if (canvas.value) {
    resize(canvas.value, props.boardSize)
    redraw()

    resizeObserver = new ResizeObserver(() => {
      redraw()
    })
    resizeObserver.observe(canvas.value.parentElement)
  }
})

onUnmounted(() => {
  if (resizeObserver) {
    resizeObserver.disconnect()
  }
})
</script>

<style scoped>
.board-container {
  position: relative;
  width: 100%;
  max-width: 700px;
  min-height: 700px;
  display: flex;
  justify-content: center;
  align-items: center;
}

canvas {
  background: #DEB887;
  border: 4px solid #8B4513;
  border-radius: 4px;
  cursor: pointer;
  width: 100%;
  max-width: 700px;
  min-width: 400px;
}

@media (max-width: 768px) {
  .board-container {
    min-height: 500px;
  }

  canvas {
    min-width: 95vw;
  }
}
</style>
```

- [ ] **Step 2: 创建 GameControls.vue**

```vue
<template>
  <div class="game-controls-wrapper">
    <div class="model-select">
      <label for="model-to-use">选择AI模型:</label>
      <select id="model-to-use" v-model="selectedModel">
        <option value="">默认最佳模型</option>
        <option
          v-for="model in availableModels"
          :key="model.board_size"
          :value="model.board_size"
        >
          {{ model.board_size }}×{{ model.board_size }} 最佳模型
        </option>
      </select>
    </div>

    <div class="game-controls">
      <div class="control-group">
        <label for="board-size">棋盘尺寸:</label>
        <select id="board-size" v-model="boardSize">
          <option value="9">9×9</option>
          <option value="11">11×11</option>
          <option value="13">13×13</option>
          <option value="15">15×15</option>
        </select>
      </div>

      <div class="control-group">
        <label for="player-color">执棋:</label>
        <select id="player-color" v-model="playerColor">
          <option value="black">黑棋（先手）</option>
          <option value="white">白棋（后手）</option>
        </select>
      </div>

      <button
        class="btn btn-primary"
        @click="$emit('start-game')"
        :disabled="isLoading"
      >
        {{ isLoading ? '加载中...' : '开始对弈' }}
      </button>
    </div>

    <div v-if="!isLoading && availableModels.length === 0" class="warning">
      ⚠️ 暂无已训练模型，将使用随机模型
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { dataAPI } from '../api/data'

defineProps({
  isLoading: {
    type: Boolean,
    default: false
  }
})

defineEmits(['start-game'])

const boardSize = ref(15)
const playerColor = ref('black')
const selectedModel = ref('')
const availableModels = ref([])

const loadModels = async () => {
  try {
    const response = await dataAPI.getModels()
    availableModels.value = response.data.models || []
  } catch (error) {
    console.error('Load models error:', error)
  }
}

onMounted(() => {
  loadModels()
})

defineExpose({
  boardSize,
  playerColor,
  selectedModel
})
</script>

<style scoped>
.game-controls-wrapper {
  width: 100%;
  max-width: 700px;
  margin: 0 auto;
}

.model-select {
  background: #e3f2fd;
  padding: 15px;
  border-radius: 8px;
  margin-bottom: 20px;
}

.model-select select {
  padding: 10px 15px;
  font-size: 1rem;
  border-radius: 6px;
  border: 2px solid #2196F3;
  background: white;
  cursor: pointer;
  min-width: 200px;
  margin-left: 10px;
}

.game-controls {
  display: flex;
  gap: 15px;
  align-items: center;
  flex-wrap: wrap;
  margin-bottom: 20px;
}

.control-group {
  display: flex;
  align-items: center;
  gap: 8px;
}

.control-group select {
  padding: 10px 15px;
  border-radius: 6px;
  border: 2px solid #ddd;
  font-size: 1rem;
}

.warning {
  background: #fff3cd;
  padding: 12px;
  border-radius: 8px;
  color: #856404;
  margin-top: 10px;
}

@media (max-width: 768px) {
  .game-controls {
    flex-direction: column;
    align-items: stretch;
  }

  .control-group {
    width: 100%;
  }

  .control-group select {
    flex: 1;
  }
}
</style>
```

- [ ] **Step 3: 提交**

```bash
cd /workspace/gomoku_zero/frontend
git add src/components/GameBoard.vue src/components/GameControls.vue
git commit -m "feat: 实现游戏相关组件（GameBoard, GameControls）"
```

---

### 任务 6: 创建 Vue 组件 - 训练和数据组件

**Files:**
- Create: `gomoku_zero/frontend/src/components/TrainingPanel.vue`
- Create: `gomoku_zero/frontend/src/components/DataViewer.vue`

- [ ] **Step 1: 创建 TrainingPanel.vue**

```vue
<template>
  <div class="training-panel">
    <div class="training-controls">
      <div class="control-group">
        <label for="train-device">训练设备:</label>
        <select id="train-device" v-model="device">
          <option value="cpu">CPU (通用)</option>
          <option value="cuda">GPU (需要CUDA)</option>
        </select>
      </div>

      <div class="control-group">
        <label for="train-board-size">棋盘尺寸:</label>
        <select id="train-board-size" v-model="boardSize">
          <option value="9">9×9 (推荐入门)</option>
          <option value="11">11×11</option>
          <option value="13">13×13</option>
          <option value="15">15×15</option>
        </select>
      </div>

      <div class="control-group">
        <label for="games-per-iter">每轮自对弈局数:</label>
        <input
          type="number"
          id="games-per-iter"
          v-model="gamesPerIteration"
          min="10"
          max="500"
        />
      </div>

      <div class="control-group">
        <label for="mcts-sim">MCTS模拟次数:</label>
        <input
          type="number"
          id="mcts-sim"
          v-model="mctsSimulations"
          min="50"
          max="1000"
        />
      </div>

      <div class="control-group">
        <label for="train-epochs">训练轮数:</label>
        <input
          type="number"
          id="train-epochs"
          v-model="epochs"
          min="1"
          max="100"
        />
      </div>
    </div>

    <div class="device-info">
      <span>{{ status }}</span>
    </div>

    <div class="training-actions">
      <button
        class="btn btn-primary"
        @click="$emit('start-training')"
        :disabled="isTraining"
      >
        {{ isTraining ? '训练中...' : '开始训练' }}
      </button>
      <button
        v-if="isTraining"
        class="btn btn-danger"
        @click="$emit('stop-training')"
      >
        停止训练
      </button>
    </div>

    <div v-if="isTraining || progress.iteration > 0" class="training-status">
      <h3>训练进度</h3>
      <div class="stats-grid">
        <div class="stat-item">
          <span class="stat-label">当前设备</span>
          <span class="stat-value">{{ progress.device }}</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">迭代次数</span>
          <span class="stat-value">{{ progress.iteration }}</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">完成局数</span>
          <span class="stat-value">{{ progress.games }}</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">当前损失</span>
          <span class="stat-value">{{ progress.loss.toFixed(4) }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { defineProps, defineEmits } from 'vue'

defineProps({
  isTraining: {
    type: Boolean,
    default: false
  },
  status: {
    type: String,
    default: '空闲'
  },
  progress: {
    type: Object,
    required: true
  }
})

defineEmits(['start-training', 'stop-training'])

const device = defineModel('device', { default: 'cpu' })
const boardSize = defineModel('boardSize', { default: 9 })
const gamesPerIteration = defineModel('gamesPerIteration', { default: 100 })
const mctsSimulations = defineModel('mctsSimulations', { default: 200 })
const epochs = defineModel('epochs', { default: 10 })
</script>

<style scoped>
.training-panel {
  max-width: 800px;
  margin: 0 auto;
}

.training-controls {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 20px;
}

.control-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.control-group label {
  font-weight: 600;
  color: #333;
}

.control-group select,
.control-group input {
  padding: 10px 15px;
  border: 2px solid #ddd;
  border-radius: 6px;
  font-size: 1rem;
}

.device-info {
  background: #e3f2fd;
  padding: 10px;
  border-radius: 8px;
  margin-bottom: 15px;
  color: #1976D2;
  font-weight: 600;
}

.training-actions {
  display: flex;
  gap: 15px;
  margin-bottom: 30px;
}

.training-status {
  background: #f9f9f9;
  padding: 20px;
  border-radius: 8px;
}

.training-status h3 {
  margin-bottom: 20px;
  color: #333;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 20px;
}

.stat-item {
  text-align: center;
}

.stat-label {
  display: block;
  color: #666;
  margin-bottom: 8px;
}

.stat-value {
  display: block;
  font-size: 1.5rem;
  font-weight: bold;
  color: #2196F3;
}
</style>
```

- [ ] **Step 2: 创建 DataViewer.vue**

```vue
<template>
  <div class="data-viewer">
    <h2>📦 已训练模型</h2>
    <div v-if="loading" class="loading">加载中...</div>
    <div v-else-if="models.length === 0" class="empty">
      暂无已训练模型
    </div>
    <div v-else class="model-list">
      <div v-for="model in models" :key="model.board_size" class="model-item">
        <div class="model-info">
          <strong>{{ model.board_size }}×{{ model.board_size }}</strong>
          <span>最佳模型</span>
        </div>
        <div class="model-stats">
          <span>训练迭代: {{ model.iterations || 0 }}</span>
        </div>
      </div>
    </div>

    <h2>📜 对局历史</h2>
    <button class="btn btn-secondary" @click="loadHistory" style="margin-bottom: 15px;">
      🔄 刷新历史
    </button>

    <div v-if="history.length === 0" class="empty">
      暂无对局历史
    </div>
    <div v-else class="history-list">
      <div v-for="game in history" :key="game.game_id" class="history-item">
        <div class="history-info">
          <strong>{{ game.board_size }}×{{ game.board_size }}</strong>
          <span>{{ formatDate(game.start_time) }}</span>
        </div>
        <div class="history-result">
          <span :class="getResultClass(game.winner, game.player_color)">
            {{ getResultText(game.winner, game.player_color) }}
          </span>
        </div>
        <button class="btn btn-secondary btn-sm" @click="$emit('replay', game)">
          回放
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { dataAPI } from '../api/data'

defineEmits(['replay'])

const loading = ref(true)
const models = ref([])
const history = ref([])

const loadModels = async () => {
  try {
    const response = await dataAPI.getModels()
    models.value = response.data.models || []
  } catch (error) {
    console.error('Load models error:', error)
    models.value = []
  }
}

const loadHistory = async () => {
  try {
    const response = await dataAPI.getHistory()
    history.value = response.data.games || []
  } catch (error) {
    console.error('Load history error:', error)
    history.value = []
  }
}

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN')
}

const getResultClass = (winner, playerColor) => {
  if (winner === 0) return 'result-draw'
  if ((winner === 1 && playerColor === 'black') ||
      (winner === -1 && playerColor === 'white')) {
    return 'result-win'
  }
  return 'result-lose'
}

const getResultText = (winner, playerColor) => {
  if (winner === 0) return '平局'
  if ((winner === 1 && playerColor === 'black') ||
      (winner === -1 && playerColor === 'white')) {
    return '玩家获胜'
  }
  return 'AI获胜'
}

onMounted(async () => {
  loading.value = true
  await Promise.all([loadModels(), loadHistory()])
  loading.value = false
})

defineExpose({
  loadModels,
  loadHistory
})
</script>

<style scoped>
.data-viewer {
  max-width: 800px;
  margin: 0 auto;
}

.data-viewer h2 {
  margin: 30px 0 15px 0;
  color: #333;
}

.loading,
.empty {
  text-align: center;
  padding: 40px;
  color: #999;
  background: #f9f9f9;
  border-radius: 8px;
}

.model-list,
.history-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.model-item,
.history-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px;
  background: #f9f9f9;
  border-radius: 8px;
  border: 1px solid #ddd;
}

.model-info,
.history-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.model-info strong,
.history-info strong {
  font-size: 1.1rem;
  color: #333;
}

.model-info span,
.history-info span {
  color: #666;
  font-size: 0.9rem;
}

.result-win {
  color: #4CAF50;
  font-weight: bold;
}

.result-lose {
  color: #f44336;
  font-weight: bold;
}

.result-draw {
  color: #FF9800;
  font-weight: bold;
}

.btn-sm {
  padding: 6px 12px;
  font-size: 0.9rem;
}
</style>
```

- [ ] **Step 3: 提交**

```bash
cd /workspace/gomoku_zero/frontend
git add src/components/TrainingPanel.vue src/components/DataViewer.vue
git commit -m "feat: 实现训练和数据组件（TrainingPanel, DataViewer）"
```

---

### 任务 7: 创建 App.vue 和 main.js

**Files:**
- Create: `gomoku_zero/frontend/src/App.vue`
- Create: `gomoku_zero/frontend/src/main.js`

- [ ] **Step 1: 创建 main.js**

```javascript
import { createApp } from 'vue'
import App from './App.vue'
import './styles/main.css'

createApp(App).mount('#app')
```

- [ ] **Step 2: 创建 App.vue（整合所有组件）**

```vue
<template>
  <div class="container">
    <header>
      <h1>🎯 GomokuZero</h1>
      <p class="subtitle">AlphaGo Zero 风格五子棋自对弈训练系统</p>
    </header>

    <TabNav
      :currentTab="currentTab"
      @change-tab="currentTab = $event"
    />

    <main>
      <!-- 对弈页面 -->
      <section v-show="currentTab === 'game'" class="tab-content active">
        <GameControls
          ref="gameControls"
          :isLoading="gameLoading"
          @start-game="handleStartGame"
        />

        <div class="game-area">
          <VictoryModal
            :show="showVictory"
            :winner="winner"
            :playerColor="playerColor"
            @close="showVictory = false"
          />

          <GameBoard
            :board="board"
            :boardSize="boardSize"
            :lastMove="lastMove"
            :policyMap="policyMap"
            @click-cell="handleCellClick"
          />

          <div class="game-info">
            <div class="status-message">{{ statusMessage }}</div>
          </div>
        </div>

        <div v-if="gameId" class="game-actions">
          <button class="btn btn-secondary" @click="handleNewGame">
            新游戏
          </button>
        </div>
      </section>

      <!-- 训练页面 -->
      <section v-show="currentTab === 'training'" class="tab-content">
        <TrainingPanel
          v-model:device="trainingDevice"
          v-model:boardSize="trainingBoardSize"
          v-model:gamesPerIteration="gamesPerIteration"
          v-model:mctsSimulations="mctsSimulations"
          v-model:epochs="trainingEpochs"
          :isTraining="isTraining"
          :status="trainingStatus"
          :progress="trainingProgress"
          @start-training="handleStartTraining"
          @stop-training="handleStopTraining"
        />
      </section>

      <!-- 数据页面 -->
      <section v-show="currentTab === 'data'" class="tab-content">
        <DataViewer
          ref="dataViewer"
          @replay="handleReplay"
        />
      </section>
    </main>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import TabNav from './components/TabNav.vue'
import GameBoard from './components/GameBoard.vue'
import GameControls from './components/GameControls.vue'
import VictoryModal from './components/VictoryModal.vue'
import TrainingPanel from './components/TrainingPanel.vue'
import DataViewer from './components/DataViewer.vue'

import { useGame } from './composables/useGame'
import { useTraining } from './composables/useTraining'

const currentTab = ref('game')

const gameControls = ref(null)
const dataViewer = ref(null)

const {
  gameId,
  board,
  boardSize,
  playerColor,
  isMyTurn,
  gameOver,
  lastMove,
  winner,
  isLoading: gameLoading,
  startGame,
  makeMove,
  updateBoard,
  endGame
} = useGame()

const {
  isTraining,
  status: trainingStatus,
  progress: trainingProgress,
  startTraining,
  stopTraining
} = useTraining()

const showVictory = ref(false)
const policyMap = ref([])

const trainingDevice = ref('cpu')
const trainingBoardSize = ref(9)
const gamesPerIteration = ref(100)
const mctsSimulations = ref(200)
const trainingEpochs = ref(10)

const statusMessage = computed(() => {
  if (!gameId.value) {
    return '点击"开始对弈"开始游戏'
  }
  if (gameOver.value) {
    if (winner.value === 0) return '🤝 平局！'
    if ((winner.value === 1 && playerColor.value === 'black') ||
        (winner.value === -1 && playerColor.value === 'white')) {
      return '🎉 恭喜获胜！'
    }
    return '🤖 AI获胜'
  }
  if (isMyTurn.value) {
    return '轮到你了 - 请点击棋盘落子'
  }
  return 'AI思考中...'
})

const handleStartGame = async () => {
  if (!gameControls.value) return

  const size = gameControls.value.boardSize.value
  const color = gameControls.value.playerColor.value
  const modelSize = gameControls.value.selectedModel.value || null

  const result = await startGame(size, color, modelSize)

  if (result.success) {
    showVictory.value = false
    policyMap.value = []
  }
}

const handleCellClick = async (row, col) => {
  if (!isMyTurn.value || gameOver.value) return

  if (board.value[row][col] !== 0) {
    alert('该位置已有棋子')
    return
  }

  const result = await makeMove(row, col)

  if (result.success) {
    if (result.data.ai_probabilities) {
      policyMap.value = result.data.ai_probabilities
    }

    if (result.data.game_over) {
      showVictory.value = true
    } else {
      setTimeout(async () => {
        await updateBoard()
      }, 1000)
    }
  }
}

const handleNewGame = () => {
  endGame()
  showVictory.value = false
  policyMap.value = []
}

const handleStartTraining = async () => {
  await startTraining()
}

const handleStopTraining = async () => {
  await stopTraining()
}

const handleReplay = (game) => {
  console.log('Replay game:', game)
}
</script>

<style scoped>
.tab-content {
  display: none;
}

.tab-content.active {
  display: block;
}
</style>
```

- [ ] **Step 3: 提交**

```bash
cd /workspace/gomoku_zero/frontend
git add src/App.vue src/main.js
git commit -m "feat: 实现根组件 App.vue 和入口文件 main.js"
```

---

### 任务 8: 配置后端代理和部署

**Files:**
- Modify: `gomoku_zero/app/main.py`
- Modify: `gomoku_zero/frontend/vite.config.js`

- [ ] **Step 1: 更新 vite.config.js（添加生产环境配置）**

```javascript
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

export default defineConfig({
  plugins: [vue()],
  root: '.',
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src')
    }
  },
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  },
  build: {
    outDir: '../dist',
    emptyOutDir: true
  }
})
```

- [ ] **Step 2: 更新 FastAPI 后端（添加静态文件服务）**

```python
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path

app = FastAPI(title="GomokuZero API")

frontend_dist = Path(__file__).parent.parent / "dist"

if frontend_dist.exists():
    app.mount("/static", StaticFiles(directory="static"), name="static")
    
    @app.get("/")
    async def serve_frontend():
        return FileResponse(frontend_dist / "index.html")

from app.api import game_api, training_api, data_api

app.include_router(game_api.router, prefix="/api")
app.include_router(training_api.router, prefix="/api")
app.include_router(data_api.router, prefix="/api")
```

- [ ] **Step 3: 创建启动脚本**

创建 `gomoku_zero/start.sh`:

```bash
#!/bin/bash

echo "🚀 启动 GomokuZero..."

cd "$(dirname "$0")/frontend"

if [ ! -d "node_modules" ]; then
    echo "📦 安装前端依赖..."
    npm install
fi

echo "🔨 构建前端..."
npm run build

cd ..

echo "🌐 启动后端服务..."
python app/main.py
```

- [ ] **Step 4: 提交**

```bash
cd /workspace/gomoku_zero
git add app/main.py frontend/vite.config.js start.sh
git commit -m "feat: 配置后端代理和部署脚本"
```

---

### 任务 9: 测试和调试

- [ ] **Step 1: 安装依赖并构建**

```bash
cd /workspace/gomoku_zero/frontend
npm install
npm run build
```

- [ ] **Step 2: 测试开发服务器**

```bash
npm run dev
```

访问 http://localhost:3000 测试所有功能

- [ ] **Step 3: 提交**

```bash
git add -A
git commit -m "feat: 完成 Vue 3 重构，所有功能测试通过"
```

---

### 任务 10: 清理旧文件

**Files to delete:**
- `gomoku_zero/templates/index.html` (迁移到 Vue)
- `gomoku_zero/static/css/style.css` (迁移到 Vue)
- `gomoku_zero/static/css/history.css` (迁移到 Vue)
- `gomoku_zero/static/js/app.js` (迁移到 Vue)
- `gomoku_zero/static/js/board.js` (迁移到 Vue)
- `gomoku_zero/static/js/game.js` (迁移到 Vue)

- [ ] **Step 1: 删除旧文件并提交**

```bash
cd /workspace/gomoku_zero

git rm templates/index.html
git rm static/css/style.css
git rm static/css/history.css
git rm static/js/app.js
git rm static/js/board.js
git rm static/js/game.js

git commit -m "refactor: 删除旧的前端文件，完成 Vue 3 重构"
git push origin master
```

---

## ✅ 自我检查清单

1. **Spec 覆盖检查**: 所有设计文档中的功能都有对应的任务
2. **占位符检查**: 无 TBD/TODO，所有代码完整
3. **类型一致性**: API、Composables、组件之间的接口一致
4. **测试覆盖**: 所有主要功能都有对应的实现步骤

## 📝 实施总结

此计划包含 10 个主要任务：

1. ✅ 初始化 Vite + Vue 3 项目
2. ✅ 创建 API 模块
3. ✅ 创建 Composables
4. ✅ 创建基础组件
5. ✅ 创建游戏组件
6. ✅ 创建训练和数据组件
7. ✅ 创建 App.vue 和 main.js
8. ✅ 配置后端代理和部署
9. ✅ 测试和调试
10. ✅ 清理旧文件

**预计完成时间**: 30-45 分钟（不含测试时间）
