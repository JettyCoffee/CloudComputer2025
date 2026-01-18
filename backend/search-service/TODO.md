# Search Service - 检索服务（LangGraph Agent）

## 目录说明
检索服务是核心Agent模块，使用LangGraph构建多Agent工作流，负责概念的跨学科检索。

## 需要完成的内容

### 1. LangGraph工作流
- [ ] 定义State状态模型 (`state.py`)
- [ ] 学科分类Agent节点
- [ ] 并行搜索编排节点
- [ ] 结果聚合节点
- [ ] 校验层节点
- [ ] 工作流图构建与编译

### 2. Agent实现
- [ ] **学科分类Agent**
  - 调用LLM分析概念涉及的学科
  - 输出学科列表、置信度、搜索关键词
  - Prompt模板设计与优化

- [ ] **并行搜索Agent**
  - 集成Tavily API
  - 异步并行搜索多个学科
  - 搜索结果解析与格式化
  - 错误处理与重试机制

- [ ] **校验Agent (Check Layer)**
  - 事实核查
  - 内容去重（基于embedding相似度）
  - 相关性评分
  - 质量过滤

### 3. Prompt工程
- [ ] `prompts/discipline_classification.py` - 学科分类Prompt
- [ ] `prompts/search_query_generation.py` - 搜索查询生成Prompt
- [ ] `prompts/validation.py` - 校验Prompt
- [ ] Prompt版本管理与A/B测试支持

### 4. 外部服务集成
- [ ] LLM客户端封装（支持Claude/GPT切换）
- [ ] Tavily API客户端
- [ ] 结果缓存（Redis）

### 5. 任务管理
- [ ] 异步任务队列（Celery/Redis Queue）
- [ ] 任务状态跟踪
- [ ] 进度回报机制

## 文件结构
```
search-service/
├── main.py                  # 服务入口
├── graph/
│   ├── state.py             # LangGraph状态定义
│   ├── nodes/
│   │   ├── classify.py      # 学科分类节点
│   │   ├── search.py        # 并行搜索节点
│   │   ├── aggregate.py     # 结果聚合节点
│   │   └── validate.py      # 校验节点
│   └── workflow.py          # 工作流构建
├── agents/
│   ├── classifier.py        # 分类Agent
│   ├── searcher.py          # 搜索Agent
│   └── validator.py         # 校验Agent
├── prompts/
│   ├── discipline_classification.py
│   ├── search_query_generation.py
│   └── validation.py
├── clients/
│   ├── llm_client.py        # LLM客户端
│   └── tavily_client.py     # Tavily客户端
├── models/
│   ├── search_task.py
│   └── search_result.py
├── config.py
├── Dockerfile
└── requirements.txt
```

## 关键设计点

### LangGraph State定义
```python
class SearchState(TypedDict):
    concept: str                      # 输入概念
    disciplines: List[Dict]           # 学科列表
    user_confirmed: bool              # 用户确认标志
    search_results: Dict[str, List]   # 按学科分组的搜索结果
    validated_chunks: List[Dict]      # 校验后的文本块
    errors: List[str]                 # 错误信息
```

### 工作流节点
1. `classify_concept` - 概念分类
2. `wait_user_confirm` - 等待用户确认（Human-in-Loop）
3. `parallel_search` - 并行搜索
4. `aggregate_results` - 结果聚合
5. `validate_results` - 结果校验
