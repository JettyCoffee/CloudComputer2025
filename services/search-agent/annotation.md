**先配置 `.env`** ：

```.env
# ============ API Keys ============
# OpenAI API (用于LLM调用)
OPENAI_API_KEY=XXX
OPENAI_BASE_URL=https://open.bigmodel.cn/api/paas/v4
OPENAI_MODEL=GLM-4.5

# Tavily API (用于网络搜索)
TAVILY_API_KEY=XXX

SEARCH_PROVIDER=tavily
WIKIPEDIA_LANG=zh
# ============ Neo4j 配置 ============
NEO4J_USER=neo4j
NEO4J_PASSWORD=your-neo4j-password
```



## 前端

## 1. 取“概念涉及哪些领域 + 默认勾选”

`POST /api/search/plan`

**请求 JSON**

```
{
  "concept": "熵",
  "max_disciplines": 8,
  "min_relevance": 0.3,
  "default_selected": 3
}
```

**响应 JSON**（data）

```
{
  "concept": "熵",
  "primary_discipline": "信息论",
  "defaults": ["d1", "d2", "d3"],
  "disciplines": [
    {
      "id": "d1",
      "name": "信息论",
      "relevance_score": 0.92,
      "reason": "关联理由",
      "search_keywords": ["信息熵", "香农 熵", "编码 定理"],
      "is_primary": true,
      "is_default_selected": true
    }
  ],
  "suggested_additions": [
    { "name": "统计力学", "reason": "..." }
  ]
}
```

## 2. 用“用户选中的学科 + 关键词”发起搜索任务

`POST /api/search/start`

**请求 JSON**

```
{
  "concept": "熵",
  "disciplines": [
    { "name": "信息论", "search_keywords": ["信息熵", "香农 熵"] },
    { "name": "热力学", "search_keywords": ["热力学 熵", "熵增原理"] }
  ],
  "search_config": {
    "depth": "medium",
    "max_results_per_discipline": 5,
    "enable_validation": false
  }
}
```

## 3. 轮询任务状态

`GET /api/search/status/{task_id}`

- 建议前端每 `0.5~1s` 轮询一次
- 直到 `status` 变为 `completed / failed / cancelled`

**响应 JSON（data）示例**

```
{
  "task_id": "task-xxxx",
  "status": "processing",
  "progress": {
    "overall": 55,
    "current_stage": "aggregation",
    "stages": {
      "classification": "completed",
      "search": "in_progress",
      "aggregation": "in_progress",
      "validation": "pending"
    }
  },
  "partial_results": {
    "total_chunks_found": 0,
    "validated_chunks": 0,
    "by_discipline": {}
  },
  "started_at": "2026-01-20T13:00:00.000000",
  "updated_at": "2026-01-20T13:00:01.000000"
}
```

状态说明：
- `pending`：任务已创建未开始
- `processing`：任务执行中
- `completed`：任务执行完成（可拉 results）
- `failed`：任务失败（可在后端日志查原因）
- `cancelled`：任务被取消

## 4. 获取最终结果（支持分页/过滤）

`GET /api/search/results/{task_id}?page=1&page_size=20&discipline=信息论&min_relevance=0.6`

Query 参数：
- `page`：默认 `1`
- `page_size`：默认 `20`（建议不超过 `100`）
- `discipline`：可选，只返回该学科的 chunks
- `min_relevance`：可选，过滤 `relevance_score` 小于该阈值的 chunks

**响应 JSON（data）示例**

```
{
  "task_id": "task-xxxx",
  "concept": "熵",
  "summary": {
    "total_chunks": 11,
    "disciplines_covered": 2,
    "average_relevance": 0.65
  },
  "chunks": [
    {
      "id": "chunk-xxxx",
      "content": "正文片段...",
      "discipline": "信息论",
      "source": {
        "url": "https://...",
        "title": "页面标题",
        "published_date": null
      },
      "relevance_score": 0.65,
      "academic_value": 0.55,
      "validation": {
        "is_validated": false,
        "confidence": 0.65,
        "notes": null
      },
      "extracted_entities": []
    }
  ],
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total": 11,
    "total_pages": 1
  }
}
```

**特殊情况：无结果**
如果检索不到内容，仍会返回 `total_chunks = 1`，其中 `chunks[0]` 是提示信息（source.url 为 `about:blank`），用于提示检查：
- `SEARCH_PROVIDER`
- 网络/代理是否可访问
- 相关 API KEY 是否配置

## 5. 取消任务（可选）

`DELETE /api/search/tasks/{task_id}`

**响应 JSON（data）示例**

```
{
  "task_id": "task-xxxx",
  "status": "cancelled"
}
```

---



## 后端（knowledge-engine）对接：入库接口（可选）

> Search-Agent 支持把 chunks 自动推送给 knowledge-engine（取决于后端是否开启 auto_ingest 以及知识引擎是否实现该接口）。

`POST {KNOWLEDGE_ENGINE_URL}/api/ingest`

**请求 JSON**

```
{
  "concept": "熵",
  "chunks": [
    {
      "id": "chunk-xxxx",
      "content": "文本...",
      "discipline": "信息论",
      "source": { "url": "https://...", "title": "xxx", "published_date": null },
      "relevance_score": 0.65,
      "academic_value": 0.55,
      "validation": { "is_validated": false, "confidence": 0.65, "notes": null },
      "extracted_entities": []
    }
  ]
}
```

**注意**
- ingest 失败不会影响 search-agent 的 results 返回（后端会忽略入库错误）
- 默认 knowledge-engine 地址通过环境变量 `KNOWLEDGE_ENGINE_URL` 配置（compose 内常见：`http://knowledge-engine:8002`）
