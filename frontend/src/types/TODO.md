# Types - TypeScript类型定义

## 目录说明
本目录包含全局TypeScript类型定义。

## 需要完成的内容

### 1. 图谱相关类型
- [ ] `graph.ts`
  - `Node` - 节点类型
  - `Edge` - 边类型
  - `GraphData` - 图谱数据
  - `NodeType` - 节点类型枚举
  - `RelationType` - 关系类型枚举

### 2. 搜索相关类型
- [ ] `search.ts`
  - `SearchTask` - 搜索任务
  - `SearchResult` - 搜索结果
  - `Discipline` - 学科信息
  - `TextChunk` - 文本块

### 3. 对话相关类型
- [ ] `chat.ts`
  - `Message` - 消息类型
  - `Session` - 会话类型
  - `ChatSource` - 引用来源

### 4. API响应类型
- [ ] `api.ts`
  - `ApiResponse<T>` - 通用响应
  - `PaginatedResponse<T>` - 分页响应
  - `ErrorResponse` - 错误响应

## 文件结构
```
types/
├── index.ts           # 统一导出
├── graph.ts           # 图谱类型
├── search.ts          # 搜索类型
├── chat.ts            # 对话类型
└── api.ts             # API类型
```

## 类型定义示例

### graph.ts
```typescript
export type NodeType = 'concept' | 'person' | 'discipline' | 'application' | 'theory';

export type RelationType = 
  | 'belongs_to' 
  | 'derived_from' 
  | 'similar_to' 
  | 'applied_in' 
  | 'proposed_by' 
  | 'influences';

export interface Node {
  id: string;
  name: string;
  type: NodeType;
  discipline: string;
  description?: string;
  properties?: Record<string, any>;
  // 可视化属性
  x?: number;
  y?: number;
  color?: string;
}

export interface Edge {
  id: string;
  source: string;
  target: string;
  relation: RelationType;
  weight?: number;
  description?: string;
}

export interface GraphData {
  nodes: Node[];
  edges: Edge[];
  metadata: {
    totalNodes: number;
    totalEdges: number;
    disciplines: string[];
    createdAt: string;
  };
}
```

### search.ts
```typescript
export interface Discipline {
  name: string;
  relevanceScore: number;
  reason: string;
  searchKeywords: string[];
}

export interface TextChunk {
  id: string;
  content: string;
  discipline: string;
  sourceUrl: string;
  relevanceScore: number;
  academicValue?: number;
}

export interface SearchTask {
  id: string;
  concept: string;
  disciplines: string[];
  status: 'pending' | 'processing' | 'completed' | 'failed';
  progress: number;
  createdAt: string;
}
```

### chat.ts
```typescript
export interface ChatSource {
  nodeId: string;
  nodeName: string;
  relevance: number;
}

export interface Message {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  sources?: ChatSource[];
  relatedNodes?: string[];
  timestamp: Date;
}

export interface Session {
  id: string;
  graphId: string;
  concept: string;
  createdAt: string;
  lastMessageAt: string;
}
```
