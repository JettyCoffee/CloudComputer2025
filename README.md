# CloudComputer2025
## Group 5
## 项目分工
- 陈子谦：前端
- 李则言：Agent并行搜索
- 李佳亮：LightRAG知识图谱构建

## 项目结构概览

```
CloudComputer2025/
├── docker-compose.yml          # 【核心】服务编排
├── .env.example                # API Keys模板
├── Technical.md                # 技术架构文档
├── PLAN.md                     # 项目计划
├── README.md
│
├── services/
│   ├── search-agent/           # 模块A：搜索服务
│   │   └── TODO.md             # 详细任务清单
│   │
│   ├── knowledge-engine/       # 模块B：LightRAG知识引擎
│   │   └── TODO.md             # 详细任务清单
│   │
│   └── web-frontend/           # 模块C：Vue3前端
│       ├── TODO.md             # 详细任务清单
│       └── src/components/
│
├── data/                       # 数据持久化
│   ├── neo4j_data/
│   └── lightrag_cache/
│
└── docs/
    └── API.md                  # API接口文档
```