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
