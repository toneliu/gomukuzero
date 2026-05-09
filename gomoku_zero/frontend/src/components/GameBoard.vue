<template>
  <div class="board-container">
    <canvas
      ref="canvas"
      @click="handleClick"
      @touchstart.prevent="handleTouchStart"
      @touchend.prevent="handleTouchEnd"
    ></canvas>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, onUnmounted, nextTick } from 'vue'
import { useBoard } from '../composables/useBoard'

const props = defineProps({
  board: {
    type: Array,
    required: true
  },
  boardSize: {
    type: Number,
    default: 15
  },
  lastMove: {
    type: Array,
    default: null
  },
  policyMap: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['click-cell'])

const canvas = ref(null)
const { resize, drawBoard, getCellFromPoint } = useBoard()

let resizeObserver = null
let lastTapTime = 0

const handleClick = (event) => {
  if (!canvas.value) return
  const cell = getCellFromPoint(event.clientX, event.clientY, props.boardSize, canvas.value)
  if (cell) {
    emit('click-cell', cell[0], cell[1])
  }
}

const handleTouchStart = (event) => {
  if (event.touches.length > 0) {
    event.preventDefault()
  }
}

const handleTouchEnd = (event) => {
  if (!canvas.value) return

  const now = Date.now()
  if (now - lastTapTime < 300) return
  lastTapTime = now

  if (event.changedTouches && event.changedTouches.length > 0) {
    const touch = event.changedTouches[0]
    const cell = getCellFromPoint(touch.clientX, touch.clientY, props.boardSize, canvas.value)
    if (cell) {
      emit('click-cell', cell[0], cell[1])
    }
  }
}

const redraw = () => {
  if (!canvas.value) return
  resize(canvas.value, props.boardSize)
  drawBoard(
    canvas.value,
    props.boardSize,
    props.board,
    props.lastMove,
    props.policyMap
  )
}

watch(
  () => props.board,
  () => redraw(),
  { deep: true }
)

watch(
  () => props.boardSize,
  () => {
    nextTick(() => redraw())
  }
)

watch(
  () => props.lastMove,
  () => redraw()
)

watch(
  () => props.policyMap,
  () => redraw(),
  { deep: true }
)

onMounted(() => {
  if (canvas.value) {
    nextTick(() => redraw())

    resizeObserver = new ResizeObserver(() => {
      redraw()
    })
    resizeObserver.observe(canvas.value.parentElement)
  }
})

onUnmounted(() => {
  if (resizeObserver) {
    resizeObserver.disconnect()
  }
})
</script>

<style scoped>
.board-container {
  position: relative;
  width: 100%;
  max-width: 700px;
  min-height: 350px;
  display: flex;
  justify-content: center;
  align-items: center;
}

canvas {
  background: #DEB887;
  border: 4px solid #8B4513;
  border-radius: 4px;
  cursor: pointer;
  touch-action: none;
  -webkit-touch-callout: none;
  -webkit-tap-highlight-color: transparent;
  user-select: none;
  -webkit-user-select: none;
}

@media (max-width: 768px) {
  .board-container {
    min-height: 300px;
  }
}
</style>
