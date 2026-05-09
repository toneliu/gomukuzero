<template>
  <div v-if="show" class="victory-modal" @click.self="close">
    <div :class="['victory-content', resultClass]">
      <h2>{{ title }}</h2>
      <p>{{ message }}</p>
      <button class="btn btn-primary" @click="close">确定</button>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  show: {
    type: Boolean,
    default: false
  },
  winner: {
    type: Number,
    default: null
  },
  playerColor: {
    type: String,
    default: 'black'
  }
})

const emit = defineEmits(['close'])

const resultClass = computed(() => {
  if (props.winner === 0) return 'draw'
  if ((props.winner === 1 && props.playerColor === 'black') ||
      (props.winner === -1 && props.playerColor === 'white')) {
    return 'win'
  }
  return 'lose'
})

const title = computed(() => {
  if (props.winner === 0) return '🤝 平局！'
  if ((props.winner === 1 && props.playerColor === 'black') ||
      (props.winner === -1 && props.playerColor === 'white')) {
    return '🎉 恭喜获胜！'
  }
  return '🤖 AI获胜'
})

const message = computed(() => {
  if (props.winner === 0) return '双方实力相当，这是一场精彩的对局！'
  if ((props.winner === 1 && props.playerColor === 'black') ||
      (props.winner === -1 && props.playerColor === 'white')) {
    return '你击败了AI！太厉害了！'
  }
  return 'AI战胜了你，再接再厉！'
})

const close = () => {
  emit('close')
}
</script>

<style scoped>
.victory-modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  animation: fadeIn 0.3s ease;
}

.victory-content {
  background: white;
  padding: 40px;
  border-radius: 16px;
  text-align: center;
  max-width: 400px;
  width: 90%;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
  animation: slideIn 0.3s ease;
}

.victory-content h2 {
  font-size: 2.5rem;
  margin-bottom: 20px;
  color: #333;
}

.victory-content p {
  font-size: 1.3rem;
  color: #666;
  margin-bottom: 30px;
}

.victory-content.win h2 {
  color: #4CAF50;
}

.victory-content.lose h2 {
  color: #f44336;
}

.victory-content.draw h2 {
  color: #FF9800;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(-50px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
