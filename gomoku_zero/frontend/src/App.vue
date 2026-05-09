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
          v-model:boardSize="gameBoardSize"
          v-model:playerColor="gamePlayerColor"
          :isLoading="gameLoading"
          @start-game="handleStartGame"
        />

        <div class="game-area">
          <VictoryModal
            :show="showVictory"
            :winner="winner"
            :playerColor="gamePlayerColor"
            @close="showVictory = false"
          />

          <GameBoard
            :board="board"
            :boardSize="gameBoardSize"
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
  playerColor: gamePlayerColor,
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

const gameBoardSize = ref(15)

const {
  isTraining,
  status: trainingStatus,
  progress: trainingProgress,
  startTraining,
  stopTraining
} = useTraining()

const trainingDevice = ref('cpu')
const trainingBoardSize = ref(9)
const gamesPerIteration = ref(100)
const mctsSimulations = ref(200)
const trainingEpochs = ref(10)

const showVictory = ref(false)
const policyMap = ref([])

const statusMessage = computed(() => {
  if (!gameId.value) {
    return '点击"开始对弈"开始游戏'
  }
  if (gameOver.value) {
    if (winner.value === 0) return '🤝 平局！'
    if ((winner.value === 1 && gamePlayerColor.value === 'black') ||
        (winner.value === -1 && gamePlayerColor.value === 'white')) {
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
  const size = gameBoardSize.value
  const color = gamePlayerColor.value
  const modelSize = gameControls.value?.selectedModel || null

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
  padding: 20px 0;
}
</style>
