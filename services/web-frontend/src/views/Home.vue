<template>
  <div class="home-view">
    <AppHeader 
      title="Cross Learning" 
    />
    <div class="content">
      <SearchPanel @search="handleSearch" />
    </div>
    
    <footer class="footer">
      <p>Powered by Cross-Disciplinary Knowledge Agent</p>
    </footer>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router';
import SearchPanel from '../components/SearchPanel.vue';
import AppHeader from '../components/AppHeader.vue';
import { useSearchStore } from '../stores/searchStore';
import { useGraphStore } from '../stores/graphStore';

const router = useRouter();
const searchStore = useSearchStore();
const graphStore = useGraphStore();

async function handleSearch(concept) {
  searchStore.setConcept(concept);
  // Clear previous data
  searchStore.setDisciplines([]);
  router.push('/select-disciplines');
}
</script>

<style scoped>
.home-view {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: radial-gradient(circle at 50% 30%, #fff, #f8f9fa);
}

.content {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  width: 100%;
  padding: 0 20px;
  transform: translateY(-5vh);
}

.footer {
  position: absolute;
  bottom: 24px;
  color: var(--color-text-secondary);
  font-size: 12px;
  opacity: 0.6;
}
</style>
