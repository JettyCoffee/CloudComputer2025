# Hooks - 自定义React Hooks

## 目录说明
本目录包含所有自定义React Hooks，封装可复用的状态逻辑。

## 需要完成的内容

### 1. 数据获取Hooks
- [ ] `useSearchQuery.ts` - 概念搜索Hook
- [ ] `useGraphData.ts` - 图谱数据获取Hook
- [ ] `useChatSession.ts` - 对话会话管理Hook
- [ ] `useTaskStatus.ts` - 任务状态轮询Hook

### 2. WebSocket Hooks
- [ ] `useWebSocket.ts` - WebSocket连接管理
- [ ] `useChatStream.ts` - 流式对话Hook

### 3. UI交互Hooks
- [ ] `useGraph.ts` - 图谱交互状态Hook
- [ ] `useNodeSelection.ts` - 节点选择Hook
- [ ] `useZoom.ts` - 缩放控制Hook
- [ ] `useDragNode.ts` - 节点拖拽Hook

### 4. 通用Hooks
- [ ] `useDebounce.ts` - 防抖Hook
- [ ] `useThrottle.ts` - 节流Hook
- [ ] `useLocalStorage.ts` - 本地存储Hook
- [ ] `useMediaQuery.ts` - 响应式查询Hook

## 示例实现

### useSearchQuery
```typescript
import { useMutation, useQuery } from '@tanstack/react-query';
import { searchApi } from '@/api/search';

export function useSearchQuery() {
  const classifyMutation = useMutation({
    mutationFn: searchApi.classifyConcept,
  });

  const startSearchMutation = useMutation({
    mutationFn: searchApi.startSearch,
  });

  const { data: taskStatus } = useQuery({
    queryKey: ['searchTask', taskId],
    queryFn: () => searchApi.getTaskStatus(taskId),
    enabled: !!taskId,
    refetchInterval: (data) => 
      data?.status === 'completed' ? false : 2000,
  });

  return {
    classifyMutation,
    startSearchMutation,
    taskStatus,
  };
}
```

### useWebSocket
```typescript
export function useWebSocket(url: string) {
  const [isConnected, setIsConnected] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const socketRef = useRef<WebSocket | null>(null);

  const connect = useCallback(() => {
    // WebSocket连接逻辑
  }, [url]);

  const send = useCallback((data: any) => {
    socketRef.current?.send(JSON.stringify(data));
  }, []);

  const disconnect = useCallback(() => {
    socketRef.current?.close();
  }, []);

  return { isConnected, messages, connect, send, disconnect };
}
```
