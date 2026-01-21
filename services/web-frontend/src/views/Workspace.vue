<template>
  <div class="workspace-view">
    <AppHeader 
      :title="searchStore.currentConcept || '未选择'" 
    >
      <ProgressSteps :current-step="3" />
    </AppHeader>

    <!-- 搜索进度遮罩 -->
    <div v-if="searchStore.isSearchInProgress" class="search-progress-overlay">
      <div class="progress-card">
        <h3>正在搜索知识...</h3>
        <div class="progress-bar">
          <div class="progress-fill" :style="{ width: searchStore.searchProgress.overall + '%' }"></div>
        </div>
        <p class="progress-info">
          {{ getStageLabel(searchStore.searchProgress.currentStage) }}
          <span class="progress-percent">{{ searchStore.searchProgress.overall }}%</span>
        </p>
        <div class="partial-results" v-if="searchStore.partialResults.totalChunksFound > 0">
          <span>已找到 {{ searchStore.partialResults.totalChunksFound }} 条知识片段</span>
        </div>
      </div>
    </div>

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
import { onMounted, watch, onUnmounted, ref } from 'vue';
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

let pollInterval = null;

// 阶段标签映射
function getStageLabel(stage) {
  const labels = {
    'pending': '准备中...',
    'classification': '正在分类概念...',
    'search': '正在搜索各学科知识...',
    'aggregation': '正在聚合结果...',
    'validation': '正在验证知识片段...',
    'completed': '搜索完成！'
  };
  return labels[stage] || stage;
}

// 轮询搜索状态
async function pollStatus() {
  if (!searchStore.currentTaskId) return;
  
  try {
    await searchStore.pollSearchStatus();
    
    if (searchStore.searchStatus === 'completed') {
      // 搜索完成，停止轮询
      stopPolling();
      
      // 等待知识引擎处理完成后获取图谱
      setTimeout(async () => {
        await graphStore.fetchGraph(searchStore.currentConcept);
      }, 3000);
    } else if (searchStore.searchStatus === 'failed' || searchStore.searchStatus === 'cancelled') {
      stopPolling();
    }
  } catch (error) {
    console.error('轮询状态失败:', error);
  }
}

function startPolling() {
  if (pollInterval) return;
  pollInterval = setInterval(pollStatus, 2000);
}

function stopPolling() {
  if (pollInterval) {
    clearInterval(pollInterval);
    pollInterval = null;
  }
}

// 监听搜索完成，自动获取图谱
watch(() => searchStore.searchStatus, async (newStatus) => {
  if (newStatus === 'completed' && searchStore.currentConcept) {
    // 搜索完成后，等待一下让知识引擎构建图谱
    setTimeout(async () => {
      await graphStore.fetchGraph(searchStore.currentConcept);
      // 图谱加载成功后初始化聊天连接
      if (graphStore.nodes.length > 0 && !graphStore.error) {
        chatStore.setConcept(searchStore.currentConcept);
        console.log(`图谱加载成功，已连接聊天服务: ${searchStore.currentConcept}`);
      }
    }, 2000);
  }
});

// 监听图谱加载成功，初始化聊天连接
watch(() => graphStore.nodes, (newNodes) => {
  if (newNodes.length > 0 && !graphStore.error && graphStore.concept) {
    chatStore.setConcept(graphStore.concept);
  }
}, { deep: true });

// Initial check
onMounted(async () => {
  if (searchStore.currentConcept) {
    // 设置chatStore的概念上下文
    chatStore.setConcept(searchStore.currentConcept);
    
    // 如果有正在进行的搜索任务，开始轮询
    if (searchStore.isSearchInProgress) {
      startPolling();
    } else {
      // 尝试获取已有图谱
      await graphStore.fetchGraph(searchStore.currentConcept);
      // 图谱加载成功后确保聊天连接已建立
      if (graphStore.nodes.length > 0 && !graphStore.error) {
        chatStore.setConcept(searchStore.currentConcept);
      }
    }
  } else {
    // 没有概念时重定向到首页
    router.push('/');
  }
});

onUnmounted(() => {
  stopPolling();
});
</script>

<style scoped>
.workspace-view {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: var(--color-background);
}

/* 搜索进度遮罩 */
.search-progress-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  backdrop-filter: blur(4px);
}

.progress-card {
  background: white;
  border-radius: var(--radius-lg);
  padding: 32px 48px;
  box-shadow: var(--shadow-lg);
  text-align: center;
  min-width: 400px;
}

.progress-card h3 {
  margin: 0 0 24px 0;
  font-size: 18px;
  color: var(--color-text-primary);
}

.progress-bar {
  height: 8px;
  background: var(--color-surface);
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 16px;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--color-primary), #34A853);
  border-radius: 4px;
  transition: width 0.3s ease;
}

.progress-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 14px;
  color: var(--color-text-secondary);
}

.progress-percent {
  font-weight: 600;
  color: var(--color-primary);
}

.partial-results {
  margin-top: 12px;
  font-size: 13px;
  color: var(--color-text-tertiary);
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
