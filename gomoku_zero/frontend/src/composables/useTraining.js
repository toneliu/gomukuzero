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
        progress.games = data.games_completed || 0
        progress.loss = data.loss || 0
        progress.device = data.device?.toUpperCase() || 'CPU'

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
