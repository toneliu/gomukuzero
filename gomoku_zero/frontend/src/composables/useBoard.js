import { ref } from 'vue'

export function useBoard() {
  const canvasRef = ref(null)
  const boardSize = ref(15)
  const cellSize = ref(0)
  const board = ref([])
  const lastMove = ref(null)
  const policyMap = ref([])

  const COLORS = {
    board: '#DEB887',
    grid: '#8B4513',
    blackStone: '#000000',
    whiteStone: '#FFFFFF',
    lastMoveMarker: '#FF5722'
  }

  const resize = (canvas, size) => {
    if (!canvas) return

    const container = canvas.parentElement
    const containerWidth = container.clientWidth || window.innerWidth
    const containerHeight = container.clientHeight || window.innerHeight

    const availableWidth = Math.min(containerWidth - 40, 700)
    const availableHeight = Math.min(containerHeight - 40, availableWidth)
    const maxSize = Math.min(availableWidth, availableHeight)

    canvas.width = maxSize
    canvas.height = maxSize
    canvas.style.width = maxSize + 'px'
    canvas.style.height = maxSize + 'px'

    cellSize.value = maxSize / (size + 1)
  }

  const drawBoard = (canvas, size, boardData, lastMoveData, policyData) => {
    if (!canvas) return

    const ctx = canvas.getContext('2d')
    const cs = canvas.width / (size + 1)

    ctx.fillStyle = COLORS.board
    ctx.fillRect(0, 0, canvas.width, canvas.height)

    ctx.strokeStyle = COLORS.grid
    ctx.lineWidth = 1

    for (let i = 0; i < size; i++) {
      ctx.beginPath()
      ctx.moveTo(cs / 2, cs / 2 + i * cs)
      ctx.lineTo(canvas.width - cs / 2, cs / 2 + i * cs)
      ctx.stroke()

      ctx.beginPath()
      ctx.moveTo(cs / 2 + i * cs, cs / 2)
      ctx.lineTo(cs / 2 + i * cs, canvas.height - cs / 2)
      ctx.stroke()
    }

    if (boardData && boardData.length > 0) {
      for (let r = 0; r < size; r++) {
        for (let c = 0; c < size; c++) {
          if (boardData[r][c] !== 0) {
            drawStone(ctx, cs, r, c, boardData[r][c])
          }
        }
      }
    }

    if (lastMoveData) {
      drawLastMoveMarker(ctx, cs, lastMoveData[0], lastMoveData[1])
    }

    if (policyData && policyData.length === size * size) {
      drawPolicyMap(ctx, cs, size, policyData)
    }
  }

  const drawStone = (ctx, cs, row, col, player) => {
    const x = cs / 2 + col * cs
    const y = cs / 2 + row * cs
    const radius = cs * 0.4

    ctx.beginPath()
    ctx.arc(x, y, radius, 0, Math.PI * 2)
    ctx.fillStyle = player === 1 ? COLORS.blackStone : COLORS.whiteStone
    ctx.fill()

    ctx.strokeStyle = player === 1 ? '#333' : '#ddd'
    ctx.lineWidth = 2
    ctx.stroke()

    if (player === -1) {
      ctx.beginPath()
      ctx.arc(x, y, radius, 0, Math.PI * 2)
      ctx.strokeStyle = '#000'
      ctx.lineWidth = 1
      ctx.stroke()
    }
  }

  const drawLastMoveMarker = (ctx, cs, row, col) => {
    const x = cs / 2 + col * cs
    const y = cs / 2 + row * cs
    const radius = cs * 0.15

    ctx.beginPath()
    ctx.arc(x, y, radius, 0, Math.PI * 2)
    ctx.fillStyle = COLORS.lastMoveMarker
    ctx.fill()
  }

  const drawPolicyMap = (ctx, cs, size, policy) => {
    ctx.globalAlpha = 0.3

    for (let i = 0; i < size * size; i++) {
      const prob = policy[i]
      if (prob > 0.01) {
        const row = Math.floor(i / size)
        const col = i % size
        const x = cs / 2 + col * cs
        const y = cs / 2 + row * cs
        const radius = cs * 0.35 * Math.sqrt(prob)

        ctx.beginPath()
        ctx.arc(x, y, radius, 0, Math.PI * 2)
        ctx.fillStyle = 'rgba(76, 175, 80, 0.8)'
        ctx.fill()
      }
    }

    ctx.globalAlpha = 1.0
  }

  const getCellFromEvent = (event, size) => {
    const rect = event.target.getBoundingClientRect()
    let clientX, clientY

    if (event.touches && event.touches.length > 0) {
      clientX = event.touches[0].clientX
      clientY = event.touches[0].clientY
    } else if (event.changedTouches && event.changedTouches.length > 0) {
      clientX = event.changedTouches[0].clientX
      clientY = event.changedTouches[0].clientY
    } else {
      clientX = event.clientX
      clientY = event.clientY
    }

    const x = clientX - rect.left
    const y = clientY - rect.top
    const cs = event.target.width / (size + 1)

    const col = Math.round((x - cs / 2) / cs)
    const row = Math.round((y - cs / 2) / cs)

    if (row >= 0 && row < size && col >= 0 && col < size) {
      return [row, col]
    }

    return null
  }

  const getCellFromPoint = (canvas, x, y, size) => {
    const rect = canvas.getBoundingClientRect()
    const offsetX = x - rect.left
    const offsetY = y - rect.top
    const cs = canvas.width / (size + 1)

    const col = Math.round((offsetX - cs / 2) / cs)
    const row = Math.round((offsetY - cs / 2) / cs)

    if (row >= 0 && row < size && col >= 0 && col < size) {
      return [row, col]
    }

    return null
  }

  const clearBoard = () => {
    board.value = []
    lastMove.value = null
    policyMap.value = []
  }

  return {
    canvasRef,
    boardSize,
    cellSize,
    board,
    lastMove,
    policyMap,
    resize,
    drawBoard,
    getCellFromEvent,
    getCellFromPoint,
    clearBoard
  }
}
