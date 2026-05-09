<template>
  <div class="board-container">
    <canvas
      ref="canvas"
      @click="handleClick"
      @touchend.prevent="handleTouchEnd"
    ></canvas>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, onUnmounted } from 'vue'
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
const { resize, drawBoard, getCellFromEvent, getCellFromPoint } = useBoard()

let resizeObserver = null
let lastTouchTime = 0

const handleClick = (event) => {
  if (!canvas.value) return

  const cell = getCellFromEvent(event, props.boardSize)
  if (cell) {
    emit('click-cell', cell[0], cell[1])
  }
}

const handleTouchEnd = (event) => {
  if (!canvas.value) return

  const now = Date.now()
  if (now - lastTouchTime < 300) return
  lastTouchTime = now

  if (event.changedTouches && event.changedTouches.length > 0) {
    const touch = event.changedTouches[0]
    const cell = getCellFromPoint(touch.clientX, touch.clientY, props.boardSize)
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
  () => redraw()
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
    redraw()

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
  min-height: 500px;
  display: flex;
  justify-content: center;
  align-items: center;
}

canvas {
  background: #DEB887;
  border: 4px solid #8B4513;
  border-radius: 4px;
  cursor: pointer;
  width: 100%;
  max-width: 700px;
  min-width: 300px;
  touch-action: manipulation;
  -webkit-tap-highlight-color: transparent;
  user-select: none;
}

@media (max-width: 768px) {
  .board-container {
    min-height: 400px;
  }

  canvas {
    min-width: 95vw;
    max-width: 95vw;
  }
}
</style>
