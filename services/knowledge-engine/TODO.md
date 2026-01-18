# Knowledge Engine 知识引擎（模块B）

## 职责
对应 PLAN 中的**模块二：知识图谱构建**，使用 LightRAG 从文本中提取实体关系，构建知识图谱，并同步到 Neo4j。

## 需要完成的文件

### 1. main.py - FastAPI入口
- [ ] `POST /api/ingest` - 接收文本块，构建知识图谱
- [ ] `GET /api/graph/{concept}` - 获取图谱数据（节点+边）
- [ ] `POST /api/query` - RAG查询接口（对话用）
- [ ] `POST /api/query/stream` - 流式RAG查询（WebSocket）
- [ ] `GET /api/graph/{concept}/prune` - 获取精简后的图谱
- [ ] 健康检查接口

### 2. rag_core.py - LightRAG核心逻辑
- [ ] LightRAG 初始化配置
- [ ] 文本插入（insert）
- [ ] 查询方法封装（naive/local/global/hybrid）
- [ ] 自定义LLM和Embedding配置

### 3. neo4j_syncer.py - 【关键】Neo4j同步
- [ ] 从LightRAG提取实体和关系
- [ ] 转换为Neo4j Cypher语句
- [ ] 批量写入Neo4j
- [ ] 增量更新逻辑

### 4. graph_pruner.py - 图谱精简
- [ ] 基于距离的节点过滤
- [ ] 基于相关性的节点过滤
- [ ] 保留桥接节点

### 5. models.py - 数据模型
- [ ] GraphNode, GraphEdge 模型
- [ ] 请求/响应模型

### 6. Dockerfile & requirements.txt

## LightRAG 集成要点

```python
from lightrag import LightRAG, QueryParam

# 初始化
rag = LightRAG(
    working_dir="./lightrag_cache",
    llm_model_func=openai_complete,  # 自定义LLM
    embedding_func=openai_embedding   # 自定义Embedding
)

# 插入文本
await rag.ainsert(text_chunks)

# 查询
result = await rag.aquery(
    query="熵在不同学科的应用",
    param=QueryParam(mode="hybrid")  # naive/local/global/hybrid
)
```

## Neo4j 同步流程
```
LightRAG内部图谱 → 提取节点/边 → 转换Cypher → 写入Neo4j
                                              ↓
                            前端从Neo4j读取 → D3.js可视化
```

## Neo4j 数据模型
```cypher
// 节点
(:Entity {id, name, type, description, embedding})

// 关系
(:Entity)-[:RELATES_TO {weight, description}]->(:Entity)
```
