<template>
  <header class="app-header">
    <div class="left-section">
      <button v-if="showBack" class="icon-btn" @click="$emit('back')" title="返回">
        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M19 12H5"/><path d="M12 19l-7-7 7-7"/></svg>
      </button>
      <slot name="left"></slot>
    </div>
    
    <div class="center-section">
      <h2 class="concept-title">{{ title }}</h2>
    </div>
    
    <div class="right-section">
      <button v-if="showExport" class="action-btn" @click="$emit('export')">
        <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="feather feather-download"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line></svg>
        导出报告
      </button>
      <slot name="right"></slot>
    </div>
  </header>
</template>

<script setup>
defineProps({
  title: {
    type: String,
    default: ''
  },
  showBack: {
    type: Boolean,
    default: false
  },
  showExport: {
    type: Boolean,
    default: true
  }
});

defineEmits(['export', 'back']);
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
  flex-shrink: 0;
}

.left-section, .right-section {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 16px;
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
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
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

.icon-btn {
  background: transparent;
  border: none;
  cursor: pointer;
  padding: 8px;
  border-radius: 50%;
  color: var(--color-text-secondary);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.2s;
  margin-right: -8px; /* Optically adjust gap */
}

.icon-btn:hover {
  background: var(--color-surface);
  color: var(--color-text-primary);
}
</style>
