<template>
  <div class="select-disciplines-view">
    <AppHeader 
      :title="searchStore.currentConcept" 
    >
      <ProgressSteps :current-step="2" />
    </AppHeader>

    <main class="main-content">
      <div class="container">
        <h2>选择相关学科领域</h2>
        <p class="subtitle">为了提供更精准的跨学科知识，请确认或调整该概念涉及的学科领域。</p>
        
        <!-- 加载状态 -->
        <div v-if="searchStore.isClassifying" class="loading-state">
          <div class="spinner"></div>
          <p>正在分析概念相关学科...</p>
        </div>

        <!-- 错误状态 -->
        <div v-else-if="searchStore.classifyError" class="error-state">
          <p>分类失败: {{ searchStore.classifyError }}</p>
          <button @click="retryClassify" class="retry-btn">重试</button>
        </div>

        <!-- 学科列表 -->
        <template v-else>
          <!-- 主学科提示 -->
          <div v-if="searchStore.primaryDiscipline" class="primary-discipline-hint">
            <span class="label">主要学科:</span>
            <span class="value">{{ searchStore.primaryDiscipline }}</span>
          </div>

          <div class="disciplines-grid">
            <div 
              v-for="discipline in searchStore.disciplines" 
              :key="getDisciplineName(discipline)"
              class="discipline-card"
              :class="{ 'is-primary': discipline.is_primary }"
            >
              <div class="discipline-info">
                <span class="name">{{ getDisciplineName(discipline) }}</span>
                <span v-if="discipline.relevance_score" class="relevance">
                  {{ Math.round(discipline.relevance_score * 100) }}%
                </span>
              </div>
              <p v-if="discipline.reason" class="reason">{{ discipline.reason }}</p>
              <button class="remove-btn" @click="searchStore.removeDiscipline(discipline)">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
              </button>
            </div>

            <div class="add-discipline-card" v-if="!isAdding">
              <button class="add-btn" @click="isAdding = true">
                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="5" x2="12" y2="19"></line><line x1="5" y1="12" x2="19" y2="12"></line></svg>
                添加学科
              </button>
            </div>
            
            <div class="add-discipline-input" v-else>
              <input 
                ref="newDisciplineInput"
                v-model="newDiscipline" 
                @keydown.enter="addNewDiscipline"
                @keydown.esc="isAdding = false" 
                placeholder="输入学科名称"
              />
              <button @click="addNewDiscipline" class="confirm-add">OK</button>
            </div>
          </div>

          <!-- 建议添加的学科 -->
          <div v-if="searchStore.suggestedAdditions && searchStore.suggestedAdditions.length > 0" class="suggested-additions">
            <h3>推荐添加</h3>
            <div class="suggestions-list">
              <button 
                v-for="suggestion in searchStore.suggestedAdditions" 
                :key="suggestion.name"
                class="suggestion-btn"
                @click="addSuggestion(suggestion)"
              >
                + {{ suggestion.name }}
                <span v-if="suggestion.reason" class="suggestion-reason">{{ suggestion.reason }}</span>
              </button>
            </div>
          </div>

          <div class="actions">
            <button class="primary-btn" @click="startQuery" :disabled="searchStore.disciplines.length === 0">
              开始查询
              <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="5" y1="12" x2="19" y2="12"></line><polyline points="12 5 19 12 12 19"></polyline></svg>
            </button>
          </div>
        </template>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue';
import { useRouter } from 'vue-router';
import { useSearchStore } from '../stores/searchStore';
import { useGraphStore } from '../stores/graphStore';
import AppHeader from '../components/AppHeader.vue';
import ProgressSteps from '../components/ProgressSteps.vue';

const router = useRouter();
const searchStore = useSearchStore();
const graphStore = useGraphStore();

const isAdding = ref(false);
const newDiscipline = ref('');
const newDisciplineInput = ref(null);

// 获取学科名称（兼容字符串和对象）
function getDisciplineName(discipline) {
  return typeof discipline === 'string' ? discipline : discipline.name;
}

onMounted(async () => {
  if (!searchStore.currentConcept) {
    router.push('/');
    return;
  }
  
  // 如果还没有学科数据，调用分类API
  if (searchStore.disciplines.length === 0) {
    await classifyConcept();
  }
});

// 调用分类API
async function classifyConcept() {
  try {
    await searchStore.classifyConcept(searchStore.currentConcept);
  } catch (error) {
    console.error('分类失败:', error);
  }
}

// 重试分类
async function retryClassify() {
  await classifyConcept();
}

function addNewDiscipline() {
  if (newDiscipline.value.trim()) {
    searchStore.addDiscipline(newDiscipline.value.trim());
    newDiscipline.value = '';
    isAdding.value = false;
  }
}

// 添加建议的学科
function addSuggestion(suggestion) {
  searchStore.addDiscipline({
    id: suggestion.name,
    name: suggestion.name,
    relevance_score: 0.8,
    reason: suggestion.reason,
    search_keywords: [],
    is_primary: false
  });
  // 从建议列表中移除
  searchStore.suggestedAdditions = searchStore.suggestedAdditions.filter(
    s => s.name !== suggestion.name
  );
}

async function startQuery() {
  try {
    // 启动搜索任务
    await searchStore.startSearch({
      depth: 'medium',
      maxResultsPerDiscipline: 10,
      enableValidation: true
    });
    
    // 跳转到工作区页面，后续会轮询搜索状态
    router.push('/workspace');
  } catch (error) {
    console.error('启动搜索失败:', error);
    alert('启动搜索失败: ' + error.message);
  }
}
</script>

<style scoped>
.select-disciplines-view {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: var(--color-background);
}

.main-content {
  flex: 1;
  display: flex;
  justify-content: center;
  padding-top: 60px;
}

.container {
  width: 100%;
  max-width: 800px;
  padding: 0 24px;
}

h2 {
  font-size: 24px;
  margin-bottom: 8px;
  color: var(--color-text-primary);
}

.subtitle {
  color: var(--color-text-secondary);
  margin-bottom: 32px;
}

.disciplines-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  margin-bottom: 48px;
}

.discipline-card {
  background: white;
  border: 1px solid var(--color-border);
  padding: 12px 24px;
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  font-size: 16px;
  color: var(--color-text-primary);
  box-shadow: var(--shadow-sm);
  transition: all 0.2s;
  position: relative;
}

.discipline-card.is-primary {
  border-color: var(--color-primary);
  background: linear-gradient(to right, rgba(59, 130, 246, 0.05), white);
}

.discipline-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

.discipline-info {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.discipline-info .name {
  font-weight: 500;
}

.discipline-info .relevance {
  font-size: 12px;
  color: var(--color-primary);
  background: rgba(59, 130, 246, 0.1);
  padding: 2px 8px;
  border-radius: 12px;
}

.discipline-card .reason {
  font-size: 12px;
  color: var(--color-text-secondary);
  margin: 0;
  line-height: 1.4;
}

.remove-btn {
  position: absolute;
  top: 8px;
  right: 8px;
  background: none;
  border: none;
  color: var(--color-text-secondary);
  cursor: pointer;
  padding: 4px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  opacity: 0.6;
}

.remove-btn:hover {
  background: var(--color-surface);
  color: #ef4444;
  opacity: 1;
}

/* 加载和错误状态 */
.loading-state,
.error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  color: var(--color-text-secondary);
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid var(--color-border);
  border-top-color: var(--color-primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 16px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.error-state {
  color: #ef4444;
}

.retry-btn {
  margin-top: 16px;
  padding: 8px 24px;
  background: var(--color-primary);
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}

/* 主学科提示 */
.primary-discipline-hint {
  margin-bottom: 20px;
  padding: 12px 16px;
  background: rgba(59, 130, 246, 0.05);
  border-radius: 8px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.primary-discipline-hint .label {
  font-size: 14px;
  color: var(--color-text-secondary);
}

.primary-discipline-hint .value {
  font-weight: 600;
  color: var(--color-primary);
}

/* 推荐添加 */
.suggested-additions {
  margin-top: 32px;
  padding-top: 24px;
  border-top: 1px dashed var(--color-border);
}

.suggested-additions h3 {
  font-size: 14px;
  color: var(--color-text-secondary);
  margin-bottom: 12px;
  font-weight: 500;
}

.suggestions-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.suggestion-btn {
  padding: 8px 16px;
  background: white;
  border: 1px dashed var(--color-border);
  border-radius: 20px;
  font-size: 14px;
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 4px;
}

.suggestion-btn:hover {
  border-color: var(--color-primary);
  color: var(--color-primary);
  background: rgba(59, 130, 246, 0.05);
}

.suggestion-reason {
  font-size: 11px;
  opacity: 0.7;
}

.add-discipline-card {
  display: flex;
  align-items: center;
}

.add-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  border: 1px dashed var(--color-border);
  border-radius: 8px;
  background: transparent;
  color: var(--color-text-secondary);
  cursor: pointer;
  font-size: 16px;
}

.add-btn:hover {
  border-color: var(--color-primary);
  color: var(--color-primary);
  background: var(--color-surface);
}

.add-discipline-input {
  display: flex;
  align-items: center;
  background: white;
  border: 1px solid var(--color-primary);
  border-radius: 8px;
  padding: 4px 12px;
}

.add-discipline-input input {
  border: none;
  outline: none;
  padding: 8px;
  font-size: 16px;
}

.confirm-add {
  background: var(--color-primary);
  color: white;
  border: none;
  padding: 6px 12px;
  border-radius: 4px;
  cursor: pointer;
}

.actions {
  display: flex;
  justify-content: flex-end;
}

.primary-btn {
  background: var(--color-text-primary); /* Using black/dark as primary per current style hint */
  color: white;
  border: none;
  padding: 14px 32px;
  border-radius: 50px;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.2s;
}

.primary-btn:hover {
  opacity: 0.9;
  transform: translateY(-1px);
}

.progress-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: var(--color-text-secondary);
}

.step.active {
  color: var(--color-text-primary);
  font-weight: 500;
}

.separator {
  color: var(--color-border);
}
</style>
