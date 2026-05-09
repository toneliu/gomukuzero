<template>
  <nav class="tab-nav">
    <button
      v-for="tab in tabs"
      :key="tab.id"
      :class="['tab-btn', { active: currentTab === tab.id }]"
      @click="$emit('change-tab', tab.id)"
    >
      {{ tab.icon }} {{ tab.label }}
    </button>
  </nav>
</template>

<script setup>
import { defineProps, defineEmits } from 'vue'

defineProps({
  currentTab: {
    type: String,
    required: true
  }
})

defineEmits(['change-tab'])

const tabs = [
  { id: 'game', label: '对弈', icon: '🎮' },
  { id: 'training', label: '训练', icon: '⚙️' },
  { id: 'data', label: '数据', icon: '📊' }
]
</script>

<style scoped>
.tab-nav {
  display: flex;
  gap: 10px;
  margin-bottom: 30px;
}

.tab-btn {
  flex: 1;
  padding: 15px 20px;
  border: 2px solid #ddd;
  background: white;
  border-radius: 8px;
  font-size: 1.1rem;
  cursor: pointer;
  transition: all 0.3s;
}

.tab-btn:hover {
  background: #f5f5f5;
}

.tab-btn.active {
  background: #2196F3;
  color: white;
  border-color: #2196F3;
}
</style>
