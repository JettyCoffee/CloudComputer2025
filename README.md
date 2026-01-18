# CloudComputer2025
## Group 5
## 项目分工
- 陈子谦：前端
- 李则言：Agent并行搜索
- 李佳亮：LightRAG知识图谱构建

## 项目结构概览

```
CloudComputer2025/
├── Technical.md              # 完整技术架构文档
├── docs/
│   ├── API.md               # 详细API接口设计文档
│   └── TODO.md              # 文档模块任务清单
├── backend/
│   ├── TODO.md              # 后端总体任务
│   ├── api-gateway/TODO.md  # API网关服务任务
│   ├── search-service/TODO.md # 检索服务(LangGraph)任务
│   ├── graph-service/TODO.md  # 图谱服务(LightRAG)任务
│   ├── chat-service/TODO.md   # RAG对话服务任务
│   └── shared/TODO.md         # 共享模块任务
├── frontend/
│   ├── TODO.md              # 前端总体任务
│   └── src/
│       ├── components/TODO.md # React组件任务
│       ├── hooks/TODO.md      # 自定义Hooks任务
│       ├── stores/TODO.md     # Zustand状态管理任务
│       ├── api/TODO.md        # API调用模块任务
│       └── types/TODO.md      # TypeScript类型任务
├── deploy/TODO.md           # 部署配置任务
├── scripts/TODO.md          # 脚本工具任务
└── tests/TODO.md            # 测试模块任务
```

## 关键文档

Technical.md - 包含：

- 系统架构图

- 三大模块技术实现方案
- LangGraph工作流设计
- LightRAG集成方案
- 核心Prompt模板
- Neo4j数据模型
- 云原生部署架构

API.md - 包含：

- 完整的RESTful API设计 (25+ 接口)
- WebSocket实时对话协议
- 请求/响应格式规范
- 错误码定义

🔌 API接口分类
模块	接口数量	主要功能
搜索API	5个	概念分类、启动搜索、状态查询、获取结果
图谱API	8个	构建图谱、获取数据、节点CRUD、导出
对话API	6个	会话管理、HTTP/WebSocket消息
文件API	2个	文件上传与状态查询
系统API	2个	健康检查、统计信息