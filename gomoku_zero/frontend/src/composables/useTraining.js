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
      // 先尝试停止已在运行的训练
      try {
        await trainingAPI.stopTraining()
      } catch (stopError) {
        // 忽略停止错误
      }

      // 立即更新显示状态
      isTraining.value = true
      status.value = '训练中...'
      progress.device = device.value.toUpperCase()

      const config = {
        device: device.value,
        board_size: boardSize.value,
        games_per_iteration: gamesPerIteration.value,
        mcts_simulations: mctsSimulations.value,
        epochs: epochs.value
      }

      console.log('开始训练，参数:', config)
      const response = await trainingAPI.startTraining(config)
      const data = response.data
      console.log('训练响应:', data)

      if (data.success) {
        // 确保显示后端返回的设备信息
        if (data.device) {
          progress.device = data.device.toUpperCase()
        }
        startPolling()
      } else {
        isTraining.value = false
        status.value = data.message || '训练启动失败'
      }

      return data
    } catch (error) {
      console.error('Start training error:', error)
      isTraining.value = false
      if (error.response?.data?.detail) {
        status.value = error.response.data.detail
      } else {
        status.value = '训练启动失败'
      }
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
    stopPolling()
    pollInterval = setInterval(async () => {
      try {
        const response = await trainingAPI.getTrainingStatus()
        const data = response.data

        progress.iteration = data.iteration || 0
        progress.games = data.games_completed || 0
        progress.loss = data.loss || 0
        progress.device = (data.device || 'CPU').toUpperCase()

        if (!data.running) {
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
