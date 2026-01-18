# Chat Service - RAG对话服务

## 目录说明
对话服务提供基于知识图谱的RAG问答功能，支持实时流式响应。

## 需要完成的内容

### 1. LightRAG查询集成
- [ ] 配置LightRAG查询模式（naive/local/global/hybrid）
- [ ] 查询结果后处理
- [ ] 上下文窗口管理

### 2. 会话管理
- [ ] 会话创建与销毁
- [ ] 会话状态存储（Redis）
- [ ] 会话历史管理
- [ ] 会话超时处理

### 3. 对话处理
- [ ] 用户消息接收与解析
- [ ] 意图识别（可选）
- [ ] 知识检索
- [ ] 回答生成
- [ ] 来源引用标注

### 4. 流式响应
- [ ] WebSocket连接管理
- [ ] 流式文本生成
- [ ] 心跳检测
- [ ] 断线重连支持

### 5. 对话增强
- [ ] 多轮对话上下文理解
- [ ] 追问建议生成
- [ ] 相关节点推荐
- [ ] 对话历史总结

### 6. 缓存策略
- [ ] 查询结果缓存
- [ ] 热点问题缓存
- [ ] 缓存失效策略

## 文件结构
```
chat-service/
├── main.py                  # 服务入口
├── rag/
│   ├── query.py             # RAG查询
│   ├── retriever.py         # 检索器
│   └── generator.py         # 生成器
├── session/
│   ├── manager.py           # 会话管理器
│   ├── storage.py           # 会话存储
│   └── history.py           # 历史管理
├── websocket/
│   ├── handler.py           # WebSocket处理器
│   ├── connection.py        # 连接管理
│   └── stream.py            # 流式响应
├── models/
│   ├── message.py           # 消息模型
│   ├── session.py           # 会话模型
│   └── response.py          # 响应模型
├── prompts/
│   ├── answer_generation.py # 回答生成Prompt
│   └── followup.py          # 追问生成Prompt
├── config.py
├── Dockerfile
└── requirements.txt
```

## 查询模式说明

### LightRAG查询模式
1. **Naive** - 简单向量检索，适合精确匹配
2. **Local** - 基于实体的局部检索，适合具体概念
3. **Global** - 基于社区的全局检索，适合宏观问题
4. **Hybrid** - 混合模式，综合以上方法

### 模式选择策略
```python
def select_query_mode(question):
    if is_specific_concept_question(question):
        return "local"
    elif is_comparison_question(question):
        return "global"
    elif is_definition_question(question):
        return "naive"
    else:
        return "hybrid"
```

## 关键Prompt

### 回答生成Prompt
```python
ANSWER_GENERATION_PROMPT = """
基于以下知识图谱上下文回答用户问题。

知识上下文:
{context}

相关实体:
{entities}

对话历史:
{history}

用户问题: {question}

要求:
1. 回答要准确、专业
2. 如有跨学科关联，要指出
3. 标注信息来源
4. 如果上下文不足，坦诚说明
"""
```

## WebSocket消息协议

### 客户端 -> 服务端
```json
{
    "type": "message|ping|close",
    "session_id": "xxx",
    "content": "用户消息"
}
```

### 服务端 -> 客户端
```json
{
    "type": "stream|complete|error|pong",
    "content": "部分/完整回答",
    "sources": [...],
    "related_nodes": [...]
}
```
