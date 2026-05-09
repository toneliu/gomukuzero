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

const boardSize = defineModel('boardSize', { type: Number, default: 15 })
const playerColor = defineModel('playerColor', { type: String, default: 'black' })

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
