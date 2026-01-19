import { defineStore } from 'pinia'
import { api } from '../api'

export const useSearchStore = defineStore('search', {
  state: () => ({
    currentConcept: '',
    isSearching: false
  }),
  
  actions: {
    async setConcept(concept) {
      this.currentConcept = concept;
      // Triggers for other stores are usually handled in the view or here
      // But keeping it simple: just state holding
    }
  }
})
