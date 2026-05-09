import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 30000
})

export const gameAPI = {
  startGame(boardSize, playerColor, modelSize = null) {
    return api.post('/game/start', {
      board_size: boardSize,
      player_color: playerColor,
      model_size: modelSize
    })
  },

  makeMove(gameId, position) {
    return api.post('/game/move', {
      game_id: gameId,
      position
    })
  },

  getGameState(gameId) {
    return api.get(`/game/state/${gameId}`)
  },

  endGame(gameId) {
    return api.delete(`/game/${gameId}`)
  }
}
