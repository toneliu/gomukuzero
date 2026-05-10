<template>
  <div class="training-panel">
    <div class="training-controls">
      <div class="control-group">
        <label for="train-device">训练设备:</label>
        <select id="train-device" v-model="device" :disabled="isTraining">
          <option value="cpu">CPU (通用)</option>
          <option value="cuda" :disabled="!cudaAvailable">GPU (需要CUDA) 
            <span v-if="!cudaAvailable">(不可用)</span>
          </option>
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
import { ref, onMounted } from 'vue'
import { trainingAPI } from '../api/training'

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

const cudaAvailable = ref(false)

const loadDeviceInfo = async () => {
  try {
    const response = await trainingAPI.getDevices()
    cudaAvailable.value = response.data.cuda_available
    if (!cudaAvailable.value && device.value === 'cuda') {
      device.value = 'cpu'
    }
  } catch (error) {
    console.error('Load device info error:', error)
  }
}

onMounted(() => {
  loadDeviceInfo()
})
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
