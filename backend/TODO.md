# Backend 后端服务

## 目录说明
本目录包含所有后端服务的代码，采用微服务架构设计。

## 需要完成的内容

### 1. 整体架构
- [ ] 设计微服务间的通信协议（gRPC/REST）
- [ ] 统一的错误处理机制
- [ ] 日志收集与监控
- [ ] 配置管理（环境变量/配置文件）

### 2. 子服务模块
- `api-gateway/` - API网关服务
- `search-service/` - 检索服务（LangGraph Agent）
- `graph-service/` - 知识图谱服务（LightRAG）
- `chat-service/` - RAG对话服务

### 3. 共享模块
- `shared/` - 共享工具类、模型定义、常量等
- `tests/` - 单元测试与集成测试

### 4. 依赖管理
- 使用 Poetry 或 pip-tools 管理Python依赖
- 统一的requirements.txt或pyproject.toml

## 技术栈
- Python 3.11+
- FastAPI
- LangGraph
- LightRAG
- SQLAlchemy / asyncpg
- Redis (缓存)
- Neo4j (图数据库)
