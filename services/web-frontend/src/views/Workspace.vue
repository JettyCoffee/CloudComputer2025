<template>
  <div class="workspace-view">
    <header class="header">
      <div class="left-section">
        <button class="icon-btn" @click="goBack" title="返回首页">
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M19 12H5"/><path d="M12 19l-7-7 7-7"/></svg>
        </button>
        <div class="concept-title">
          <span class="label">当前探索:</span>
          <h2 class="value">{{ searchStore.currentConcept || '未选择' }}</h2>
        </div>
      </div>
      
      <div class="right-section">
        <button class="action-btn">
          <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="feather feather-download"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line></svg>
          导出报告
        </button>
      </div>
    </header>

    <main class="main-content">
      <div class="panel graph-panel">
        <GraphView />
      </div>
      <div class="panel chat-panel-container">
        <ChatPanel />
      </div>
    </main>
  </div>
</template>

<script setup>
import { onMounted } from 'vue';
import { useRouter } from 'vue-router';
import GraphView from '../components/GraphView.vue';
import ChatPanel from '../components/ChatPanel.vue';
import { useSearchStore } from '../stores/searchStore';
import { useGraphStore } from '../stores/graphStore';
import { useChatStore } from '../stores/chatStore';

const router = useRouter();
const searchStore = useSearchStore();
const graphStore = useGraphStore();
const chatStore = useChatStore();

function goBack() {
  router.push('/');
}

// Initial check
onMounted(() => {
  if (!searchStore.currentConcept) {
    // If refreshed on workspace, default or redirect
    // let's just set a default for demo
    searchStore.setConcept("熵");
    graphStore.fetchGraph("熵");
  }
});
</script>

<style scoped>
.workspace-view {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: var(--color-background);
}

.header {
  height: 64px;
  border-bottom: 1px solid var(--color-border);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  background: white;
  z-index: 10;
}

.left-section {
  display: flex;
  align-items: center;
  gap: 16px;
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
}

.icon-btn:hover {
  background: var(--color-surface);
  color: var(--color-text-primary);
}

.concept-title {
  display: flex;
  align-items: baseline;
  gap: 8px;
}

.concept-title .label {
  font-size: 12px;
  color: var(--color-text-secondary);
  text-transform: uppercase;
  font-weight: 600;
}

.concept-title .value {
  font-size: 20px;
  font-weight: 500;
  color: var(--color-text-primary);
  margin: 0;
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: white;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-full);
  font-size: 14px;
  font-weight: 500;
  color: var(--color-text-primary);
  cursor: pointer;
  transition: all 0.2s;
}

.action-btn:hover {
  background: var(--color-surface);
  border-color: var(--color-text-secondary);
}

.main-content {
  flex: 1;
  display: flex;
  overflow: hidden;
  padding: 16px;
  gap: 16px;
  background: var(--color-surface-hover);
}

.panel {
  height: 100%;
  border-radius: var(--radius-lg);
  overflow: hidden;
  background: white;
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--color-border);
}

.graph-panel {
  flex: 3; /* 60% approx with gap */
  position: relative;
}

.chat-panel-container {
  flex: 2; /* 40% approx */
  display: flex;
  flex-direction: column;
}
</style>
