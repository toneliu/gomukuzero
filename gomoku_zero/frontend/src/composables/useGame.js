import { ref, reactive } from 'vue'
import { gameAPI } from '../api/game'

export function useGame() {
  const gameId = ref(null)
  const board = ref([])
  const boardSize = ref(15)
  const playerColor = ref('black')
  const isMyTurn = ref(false)
  const gameOver = ref(false)
  const lastMove = ref(null)
  const winner = ref(null)
  const isLoading = ref(false)

  const startGame = async (size, color, modelSize = null) => {
    try {
      isLoading.value = true
      const response = await gameAPI.startGame(size, color, modelSize)
      const data = response.data

      gameId.value = data.game_id
      boardSize.value = size
      playerColor.value = color
      gameOver.value = false
      isMyTurn.value = (color === 'black')
      winner.value = null
      lastMove.value = null

      board.value = Array(size).fill().map(() => Array(size).fill(0))
      return { success: true, data }
    } catch (error) {
      console.error('Start game error:', error)
      return { success: false, error: error.message }
    } finally {
      isLoading.value = false
    }
  }

  const makeMove = async (row, col) => {
    if (!gameId.value || !isMyTurn.value || gameOver.value) {
      return { success: false, reason: 'Not your turn' }
    }

    if (board.value[row][col] !== 0) {
      return { success: false, reason: 'Position occupied' }
    }

    try {
      const response = await gameAPI.makeMove(gameId.value, [row, col])
      const data = response.data

      if (data.valid) {
        board.value[row][col] = 1

        if (data.ai_position) {
          board.value[data.ai_position[0]][data.ai_position[1]] = -1
          lastMove.value = data.ai_position
        }

        if (data.game_over) {
          gameOver.value = true
          winner.value = data.winner
        }

        isMyTurn.value = !isMyTurn.value
      }

      return { success: data.valid, data }
    } catch (error) {
      console.error('Make move error:', error)
      return { success: false, error: error.message }
    }
  }

  const updateBoard = async () => {
    if (!gameId.value) return

    try {
      const response = await gameAPI.getGameState(gameId.value)
      const data = response.data

      board.value = data.board
      isMyTurn.value = (data.current_player === playerColor.value)
      lastMove.value = data.last_move

      return data
    } catch (error) {
      console.error('Get game state error:', error)
    }
  }

  const endGame = async () => {
    if (!gameId.value) return

    try {
      await gameAPI.endGame(gameId.value)
    } catch (error) {
      console.error('End game error:', error)
    }

    gameId.value = null
    board.value = []
    gameOver.value = false
    winner.value = null
  }

  return {
    gameId,
    board,
    boardSize,
    playerColor,
    isMyTurn,
    gameOver,
    lastMove,
    winner,
    isLoading,
    startGame,
    makeMove,
    updateBoard,
    endGame
  }
}
