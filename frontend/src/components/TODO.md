# Components - React组件

## 目录说明
本目录包含所有React组件，按功能模块组织。

## 需要完成的内容

### 1. 通用组件 (common/)
- [ ] `Header.tsx` - 页面头部导航
- [ ] `Loading.tsx` - 加载状态组件
- [ ] `ErrorBoundary.tsx` - 错误边界
- [ ] `Tooltip.tsx` - 工具提示
- [ ] `Modal.tsx` - 模态框
- [ ] `Button.tsx` - 按钮变体

### 2. 图谱可视化组件 (GraphVisualization/)
- [ ] `ForceGraph.tsx` - D3力导向图主组件
- [ ] `GraphControls.tsx` - 图谱控制面板（缩放、布局、筛选）
- [ ] `NodeDetail.tsx` - 节点详情弹窗
- [ ] `EdgeDetail.tsx` - 边详情弹窗
- [ ] `Legend.tsx` - 图例说明
- [ ] `MiniMap.tsx` - 小地图导航（可选）
- [ ] `SearchInGraph.tsx` - 图内搜索

### 3. 对话面板组件 (ChatPanel/)
- [ ] `ChatHistory.tsx` - 对话历史列表
- [ ] `ChatInput.tsx` - 消息输入框
- [ ] `MessageBubble.tsx` - 消息气泡
- [ ] `SourceReference.tsx` - 来源引用展示
- [ ] `SuggestedQuestions.tsx` - 推荐问题
- [ ] `StreamingText.tsx` - 流式文本显示

### 4. 搜索面板组件 (SearchPanel/)
- [ ] `ConceptInput.tsx` - 概念输入框
- [ ] `DisciplineSelector.tsx` - 学科选择器
- [ ] `SearchProgress.tsx` - 搜索进度展示
- [ ] `ResultPreview.tsx` - 搜索结果预览
- [ ] `FileUploader.tsx` - 文件上传组件

### 5. 布局组件 (Layout/)
- [ ] `MainLayout.tsx` - 主布局
- [ ] `SplitPane.tsx` - 分栏布局
- [ ] `ResizablePanel.tsx` - 可调整大小的面板

## 组件开发规范

### 文件结构
每个组件文件夹包含：
```
ComponentName/
├── index.tsx          # 主组件
├── ComponentName.tsx  # 组件实现
├── types.ts          # 类型定义
├── hooks.ts          # 自定义Hooks（可选）
└── styles.css        # 额外样式（可选）
```

### TypeScript类型
所有组件都需要定义完整的Props类型：
```typescript
interface GraphNodeProps {
  node: NodeData;
  isSelected: boolean;
  onSelect: (id: string) => void;
}
```

### 样式规范
优先使用Tailwind CSS类名，避免内联样式：
```tsx
<div className="flex items-center gap-4 p-4 bg-white rounded-lg shadow">
```
