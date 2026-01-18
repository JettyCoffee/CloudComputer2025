# Graph Service - 知识图谱服务（LightRAG集成）

## 目录说明
知识图谱服务负责从文本块中提取实体关系，构建知识图谱，并提供图谱查询接口。

## 需要完成的内容

### 1. LightRAG集成
- [ ] LightRAG初始化与配置
- [ ] 自定义存储后端（Neo4j适配）
- [ ] 自定义LLM调用（Claude/GPT）
- [ ] 文本插入与索引构建

### 2. 实体关系提取
- [ ] 实体提取Prompt设计
- [ ] 关系抽取Prompt设计
- [ ] 实体类型定义（Concept, Person, Discipline, Application等）
- [ ] 关系类型定义（belongs_to, derived_from, similar_to等）
- [ ] 实体消歧与规范化

### 3. 知识图谱构建
- [ ] 从文本块批量构建图谱
- [ ] 增量图谱更新
- [ ] 图谱合并策略
- [ ] 图谱版本管理

### 4. 图谱精简算法
- [ ] 基于距离的节点过滤
- [ ] 基于相关性的节点过滤
- [ ] 桥接节点识别与保留
- [ ] 可配置的精简参数

### 5. Neo4j数据层
- [ ] Neo4j连接管理
- [ ] 节点CRUD操作
- [ ] 边CRUD操作
- [ ] Cypher查询封装
- [ ] 图数据导出（JSON格式）

### 6. 向量索引
- [ ] 节点embedding生成
- [ ] 向量相似度搜索
- [ ] 混合检索支持

## 文件结构
```
graph-service/
├── main.py                  # 服务入口
├── lightrag/
│   ├── config.py            # LightRAG配置
│   ├── adapter.py           # 自定义适配器
│   └── processor.py         # 文本处理器
├── extraction/
│   ├── entity_extractor.py  # 实体提取
│   ├── relation_extractor.py # 关系提取
│   └── normalizer.py        # 实体规范化
├── graph/
│   ├── builder.py           # 图谱构建器
│   ├── pruner.py            # 图谱精简器
│   └── merger.py            # 图谱合并器
├── neo4j/
│   ├── connection.py        # 连接管理
│   ├── repository.py        # 数据访问层
│   └── queries.py           # Cypher查询
├── prompts/
│   ├── entity_extraction.py
│   └── relation_extraction.py
├── models/
│   ├── node.py              # 节点模型
│   ├── edge.py              # 边模型
│   └── graph.py             # 图模型
├── config.py
├── Dockerfile
└── requirements.txt
```

## Neo4j数据模型

### 节点类型
```cypher
// 概念节点
(:Concept {
    id: string,
    name: string,
    description: string,
    discipline: string,
    embedding: list<float>
})

// 学科节点
(:Discipline {
    id: string,
    name: string
})

// 人物节点
(:Person {
    id: string,
    name: string,
    contribution: string
})
```

### 关系类型
- `BELONGS_TO` - 属于某学科
- `DERIVED_FROM` - 派生自
- `SIMILAR_TO` - 相似于
- `APPLIED_IN` - 应用于
- `PROPOSED_BY` - 由某人提出
- `INFLUENCES` - 影响

## 关键算法

### 图谱精简算法伪代码
```python
def prune_graph(graph, core_concept, config):
    # 1. BFS计算距离
    distances = bfs_from_core(graph, core_concept)
    
    # 2. 过滤远距离节点
    candidates = filter_by_distance(graph, distances, config.max_distance)
    
    # 3. 计算语义相关性
    relevance_scores = compute_relevance(candidates, core_concept)
    
    # 4. 识别桥接节点
    bridge_nodes = find_bridge_nodes(graph, candidates)
    
    # 5. 综合过滤
    final_nodes = filter_by_relevance(candidates, relevance_scores, 
                                       config.min_relevance, bridge_nodes)
    
    return build_subgraph(graph, final_nodes)
```
