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
