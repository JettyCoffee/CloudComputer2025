# API Gateway - API网关服务

## 目录说明
API网关是所有外部请求的统一入口，负责请求路由、认证、限流等。

## 需要完成的内容

### 1. 核心功能
- [ ] FastAPI应用主入口 (`main.py`)
- [ ] 路由注册与管理
- [ ] 请求/响应中间件
- [ ] 统一的响应格式封装

### 2. API路由模块
- [ ] `/api/search/*` - 概念搜索相关路由
- [ ] `/api/graph/*` - 知识图谱操作路由
- [ ] `/api/chat/*` - RAG对话路由
- [ ] `/api/upload/*` - 文件上传路由
- [ ] `/api/health` - 健康检查路由

### 3. 中间件
- [ ] CORS跨域处理
- [ ] 请求日志记录
- [ ] 异常全局捕获
- [ ] 请求限流（可选）

### 4. 服务调用
- [ ] 封装对search-service的调用
- [ ] 封装对graph-service的调用
- [ ] 封装对chat-service的调用
- [ ] 服务发现与负载均衡（可选）

### 5. WebSocket支持
- [ ] WebSocket连接管理
- [ ] 实时对话流式响应

## 文件结构
```
api-gateway/
├── main.py              # FastAPI入口
├── routers/
│   ├── search.py        # 搜索路由
│   ├── graph.py         # 图谱路由
│   ├── chat.py          # 对话路由
│   └── upload.py        # 上传路由
├── middleware/
│   ├── cors.py
│   ├── logging.py
│   └── error_handler.py
├── schemas/
│   ├── request.py       # 请求模型
│   └── response.py      # 响应模型
├── services/
│   └── service_client.py # 微服务调用客户端
├── config.py            # 配置
├── Dockerfile
└── requirements.txt
```

## API接口清单
参考 Technical.md 中的API设计部分
