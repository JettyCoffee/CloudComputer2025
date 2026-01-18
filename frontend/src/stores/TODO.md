# Stores - Zustand状态管理

## 目录说明
本目录使用Zustand管理全局状态。

## 需要完成的内容

### 1. 搜索状态 Store
- [ ] `searchStore.ts`
  - 当前搜索概念
  - 学科分类结果
  - 搜索任务状态
  - 搜索结果

### 2. 图谱状态 Store
- [ ] `graphStore.ts`
  - 当前图谱ID
  - 节点数据
  - 边数据
  - 选中的节点/边
  - 图谱视图配置（缩放、平移等）
  - 筛选条件

### 3. 对话状态 Store
- [ ] `chatStore.ts`
  - 当前会话ID
  - 对话历史
  - 流式响应状态
  - 推荐问题

### 4. 用户设置 Store
- [ ] `settingsStore.ts`
  - 主题设置
  - 布局配置
  - API配置（可选）

## 文件结构
```
stores/
├── index.ts           # 统一导出
├── searchStore.ts     # 搜索状态
├── graphStore.ts      # 图谱状态
├── chatStore.ts       # 对话状态
└── settingsStore.ts   # 设置状态
```

## 示例实现

### graphStore.ts
```typescript
import { create } from 'zustand';

interface Node {
  id: string;
  name: string;
  type: string;
  discipline: string;
  x?: number;
  y?: number;
}

interface Edge {
  id: string;
  source: string;
  target: string;
  relation: string;
}

interface GraphState {
  graphId: string | null;
  nodes: Node[];
  edges: Edge[];
  selectedNodeId: string | null;
  filter: {
    disciplines: string[];
    nodeTypes: string[];
  };
  
  // Actions
  setGraphData: (graphId: string, nodes: Node[], edges: Edge[]) => void;
  selectNode: (nodeId: string | null) => void;
  setFilter: (filter: Partial<GraphState['filter']>) => void;
  updateNodePosition: (nodeId: string, x: number, y: number) => void;
}

export const useGraphStore = create<GraphState>((set) => ({
  graphId: null,
  nodes: [],
  edges: [],
  selectedNodeId: null,
  filter: {
    disciplines: [],
    nodeTypes: [],
  },

  setGraphData: (graphId, nodes, edges) => 
    set({ graphId, nodes, edges }),
  
  selectNode: (nodeId) => 
    set({ selectedNodeId: nodeId }),
  
  setFilter: (filter) => 
    set((state) => ({ filter: { ...state.filter, ...filter } })),
  
  updateNodePosition: (nodeId, x, y) =>
    set((state) => ({
      nodes: state.nodes.map((n) =>
        n.id === nodeId ? { ...n, x, y } : n
      ),
    })),
}));
```

### chatStore.ts
```typescript
interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  sources?: { nodeId: string; nodeName: string }[];
  timestamp: Date;
}

interface ChatState {
  sessionId: string | null;
  messages: Message[];
  isStreaming: boolean;
  streamingContent: string;
  
  // Actions
  setSession: (sessionId: string) => void;
  addMessage: (message: Message) => void;
  setStreaming: (isStreaming: boolean) => void;
  appendStreamContent: (content: string) => void;
  clearStreamContent: () => void;
}
```
