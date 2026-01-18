# Search Agent 搜索服务（模块A）

## 职责
对应 PLAN 中的**模块一：检索**，负责接收用户查询、调用LLM进行学科分类、并行调用Tavily搜索、校验结果。

## 需要完成的文件

### 1. main.py - FastAPI入口
- [ ] `POST /api/classify` - 概念学科分类接口
- [ ] `POST /api/search` - 启动跨学科搜索
- [ ] `GET /api/search/{task_id}` - 查询搜索状态
- [ ] `GET /api/results/{task_id}` - 获取搜索结果
- [ ] 健康检查接口

### 2. agent.py - LangChain搜索逻辑
- [ ] 学科分类Agent（调用LLM分析概念涉及的学科）
- [ ] Tavily并行搜索逻辑（asyncio并发）
- [ ] 校验层Agent（Check Layer，校验搜索结果）
- [ ] 结果聚合与格式化

### 3. prompts.py - Prompt模板
- [ ] 学科分类Prompt
- [ ] 校验Prompt

### 4. models.py - 数据模型
- [ ] 请求/响应Pydantic模型

### 5. Dockerfile & requirements.txt

## 技术要点
```python
# 学科分类输出格式
{
    "concept": "熵",
    "disciplines": [
        {"name": "热力学", "relevance": 0.95, "keywords": ["热力学熵", "克劳修斯"]},
        {"name": "信息论", "relevance": 0.90, "keywords": ["信息熵", "香农"]}
    ]
}
```

## 调用流程
```
用户输入概念 → 学科分类Agent → 返回学科列表 → 用户确认
                                                    ↓
                                          并行Tavily搜索
                                                    ↓
                                            校验层过滤
                                                    ↓
                                    发送文本块到 knowledge-engine
```
