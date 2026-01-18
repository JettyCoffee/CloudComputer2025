# API - API调用模块

## 目录说明
本目录封装所有后端API调用逻辑。

## 需要完成的内容

### 1. 基础配置
- [ ] `client.ts` - Axios实例配置
  - 基础URL配置
  - 请求拦截器（添加认证头等）
  - 响应拦截器（错误处理）
  - 超时配置

### 2. 搜索API
- [ ] `search.ts`
  - `classifyConcept(concept)` - 概念分类
  - `startSearch(concept, disciplines)` - 开始搜索
  - `getTaskStatus(taskId)` - 获取任务状态
  - `getSearchResults(taskId)` - 获取搜索结果

### 3. 图谱API
- [ ] `graph.ts`
  - `buildGraph(taskId, concept, config)` - 构建图谱
  - `getGraph(graphId)` - 获取图谱数据
  - `getNodeDetail(graphId, nodeId)` - 获取节点详情
  - `getNeighbors(graphId, nodeId)` - 获取邻居节点
  - `updateNode(graphId, nodeId, data)` - 更新节点
  - `deleteNode(graphId, nodeId)` - 删除节点

### 4. 对话API
- [ ] `chat.ts`
  - `createSession(graphId, concept)` - 创建会话
  - `sendMessage(sessionId, message)` - 发送消息
  - `getHistory(sessionId)` - 获取对话历史
  - `deleteSession(sessionId)` - 删除会话

### 5. 文件上传API
- [ ] `upload.ts`
  - `uploadFile(file, concept)` - 上传文件

### 6. WebSocket
- [ ] `websocket.ts`
  - WebSocket连接管理类
  - 消息发送/接收
  - 重连逻辑

## 文件结构
```
api/
├── index.ts           # 统一导出
├── client.ts          # Axios客户端
├── search.ts          # 搜索API
├── graph.ts           # 图谱API
├── chat.ts            # 对话API
├── upload.ts          # 上传API
├── websocket.ts       # WebSocket
└── types.ts           # API类型定义
```

## 示例实现

### client.ts
```typescript
import axios from 'axios';

export const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 响应拦截器
apiClient.interceptors.response.use(
  (response) => response.data,
  (error) => {
    // 统一错误处理
    const message = error.response?.data?.message || '请求失败';
    console.error('API Error:', message);
    return Promise.reject(error);
  }
);
```

### search.ts
```typescript
import { apiClient } from './client';

export interface ClassifyResponse {
  concept: string;
  primary_discipline: string;
  disciplines: Array<{
    name: string;
    relevance_score: number;
    reason: string;
    search_keywords: string[];
  }>;
}

export const searchApi = {
  classifyConcept: (concept: string) =>
    apiClient.post<ClassifyResponse>('/search/classify', { concept }),

  startSearch: (concept: string, disciplines: string[]) =>
    apiClient.post('/search/start', { concept, disciplines }),

  getTaskStatus: (taskId: string) =>
    apiClient.get(`/search/status/${taskId}`),

  getSearchResults: (taskId: string) =>
    apiClient.get(`/search/results/${taskId}`),
};
```
