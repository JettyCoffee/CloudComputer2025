import { defineStore } from 'pinia'
import { api } from '../api'

export const useGraphStore = defineStore('graph', {
  state: () => ({
    nodes: [],
    links: [],
    loading: false,
    selectedNode: null,
    disciplines: []
  }),
  
  actions: {
    async fetchGraph(concept) {
      this.loading = true;
      try {
        const data = await api.getGraph(concept);
        
        // Transform data for D3 (if needed, but usually D3 modifies objects in place)
        // We clone to avoid reactivity issues during simulation if necessary
        this.nodes = data.nodes.map(n => ({...n}));
        this.links = data.links.map(l => ({...l}));
        
        // Extract unique disciplines for coloring
        const groups = new Set(this.nodes.map(n => n.group));
        this.disciplines = Array.from(groups);
        
      } catch (error) {
        console.error("Failed to fetch graph:", error);
      } finally {
        this.loading = false;
      }
    },
    
    selectNode(node) {
      this.selectedNode = node;
    }
  }
})
