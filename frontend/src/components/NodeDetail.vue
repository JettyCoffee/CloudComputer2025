<template>
  <div v-if="graphStore.selectedNode" class="node-detail-card">
    <div class="header">
      <h3 class="title">{{ graphStore.selectedNode.id }}</h3>
      <button class="close-btn" @click="graphStore.selectedNode = null">
        ×
      </button>
    </div>
    
    <div class="badge" :style="{ backgroundColor: color }">
      {{ graphStore.selectedNode.group }}
    </div>
    
    <div class="actions">
      <button class="action-btn primary" @click="askAbout">
        在对话中探索
      </button>
      <button class="action-btn" @click="expandNode">
        展开关联
      </button>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { useGraphStore } from '../stores/graphStore';
import { useChatStore } from '../stores/chatStore';
import * as d3 from 'd3';

const graphStore = useGraphStore();
const chatStore = useChatStore();

const color = computed(() => {
  // Re-use logic or pass color prop
  // Ideally color scale should be shared or in store
  // For now simple reliable hash or default
  return "#4285F4"; 
});

function askAbout() {
  const node = graphStore.selectedNode;
  if (node) {
    chatStore.sendMessage(`能详细介绍一下"${node.id}"在${node.group}中的应用吗？`);
  }
}

function expandNode() {
  // Placeholder for expanding graph
  alert("正在请求更多节点关联...");
}
</script>

<style scoped>
.node-detail-card {
  position: absolute;
  top: 20px;
  right: 20px;
  width: 280px;
  background: white;
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-lg);
  padding: 20px;
  border: 1px solid var(--color-border);
  backdrop-filter: blur(10px);
  z-index: 100;
  animation: slideIn 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

@keyframes slideIn {
  from { opacity: 0; transform: translateY(-10px); }
  to { opacity: 1; transform: translateY(0); }
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
}

.title {
  font-size: 18px;
  font-weight: 600;
  margin: 0;
  color: var(--color-text-primary);
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  line-height: 1;
  color: var(--color-text-secondary);
  cursor: pointer;
  padding: 0;
}

.badge {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 100px;
  color: white;
  font-size: 12px;
  font-weight: 500;
  margin-bottom: 24px;
}

.actions {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.action-btn {
  width: 100%;
  padding: 10px;
  border-radius: var(--radius-sm);
  border: 1px solid var(--color-border);
  background: white;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.action-btn:hover {
  background: var(--color-surface);
}

.action-btn.primary {
  background: var(--color-text-primary);
  color: white;
  border: none;
}

.action-btn.primary:hover {
  background: #000;
}
</style>
