<template>
  <div class="select-disciplines-view">
    <AppHeader :title="searchStore.currentConcept" @export="handleExport">
      <template #left>
        <div class="progress-indicator">
          <span class="step active">1. 输入</span>
          <span class="separator">→</span>
          <span class="step active">2. 学科选择</span>
          <span class="separator">→</span>
          <span class="step">3. 探索</span>
        </div>
      </template>
    </AppHeader>

    <main class="main-content">
      <div class="container">
        <h2>选择相关学科领域</h2>
        <p class="subtitle">为了提供更精准的跨学科知识，请确认或调整该概念涉及的学科领域。</p>
        
        <div class="disciplines-grid">
          <div 
            v-for="discipline in searchStore.disciplines" 
            :key="discipline"
            class="discipline-card"
          >
            <span>{{ discipline }}</span>
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

        <div class="actions">
          <button class="primary-btn" @click="startQuery">
            开始查询
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="5" y1="12" x2="19" y2="12"></line><polyline points="12 5 19 12 12 19"></polyline></svg>
          </button>
        </div>
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

const router = useRouter();
const searchStore = useSearchStore();
const graphStore = useGraphStore();

const isAdding = ref(false);
const newDiscipline = ref('');
const newDisciplineInput = ref(null);

onMounted(async () => {
  if (!searchStore.currentConcept) {
    router.push('/');
    return;
  }
  
  // Mock API call to get initial disciplines
  // In real app, this would be an API call based on concept
  if (searchStore.disciplines.length === 0) {
    // Simulate loading
    const startList = ['物理学', '信息论', '复杂系统科学'];
    if (searchStore.currentConcept.includes('熵')) {
      searchStore.setDisciplines(startList);
    } else {
       searchStore.setDisciplines(['计算机科学', '数学', '哲学']);
    }
  }
});

function addNewDiscipline() {
  if (newDiscipline.value.trim()) {
    searchStore.addDiscipline(newDiscipline.value.trim());
    newDiscipline.value = '';
    isAdding.value = false;
  }
}

function startQuery() {
  // Trigger graph fetch
  graphStore.fetchGraph(searchStore.currentConcept);
  router.push('/workspace');
}

function handleExport() {
  alert('导出功能开发中...');
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
  align-items: center;
  gap: 12px;
  font-size: 16px;
  color: var(--color-text-primary);
  box-shadow: var(--shadow-sm);
  transition: all 0.2s;
}

.discipline-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

.remove-btn {
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
