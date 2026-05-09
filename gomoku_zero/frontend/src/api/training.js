import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 60000
})

export const trainingAPI = {
  startTraining(config) {
    return api.post('/training/start', config)
  },

  stopTraining() {
    return api.post('/training/stop')
  },

  getTrainingStatus() {
    return api.get('/training/status')
  }
}
