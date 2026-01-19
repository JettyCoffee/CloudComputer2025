<template>
  <div class="search-container" :class="{ 'compact': isCompact }">
    <h1 v-if="!isCompact" class="title">探索跨学科知识</h1>
    
    <div class="search-box">
      <div class="icon-wrapper">
        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="search-icon"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>
      </div>
      <input 
        type="text" 
        v-model="query" 
        @keydown.enter="handleSearch"
        placeholder="输入核心概念，例如：熵、涌现、网络理论..."
        class="search-input"
        autofocus
      />
      <button v-if="query" @click="query = ''" class="clear-btn">
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
      </button>
    </div>

    <div v-if="!isCompact" class="suggestions">
      <button @click="quickSearch('熵')" class="suggestion-pill">熵</button>
      <button @click="quickSearch('控制论')" class="suggestion-pill">控制论</button>
      <button @click="quickSearch('博弈论')" class="suggestion-pill">博弈论</button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';

const props = defineProps({
  isCompact: Boolean
});

const emit = defineEmits(['search']);
const query = ref('');

function handleSearch() {
  if (query.value.trim()) {
    emit('search', query.value.trim());
  }
}

function quickSearch(term) {
  query.value = term;
  handleSearch();
}
</script>

<style scoped>
.search-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100%;
  max-width: 680px;
  margin: 0 auto;
  transition: all 0.3s ease;
}

.title {
  font-size: 3rem;
  font-weight: 500;
  color: var(--color-text-primary);
  margin-bottom: 2rem;
  letter-spacing: -1px;
}

.search-box {
  width: 100%;
  height: 56px;
  background: white;
  border: 1px solid var(--color-border);
  border-radius: 28px;
  display: flex;
  align-items: center;
  padding: 0 16px;
  box-shadow: var(--shadow-sm);
  transition: all 0.2s ease;
}

.search-box:hover, .search-box:focus-within {
  box-shadow: var(--shadow-md);
  border-color: transparent;
  transform: translateY(-1px);
}

.icon-wrapper {
  color: var(--color-text-secondary);
  display: flex;
  align-items: center;
  margin-right: 12px;
}

.search-input {
  flex: 1;
  border: none;
  outline: none;
  font-size: 16px;
  height: 100%;
  color: var(--color-text-primary);
}

.clear-btn {
  background: none;
  border: none;
  color: var(--color-text-secondary);
  cursor: pointer;
  padding: 4px;
  border-radius: 50%;
  display: flex;
  align-items: center;
}

.clear-btn:hover {
  background: var(--color-surface);
}

.suggestions {
  margin-top: 24px;
  display: flex;
  gap: 12px;
}

.suggestion-pill {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  padding: 8px 16px;
  border-radius: 100px;
  font-size: 14px;
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: all 0.2s;
}

.suggestion-pill:hover {
  background: white;
  border-color: var(--color-text-secondary);
  color: var(--color-text-primary);
}

/* Compact Mode (for header) */
.compact .title {
  display: none;
}

.compact .suggestions {
  display: none;
}

.compact .search-box {
  height: 44px;
  background: var(--color-surface);
  border: none;
  box-shadow: none;
}

.compact .search-box:focus-within {
  background: white;
  box-shadow: var(--shadow-sm);
}
</style>
