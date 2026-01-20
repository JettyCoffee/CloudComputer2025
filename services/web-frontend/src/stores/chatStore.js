import { defineStore } from 'pinia'
import { api } from '../api'

export const useChatStore = defineStore('chat', {
  state: () => ({
    messages: [],
    isStreaming: false
  }),
  
  actions: {
    async sendMessage(text) {
      // User message
      this.messages.push({
        id: Date.now(),
        role: 'user',
        content: text
      });
      
      this.isStreaming = true;
      const botMsgId = Date.now() + 1;
      
      // Placeholder for bot message
      this.messages.push({
        id: botMsgId,
        role: 'assistant',
        content: ''
      });
      
      const botMsgIndex = this.messages.findIndex(m => m.id === botMsgId);
      
      try {
        const stream = api.streamAnswer(text);
        for await (const chunk of stream) {
          this.messages[botMsgIndex].content += chunk;
        }
      } catch (e) {
        this.messages[botMsgIndex].content += "\n[出错: 无法连接到知识引擎]";
      } finally {
        this.isStreaming = false;
      }
    }
  }
})
