<template>
  <div class="workspace-view">
    <AppHeader 
      :title="searchStore.currentConcept || '未选择'" 
    >
      <ProgressSteps :current-step="3" />
    </AppHeader>

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
import AppHeader from '../components/AppHeader.vue';
import ProgressSteps from '../components/ProgressSteps.vue';
import { useSearchStore } from '../stores/searchStore';
import { useGraphStore } from '../stores/graphStore';
import { useChatStore } from '../stores/chatStore';

const router = useRouter();
const searchStore = useSearchStore();
const graphStore = useGraphStore();
const chatStore = useChatStore();

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

/* AppHeader is used instead of internal header structure now */

.progress-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: var(--color-text-secondary);
  margin-left: 16px;
}

.step.active {
  color: var(--color-text-primary);
  font-weight: 500;
}

.step.completed {
  opacity: 0.7;
}

.separator {
  color: var(--color-border);
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
