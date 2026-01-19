<template>
  <header class="app-header">
    <div class="left-section">
      <slot name="left"></slot>
    </div>
    
    <div class="center-section">
      <h2 class="concept-title">{{ title || '探索' }}</h2>
    </div>
    
    <div class="right-section">
      <button class="action-btn" @click="$emit('export')">
        <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="feather feather-download"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line></svg>
        导出报告
      </button>
    </div>
  </header>
</template>

<script setup>
defineProps({
  title: String
});

defineEmits(['export']);
</script>

<style scoped>
.app-header {
  height: 64px;
  border-bottom: 1px solid var(--color-border);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  background: white;
  z-index: 10;
  width: 100%;
}

.left-section, .right-section {
  flex: 1;
  display: flex;
  align-items: center;
}

.center-section {
  flex: 2;
  display: flex;
  justify-content: center;
}

.right-section {
  justify-content: flex-end;
}

.concept-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--color-text-primary);
  margin: 0;
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  border-radius: 6px;
  background: white;
  border: 1px solid var(--color-border);
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  color: var(--color-text-secondary);
  transition: all 0.2s;
}

.action-btn:hover {
  background: var(--color-surface);
  color: var(--color-text-primary);
}
</style>
