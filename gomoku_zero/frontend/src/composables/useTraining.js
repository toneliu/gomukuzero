import { ref, reactive } from 'vue'
import axios from 'axios'

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
  let eventSource = null

  const updateProgressFromResponse = (data) => {
    progress.iteration = data.iteration || 0
    progress.games = data.games_completed || 0
    progress.loss = data.loss || 0
    progress.device = (data.device || 'CPU').toUpperCase()
  }

  const connectSSE = () => {
    if (eventSource) {
      eventSource.close()
    }

    console.log('连接SSE实时更新...')
    eventSource = new EventSource('/api/training/stream')

    eventSource.onopen = () => {
      console.log('SSE连接已建立')
    }

    eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        console.log('收到SSE消息:', data.type, data)

        switch (data.type) {
          case 'training_started':
            isTraining.value = true
            status.value = '训练中...'
            progress.device = (data.device || 'CPU').toUpperCase()
            progress.iteration = 0
            progress.games = 0
            progress.loss = 0
            break

          case 'iteration_complete':
            isTraining.value = true
            status.value = '训练中...'
            updateProgressFromResponse(data)
            break

          case 'training_stopped':
            isTraining.value = false
            status.value = '训练完成'
            updateProgressFromResponse(data)
            disconnectSSE()
            break

          case 'heartbeat':
            console.log('SSE心跳')
            break

          default:
            console.log('未知SSE消息类型:', data.type)
        }
      } catch (error) {
        console.error('解析SSE消息失败:', error)
      }
    }

    eventSource.onerror = (error) => {
      console.error('SSE连接错误:', error)
      disconnectSSE()
      setTimeout(() => {
        if (isTraining.value) {
          console.log('尝试重新连接SSE...')
          connectSSE()
        }
      }, 3000)
    }
  }

  const disconnectSSE = () => {
    if (eventSource) {
      console.log('断开SSE连接')
      eventSource.close()
      eventSource = null
    }
  }

  const checkTrainingStatus = async () => {
    try {
      console.log('检查训练状态...')
      const response = await axios.get('/api/training/status')
      const data = response.data
      console.log('训练状态响应:', data)

      updateProgressFromResponse(data)

      if (data.running) {
        isTraining.value = true
        status.value = '训练中...'
        console.log('检测到训练进行中，连接SSE实时更新')
        connectSSE()
      } else {
        status.value = '空闲'
        disconnectSSE()
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
        await axios.post('/api/training/stop')
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
      const response = await axios.post('/api/training/start', config)
      const data = response.data
      console.log('训练响应:', data)

      if (data.success) {
        if (data.device) {
          progress.device = data.device.toUpperCase()
        }
        console.log('训练启动成功，连接SSE实时更新')
        connectSSE()
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
      await axios.post('/api/training/stop')
      isTraining.value = false
      status.value = '已停止'
      disconnectSSE()
      console.log('训练已停止')
    } catch (error) {
      console.error('Stop training error:', error)
      isTraining.value = false
      status.value = '停止训练失败'
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
    checkTrainingStatus,
    disconnectSSE
  }
}
