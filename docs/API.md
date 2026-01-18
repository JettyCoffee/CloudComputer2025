# API接口设计文档

## 概述

本文档定义了跨学科知识图谱智能体系统的所有API接口规范。

### 基础信息
- **Base URL**: `http://localhost:8000/api`
- **协议**: HTTP/HTTPS
- **数据格式**: JSON
- **字符编码**: UTF-8

### 通用响应格式

```json
{
    "code": 200,
    "message": "success",
    "data": { ... },
    "timestamp": "2026-01-18T12:00:00Z"
}
```

### 错误响应格式

```json
{
    "code": 400,
    "message": "错误描述",
    "error": {
        "type": "ValidationError",
        "details": [...]
    },
    "timestamp": "2026-01-18T12:00:00Z"
}
```

### HTTP状态码

| 状态码 | 说明 |
|--------|------|
| 200 | 成功 |
| 201 | 创建成功 |
| 400 | 请求参数错误 |
| 401 | 未授权 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

---

## 一、概念搜索API

### 1.1 概念分类

分析输入概念，返回相关学科分类。

**Endpoint**: `POST /search/classify`

**请求头**:
```
Content-Type: application/json
```

**请求体**:
```json
{
    "concept": "熵",
    "max_disciplines": 5,
    "min_relevance": 0.3
}
```

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| concept | string | 是 | 核心概念词 |
| max_disciplines | integer | 否 | 最大返回学科数，默认5 |
| min_relevance | float | 否 | 最小相关性阈值，默认0.3 |

**响应体**:
```json
{
    "code": 200,
    "message": "success",
    "data": {
        "concept": "熵",
        "primary_discipline": "热力学",
        "disciplines": [
            {
                "id": "d1",
                "name": "热力学",
                "relevance_score": 1.0,
                "reason": "熵的概念起源于热力学第二定律，由克劳修斯首次提出",
                "search_keywords": ["热力学熵", "克劳修斯熵", "热力学第二定律"],
                "is_primary": true
            },
            {
                "id": "d2",
                "name": "信息论",
                "relevance_score": 0.95,
                "reason": "香农将熵的概念引入信息论，定义信息熵",
                "search_keywords": ["信息熵", "香农熵", "信息论"],
                "is_primary": false
            },
            {
                "id": "d3",
                "name": "统计力学",
                "relevance_score": 0.9,
                "reason": "玻尔兹曼从统计角度重新定义熵",
                "search_keywords": ["玻尔兹曼熵", "统计熵", "微观态"],
                "is_primary": false
            }
        ],
        "suggested_additions": [
            {
                "name": "机器学习",
                "reason": "交叉熵损失函数广泛应用于深度学习"
            }
        ]
    }
}
```

---

### 1.2 启动搜索任务

启动跨学科概念搜索任务。

**Endpoint**: `POST /search/start`

**请求体**:
```json
{
    "concept": "熵",
    "disciplines": [
        {
            "name": "热力学",
            "search_keywords": ["热力学熵", "克劳修斯熵"]
        },
        {
            "name": "信息论",
            "search_keywords": ["信息熵", "香农熵"]
        }
    ],
    "search_config": {
        "depth": "medium",
        "max_results_per_discipline": 10,
        "enable_validation": true
    }
}
```

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| concept | string | 是 | 核心概念词 |
| disciplines | array | 是 | 要搜索的学科列表 |
| search_config.depth | string | 否 | 搜索深度: shallow/medium/deep |
| search_config.max_results_per_discipline | integer | 否 | 每个学科的最大结果数 |
| search_config.enable_validation | boolean | 否 | 是否启用校验层 |

**响应体**:
```json
{
    "code": 200,
    "message": "success",
    "data": {
        "task_id": "task-uuid-12345",
        "status": "processing",
        "created_at": "2026-01-18T12:00:00Z",
        "estimated_duration_seconds": 30
    }
}
```

---

### 1.3 查询任务状态

查询搜索任务的执行状态。

**Endpoint**: `GET /search/status/{task_id}`

**路径参数**:
| 参数 | 类型 | 说明 |
|------|------|------|
| task_id | string | 任务ID |

**响应体**:
```json
{
    "code": 200,
    "message": "success",
    "data": {
        "task_id": "task-uuid-12345",
        "status": "processing",
        "progress": {
            "overall": 65,
            "current_stage": "validation",
            "stages": {
                "classification": "completed",
                "search": "completed",
                "aggregation": "completed",
                "validation": "in_progress"
            }
        },
        "partial_results": {
            "total_chunks_found": 25,
            "validated_chunks": 15,
            "by_discipline": {
                "热力学": 8,
                "信息论": 10,
                "统计力学": 7
            }
        },
        "started_at": "2026-01-18T12:00:00Z",
        "updated_at": "2026-01-18T12:00:20Z"
    }
}
```

**状态值说明**:
| status | 说明 |
|--------|------|
| pending | 等待处理 |
| processing | 处理中 |
| completed | 完成 |
| failed | 失败 |
| cancelled | 已取消 |

---

### 1.4 获取搜索结果

获取完成的搜索任务结果。

**Endpoint**: `GET /search/results/{task_id}`

**查询参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| page | integer | 否 | 页码，默认1 |
| page_size | integer | 否 | 每页数量，默认20 |
| discipline | string | 否 | 按学科筛选 |
| min_relevance | float | 否 | 最小相关性 |

**响应体**:
```json
{
    "code": 200,
    "message": "success",
    "data": {
        "task_id": "task-uuid-12345",
        "concept": "熵",
        "summary": {
            "total_chunks": 25,
            "disciplines_covered": 3,
            "average_relevance": 0.82
        },
        "chunks": [
            {
                "id": "chunk-001",
                "content": "熵（Entropy）是热力学中表示系统混乱程度的物理量。根据热力学第二定律，孤立系统的熵总是趋向于增大...",
                "discipline": "热力学",
                "source": {
                    "url": "https://example.com/thermodynamics",
                    "title": "热力学基础教程",
                    "published_date": "2024-01-15"
                },
                "relevance_score": 0.95,
                "academic_value": 0.88,
                "validation": {
                    "is_validated": true,
                    "confidence": 0.92,
                    "notes": "内容来自权威学术资源"
                },
                "extracted_entities": ["熵", "热力学第二定律", "孤立系统"]
            }
        ],
        "pagination": {
            "page": 1,
            "page_size": 20,
            "total": 25,
            "total_pages": 2
        }
    }
}
```

---

### 1.5 取消搜索任务

取消正在执行的搜索任务。

**Endpoint**: `DELETE /search/tasks/{task_id}`

**响应体**:
```json
{
    "code": 200,
    "message": "Task cancelled successfully",
    "data": {
        "task_id": "task-uuid-12345",
        "status": "cancelled"
    }
}
```

---

## 二、知识图谱API

### 2.1 构建知识图谱

从搜索结果构建知识图谱。

**Endpoint**: `POST /graph/build`

**请求体**:
```json
{
    "task_id": "task-uuid-12345",
    "concept": "熵",
    "build_config": {
        "prune_config": {
            "max_distance": 3,
            "min_relevance": 0.5,
            "preserve_bridges": true
        },
        "entity_types": ["concept", "person", "discipline", "application"],
        "relation_types": ["belongs_to", "derived_from", "similar_to", "influences"]
    }
}
```

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| task_id | string | 是 | 搜索任务ID |
| concept | string | 是 | 核心概念 |
| build_config.prune_config | object | 否 | 图谱精简配置 |
| build_config.entity_types | array | 否 | 要提取的实体类型 |
| build_config.relation_types | array | 否 | 要提取的关系类型 |

**响应体**:
```json
{
    "code": 200,
    "message": "success",
    "data": {
        "graph_id": "graph-uuid-67890",
        "status": "building",
        "created_at": "2026-01-18T12:01:00Z"
    }
}
```

---

### 2.2 获取图谱状态

查询图谱构建状态。

**Endpoint**: `GET /graph/{graph_id}/status`

**响应体**:
```json
{
    "code": 200,
    "message": "success",
    "data": {
        "graph_id": "graph-uuid-67890",
        "status": "completed",
        "progress": 100,
        "stats": {
            "total_nodes": 45,
            "total_edges": 78,
            "nodes_by_type": {
                "concept": 30,
                "person": 8,
                "discipline": 4,
                "application": 3
            },
            "disciplines": ["热力学", "信息论", "统计力学"]
        }
    }
}
```

---

### 2.3 获取图谱数据

获取完整的图谱数据用于可视化。

**Endpoint**: `GET /graph/{graph_id}`

**查询参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| include_positions | boolean | 否 | 是否包含节点位置 |
| disciplines | string | 否 | 按学科筛选，逗号分隔 |
| node_types | string | 否 | 按节点类型筛选 |

**响应体**:
```json
{
    "code": 200,
    "message": "success",
    "data": {
        "graph_id": "graph-uuid-67890",
        "concept": "熵",
        "nodes": [
            {
                "id": "n1",
                "name": "熵",
                "type": "concept",
                "discipline": "热力学",
                "description": "表示系统混乱程度的物理量",
                "properties": {
                    "symbol": "S",
                    "unit": "J/K"
                },
                "position": {
                    "x": 400,
                    "y": 300
                },
                "style": {
                    "color": "#4A90D9",
                    "size": 40
                }
            },
            {
                "id": "n2",
                "name": "香农熵",
                "type": "concept",
                "discipline": "信息论",
                "description": "信息论中的熵定义",
                "properties": {
                    "formula": "H(X) = -Σp(x)log(p(x))"
                },
                "position": {
                    "x": 550,
                    "y": 250
                },
                "style": {
                    "color": "#50C878",
                    "size": 35
                }
            }
        ],
        "edges": [
            {
                "id": "e1",
                "source": "n1",
                "target": "n2",
                "relation": "derived_from",
                "weight": 0.9,
                "description": "香农熵概念源自热力学熵",
                "style": {
                    "color": "#999",
                    "width": 2
                }
            }
        ],
        "metadata": {
            "total_nodes": 45,
            "total_edges": 78,
            "disciplines": ["热力学", "信息论", "统计力学"],
            "created_at": "2026-01-18T12:01:00Z",
            "updated_at": "2026-01-18T12:02:30Z"
        }
    }
}
```

---

### 2.4 获取节点详情

获取单个节点的详细信息。

**Endpoint**: `GET /graph/{graph_id}/nodes/{node_id}`

**响应体**:
```json
{
    "code": 200,
    "message": "success",
    "data": {
        "id": "n1",
        "name": "熵",
        "type": "concept",
        "discipline": "热力学",
        "description": "熵是热力学中表示系统混乱程度或无序程度的物理量...",
        "properties": {
            "symbol": "S",
            "unit": "J/K",
            "discovered_by": "鲁道夫·克劳修斯",
            "year": 1865
        },
        "related_chunks": [
            {
                "chunk_id": "chunk-001",
                "content_preview": "熵（Entropy）是热力学中...",
                "source_url": "https://example.com"
            }
        ],
        "neighbors": {
            "incoming": [
                {
                    "node_id": "n10",
                    "node_name": "克劳修斯",
                    "relation": "proposed_by"
                }
            ],
            "outgoing": [
                {
                    "node_id": "n2",
                    "node_name": "香农熵",
                    "relation": "derived_from"
                }
            ]
        }
    }
}
```

---

### 2.5 获取邻居节点

获取指定节点的邻居节点。

**Endpoint**: `GET /graph/{graph_id}/nodes/{node_id}/neighbors`

**查询参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| depth | integer | 否 | 搜索深度，默认1 |
| direction | string | 否 | 方向: in/out/both |
| relation_types | string | 否 | 关系类型筛选 |

**响应体**:
```json
{
    "code": 200,
    "message": "success",
    "data": {
        "center_node": "n1",
        "neighbors": [
            {
                "node": {
                    "id": "n2",
                    "name": "香农熵",
                    "type": "concept"
                },
                "relation": {
                    "type": "derived_from",
                    "direction": "outgoing",
                    "weight": 0.9
                },
                "path_length": 1
            }
        ],
        "total": 12
    }
}
```

---

### 2.6 更新节点

更新节点信息。

**Endpoint**: `PUT /graph/{graph_id}/nodes/{node_id}`

**请求体**:
```json
{
    "description": "更新后的描述",
    "properties": {
        "custom_field": "自定义值"
    },
    "position": {
        "x": 450,
        "y": 320
    }
}
```

**响应体**:
```json
{
    "code": 200,
    "message": "Node updated successfully",
    "data": {
        "id": "n1",
        "updated_fields": ["description", "properties", "position"]
    }
}
```

---

### 2.7 删除节点

删除指定节点及其相关边。

**Endpoint**: `DELETE /graph/{graph_id}/nodes/{node_id}`

**响应体**:
```json
{
    "code": 200,
    "message": "Node deleted successfully",
    "data": {
        "deleted_node": "n1",
        "deleted_edges": ["e1", "e5", "e12"]
    }
}
```

---

### 2.8 导出图谱

导出图谱数据为指定格式。

**Endpoint**: `GET /graph/{graph_id}/export`

**查询参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| format | string | 否 | 导出格式: json/csv/gexf |

**响应**: 文件下载

---

## 三、RAG对话API

### 3.1 创建对话会话

创建新的对话会话。

**Endpoint**: `POST /chat/sessions`

**请求体**:
```json
{
    "graph_id": "graph-uuid-67890",
    "concept": "熵",
    "config": {
        "query_mode": "hybrid",
        "max_context_length": 4000,
        "temperature": 0.7
    }
}
```

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| graph_id | string | 是 | 关联的图谱ID |
| concept | string | 是 | 核心概念 |
| config.query_mode | string | 否 | 查询模式: naive/local/global/hybrid |
| config.max_context_length | integer | 否 | 最大上下文长度 |
| config.temperature | float | 否 | LLM温度参数 |

**响应体**:
```json
{
    "code": 200,
    "message": "success",
    "data": {
        "session_id": "session-uuid-11111",
        "graph_id": "graph-uuid-67890",
        "concept": "熵",
        "created_at": "2026-01-18T12:05:00Z",
        "websocket_url": "ws://localhost:8000/ws/chat/session-uuid-11111"
    }
}
```

---

### 3.2 发送消息（HTTP）

通过HTTP发送对话消息（非流式）。

**Endpoint**: `POST /chat/sessions/{session_id}/messages`

**请求体**:
```json
{
    "content": "熵在机器学习中有什么应用？",
    "query_mode": "hybrid"
}
```

**响应体**:
```json
{
    "code": 200,
    "message": "success",
    "data": {
        "message_id": "msg-uuid-22222",
        "role": "assistant",
        "content": "熵在机器学习中有多种重要应用：\n\n1. **交叉熵损失函数**：在分类任务中广泛使用...\n\n2. **信息增益**：在决策树算法中用于特征选择...",
        "sources": [
            {
                "node_id": "n15",
                "node_name": "交叉熵损失",
                "relevance": 0.95,
                "snippet": "交叉熵损失函数是深度学习中最常用的损失函数之一..."
            },
            {
                "node_id": "n18",
                "node_name": "信息增益",
                "relevance": 0.88,
                "snippet": "信息增益是决策树算法中用于选择最优特征的指标..."
            }
        ],
        "related_nodes": ["n15", "n18", "n20"],
        "suggested_questions": [
            "交叉熵和KL散度有什么关系？",
            "如何理解信息增益的计算过程？"
        ],
        "created_at": "2026-01-18T12:06:00Z"
    }
}
```

---

### 3.3 WebSocket对话（流式）

通过WebSocket进行实时流式对话。

**Endpoint**: `WebSocket /ws/chat/{session_id}`

**客户端发送消息格式**:
```json
{
    "type": "message",
    "content": "解释一下熵增原理",
    "query_mode": "local"
}
```

```json
{
    "type": "ping"
}
```

**服务端响应消息格式**:

流式内容:
```json
{
    "type": "stream",
    "message_id": "msg-uuid-33333",
    "content": "熵增原理，也称为",
    "done": false
}
```

```json
{
    "type": "stream",
    "message_id": "msg-uuid-33333",
    "content": "热力学第二定律，指出",
    "done": false
}
```

完成响应:
```json
{
    "type": "complete",
    "message_id": "msg-uuid-33333",
    "content": "熵增原理，也称为热力学第二定律，指出孤立系统的熵永不自发减少...",
    "sources": [...],
    "related_nodes": [...],
    "suggested_questions": [...],
    "done": true
}
```

错误响应:
```json
{
    "type": "error",
    "code": "RETRIEVAL_ERROR",
    "message": "检索知识图谱时发生错误"
}
```

心跳响应:
```json
{
    "type": "pong",
    "timestamp": "2026-01-18T12:07:00Z"
}
```

---

### 3.4 获取对话历史

获取会话的对话历史。

**Endpoint**: `GET /chat/sessions/{session_id}/history`

**查询参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| limit | integer | 否 | 返回消息数量，默认50 |
| before | string | 否 | 获取此消息ID之前的消息 |

**响应体**:
```json
{
    "code": 200,
    "message": "success",
    "data": {
        "session_id": "session-uuid-11111",
        "messages": [
            {
                "id": "msg-uuid-22222",
                "role": "user",
                "content": "熵在机器学习中有什么应用？",
                "created_at": "2026-01-18T12:05:30Z"
            },
            {
                "id": "msg-uuid-22223",
                "role": "assistant",
                "content": "熵在机器学习中有多种重要应用...",
                "sources": [...],
                "created_at": "2026-01-18T12:06:00Z"
            }
        ],
        "has_more": false
    }
}
```

---

### 3.5 获取会话列表

获取用户的所有对话会话。

**Endpoint**: `GET /chat/sessions`

**响应体**:
```json
{
    "code": 200,
    "message": "success",
    "data": {
        "sessions": [
            {
                "id": "session-uuid-11111",
                "concept": "熵",
                "graph_id": "graph-uuid-67890",
                "message_count": 10,
                "created_at": "2026-01-18T12:05:00Z",
                "last_message_at": "2026-01-18T12:30:00Z"
            }
        ],
        "total": 1
    }
}
```

---

### 3.6 删除会话

删除指定会话及其历史记录。

**Endpoint**: `DELETE /chat/sessions/{session_id}`

**响应体**:
```json
{
    "code": 200,
    "message": "Session deleted successfully",
    "data": {
        "session_id": "session-uuid-11111",
        "deleted_messages": 10
    }
}
```

---

## 四、文件上传API

### 4.1 上传文件

上传文件作为额外知识源。

**Endpoint**: `POST /upload`

**请求头**:
```
Content-Type: multipart/form-data
```

**请求体**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| file | file | 是 | 上传的文件(PDF/TXT/MD) |
| concept | string | 否 | 关联的概念 |
| graph_id | string | 否 | 关联的图谱ID |

**响应体**:
```json
{
    "code": 200,
    "message": "success",
    "data": {
        "file_id": "file-uuid-44444",
        "filename": "research_paper.pdf",
        "size": 1024000,
        "mime_type": "application/pdf",
        "status": "processing",
        "created_at": "2026-01-18T12:10:00Z"
    }
}
```

---

### 4.2 获取文件状态

查询文件处理状态。

**Endpoint**: `GET /upload/{file_id}/status`

**响应体**:
```json
{
    "code": 200,
    "message": "success",
    "data": {
        "file_id": "file-uuid-44444",
        "status": "completed",
        "progress": 100,
        "result": {
            "extracted_chunks": 15,
            "extracted_entities": 23
        }
    }
}
```

---

## 五、系统API

### 5.1 健康检查

检查系统健康状态。

**Endpoint**: `GET /health`

**响应体**:
```json
{
    "code": 200,
    "message": "success",
    "data": {
        "status": "healthy",
        "version": "1.0.0",
        "services": {
            "api-gateway": "healthy",
            "search-service": "healthy",
            "graph-service": "healthy",
            "chat-service": "healthy",
            "neo4j": "healthy",
            "redis": "healthy"
        },
        "timestamp": "2026-01-18T12:00:00Z"
    }
}
```

---

### 5.2 系统统计

获取系统统计信息。

**Endpoint**: `GET /stats`

**响应体**:
```json
{
    "code": 200,
    "message": "success",
    "data": {
        "total_graphs": 15,
        "total_nodes": 1250,
        "total_edges": 2890,
        "total_sessions": 45,
        "total_messages": 380,
        "active_tasks": 2
    }
}
```

---

## 六、错误码定义

| 错误码 | 说明 |
|--------|------|
| 1001 | 概念不能为空 |
| 1002 | 学科列表不能为空 |
| 1003 | 搜索任务不存在 |
| 1004 | 搜索任务未完成 |
| 2001 | 图谱不存在 |
| 2002 | 节点不存在 |
| 2003 | 图谱构建失败 |
| 3001 | 会话不存在 |
| 3002 | 消息发送失败 |
| 3003 | WebSocket连接失败 |
| 4001 | 文件格式不支持 |
| 4002 | 文件大小超限 |
| 5001 | LLM服务不可用 |
| 5002 | 搜索服务不可用 |
| 5003 | 数据库连接失败 |

---

## 附录

### A. 实体类型枚举

```typescript
enum NodeType {
    CONCEPT = "concept",      // 概念
    PERSON = "person",        // 人物
    DISCIPLINE = "discipline", // 学科
    APPLICATION = "application", // 应用
    THEORY = "theory"         // 理论
}
```

### B. 关系类型枚举

```typescript
enum RelationType {
    BELONGS_TO = "belongs_to",     // 属于
    DERIVED_FROM = "derived_from", // 派生自
    SIMILAR_TO = "similar_to",     // 相似于
    APPLIED_IN = "applied_in",     // 应用于
    PROPOSED_BY = "proposed_by",   // 由...提出
    INFLUENCES = "influences"      // 影响
}
```

### C. 查询模式说明

| 模式 | 说明 | 适用场景 |
|------|------|----------|
| naive | 简单向量检索 | 精确概念查询 |
| local | 基于实体的局部检索 | 具体概念深入探索 |
| global | 基于社区的全局检索 | 宏观关系理解 |
| hybrid | 混合模式 | 通用查询（推荐） |
