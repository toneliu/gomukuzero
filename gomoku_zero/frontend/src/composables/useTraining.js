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

  const updateProgressFromResponse = (data) => {
    progress.iteration = data.iteration || 0
    progress.games = data.games_completed || 0
    progress.loss = data.loss || 0
    progress.device = (data.device || 'CPU').toUpperCase()
  }

  const checkTrainingStatus = async () => {
    try {
      console.log('检查训练状态...')
      const response = await trainingAPI.getTrainingStatus()
      const data = response.data
      console.log('训练状态响应:', data)

      updateProgressFromResponse(data)

      if (data.running) {
        isTraining.value = true
        status.value = '训练中...'
        console.log('检测到训练进行中，设备:', progress.device, '迭代:', progress.iteration, '游戏数:', progress.games)
        startPolling()
      } else {
        status.value = '空闲'
      }
    } catch (error) {
      console.error('检查训练状态失败:', error)
      status.value = '检查状态失败'
    }
  }

  const startTraining = async () => {
    try {
      console.log('准备开始训练...')

      try {
        await trainingAPI.stopTraining()
        await new Promise(resolve => setTimeout(resolve, 500))
      } catch (stopError) {
        console.log('停止旧训练（忽略错误）:', stopError)
      }

      isTraining.value = true
      status.value = '训练中...'
      progress.device = device.value.toUpperCase()
      progress.iteration = 0
      progress.games = 0
      progress.loss = 0

      const config = {
        device: device.value,
        board_size: boardSize.value,
        games_per_iteration: gamesPerIteration.value,
        mcts_simulations: mctsSimulations.value,
        epochs: epochs.value
      }

      console.log('发送训练请求，参数:', config)
      const response = await trainingAPI.startTraining(config)
      const data = response.data
      console.log('训练响应:', data)

      if (data.success) {
        if (data.device) {
          progress.device = data.device.toUpperCase()
        }
        console.log('训练启动成功，开始轮询')
        startPolling()
      } else {
        console.error('训练启动失败:', data.message)
        isTraining.value = false
        status.value = data.message || '训练启动失败'
      }

      return data
    } catch (error) {
      console.error('Start training error:', error)
      isTraining.value = false
      if (error.response?.data?.detail) {
        status.value = error.response.data.detail
      } else if (error.message) {
        status.value = error.message
      } else {
        status.value = '训练启动失败'
      }
      return { success: false, error: error.message }
    }
  }

  const stopTraining = async () => {
    try {
      console.log('停止训练...')
      await trainingAPI.stopTraining()
      isTraining.value = false
      status.value = '已停止'
      stopPolling()
      console.log('训练已停止')
    } catch (error) {
      console.error('Stop training error:', error)
      isTraining.value = false
      status.value = '停止训练失败'
    }
  }

  const startPolling = () => {
    stopPolling()
    console.log('开始轮询训练状态，间隔2秒')
    pollInterval = setInterval(async () => {
      try {
        const response = await trainingAPI.getTrainingStatus()
        const data = response.data
        console.log('轮询响应 - 迭代:', data.iteration, '游戏数:', data.games_completed, '运行中:', data.running)

        updateProgressFromResponse(data)

        if (!data.running && isTraining.value) {
          console.log('检测到训练结束')
          isTraining.value = false
          status.value = '训练完成'
          stopPolling()
        } else if (data.running && !isTraining.value) {
          console.log('检测到训练从文件恢复')
          isTraining.value = true
          status.value = '训练中...'
        }
      } catch (error) {
        console.error('轮询失败:', error)
      }
    }, 2000)
  }

  const stopPolling = () => {
    if (pollInterval) {
      clearInterval(pollInterval)
      pollInterval = null
      console.log('轮询已停止')
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
    stopTraining,
    checkTrainingStatus
  }
}
