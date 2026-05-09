import axios from 'axios'

const api = axios.create({
  baseURL: '/api/data',
  timeout: 10000
})

export const dataAPI = {
  getModels() {
    return api.get('/models')
  },

  getHistory() {
    return api.get('/history')
  },

  getGameDetails(gameId) {
    return api.get(`/history/${gameId}`)
  },

  getTrainingData() {
    return api.get('/training')
  },

  getBoardSizes() {
    return api.get('/config/sizes')
  },

  getTrainingConfig() {
    return api.get('/config/training')
  }
}
