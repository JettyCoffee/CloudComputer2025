<template>
  <div class="home-view">
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
import { useSearchStore } from '../stores/searchStore';
import { useGraphStore } from '../stores/graphStore';

const router = useRouter();
const searchStore = useSearchStore();
const graphStore = useGraphStore();

async function handleSearch(concept) {
  searchStore.setConcept(concept);
  // Pre-fetch graph data while navigating
  graphStore.fetchGraph(concept);
  router.push('/workspace');
}
</script>

<style scoped>
.home-view {
  height: 100vh;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  background: radial-gradient(circle at 50% 30%, #fff, #f8f9fa);
}

.content {
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
