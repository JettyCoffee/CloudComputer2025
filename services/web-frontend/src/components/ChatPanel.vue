<template>
  <div class="chat-panel">
    <div class="messages" ref="messagesContainer">
      <div 
        v-for="msg in chatStore.messages" 
        :key="msg.id" 
        class="message-wrapper"
        :class="{ 'user-align': msg.role === 'user' }"
      >
        <div 
          class="message-bubble"
          :class="msg.role === 'user' ? 'user-bubble' : 'bot-bubble'"
        >
          <div class="role-label" v-if="msg.role !== 'system'">
            {{ msg.role === 'user' ? '您' : '知识助手' }}
          </div>
          <div class="message-content" v-html="formatText(msg.content)"></div>
        </div>
      </div>
      
      <div v-if="chatStore.isStreaming" class="streaming-indicator">
        <span>●</span><span>●</span><span>●</span>
      </div>
    </div>

    <div class="input-area">
      <div class="input-wrapper">
        <textarea 
          v-model="input" 
          @keydown.enter.prevent="sendMessage"
          placeholder="追问关于知识图谱的细节..."
          rows="1"
          ref="textareaRef"
        ></textarea>
        <button 
          @click="sendMessage" 
          :disabled="!input.trim() || chatStore.isStreaming"
          class="send-btn"
        >
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="22" y1="2" x2="11" y2="13"></line><polygon points="22 2 15 22 11 13 2 9 22 2"></polygon></svg>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick, watch } from 'vue';
import { useChatStore } from '../stores/chatStore';

const chatStore = useChatStore();
const input = ref('');
const messagesContainer = ref(null);
const textareaRef = ref(null);

function formatText(text) {
  // Simple bold formatter for **text**
  return text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
             .replace(/\n/g, '<br>');
}

async function sendMessage() {
  const text = input.value.trim();
  if (!text) return;
  
  input.value = '';
  await chatStore.sendMessage(text);
}

// Auto scroll
watch(() => chatStore.messages, () => {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight;
    }
  });
}, { deep: true });

</script>

<style scoped>
.chat-panel {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: white;
  border-radius: var(--radius-lg);
  overflow: hidden;
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--color-border);
}

.messages {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.message-wrapper {
  display: flex;
  width: 100%;
}

.user-align {
  justify-content: flex-end;
}

.message-bubble {
  max-width: 85%;
  padding: 16px 20px;
  border-radius: 18px;
  position: relative;
  line-height: 1.6;
}

.user-bubble {
  background-color: var(--color-primary);
  color: white;
  border-bottom-right-radius: 4px;
}

.bot-bubble {
  background-color: var(--color-surface);
  color: var(--color-text-primary);
  border-bottom-left-radius: 4px;
}

.role-label {
  font-size: 11px;
  margin-bottom: 4px;
  opacity: 0.7;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.message-content :deep(strong) {
  font-weight: 700;
}

.input-area {
  padding: 20px;
  border-top: 1px solid var(--color-border);
  background: white;
}

.input-wrapper {
  display: flex;
  align-items: center;
  background: var(--color-surface);
  border-radius: var(--radius-full);
  padding: 8px 8px 8px 24px;
  border: 1px solid transparent;
  transition: all 0.2s ease;
}

.input-wrapper:focus-within {
  border-color: var(--color-border);
  background: white;
  box-shadow: var(--shadow-sm);
}

textarea {
  flex: 1;
  border: none;
  background: transparent;
  outline: none;
  resize: none;
  font-size: 15px;
  font-family: inherit;
  color: var(--color-text-primary);
  max-height: 100px;
}

.send-btn {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  border: none;
  background: var(--color-primary);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: background 0.2s;
  margin-left: 8px;
}

.send-btn:hover:not(:disabled) {
  background: var(--color-primary-hover);
}

.send-btn:disabled {
  background: var(--color-border);
  cursor: not-allowed;
}

.streaming-indicator {
  padding: 0 20px;
  color: var(--color-text-secondary);
  font-size: 12px;
  animation: pulse 1.5s infinite;
}

@keyframes pulse {
  0% { opacity: 0.4; }
  50% { opacity: 1; }
  100% { opacity: 0.4; }
}
</style>
