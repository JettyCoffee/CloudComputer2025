import { defineStore } from 'pinia'
import { api } from '../api'

export const useSearchStore = defineStore('search', {
  state: () => ({
    currentConcept: '',
    disciplines: [],
    isSearching: false
  }),
  
  actions: {
    async setConcept(concept) {
      this.currentConcept = concept;
    },
    setDisciplines(list) {
      this.disciplines = list;
    },
    addDiscipline(item) {
      if (!this.disciplines.includes(item)) {
        this.disciplines.push(item);
      }
    },
    removeDiscipline(item) {
      this.disciplines = this.disciplines.filter(i => i !== item);
    }
  }
})
