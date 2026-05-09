import axios from 'axios'

const api = axios.create({
  baseURL: '/api/training',
  timeout: 60000
})

export const trainingAPI = {
  startTraining(config) {
    return api.post('/start', config)
  },

  stopTraining() {
    return api.post('/stop')
  },

  getTrainingStatus() {
    return api.get('/status')
  },

  getDevices() {
    return api.get('/devices')
  }
}
