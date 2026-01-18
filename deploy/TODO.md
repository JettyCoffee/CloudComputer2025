# Deploy - 部署配置

## 目录说明
本目录包含所有部署相关的配置文件，包括Docker、docker-compose等。

## 需要完成的内容

### 1. Docker配置
- [ ] `Dockerfile.frontend` - 前端Docker镜像
- [ ] `Dockerfile.api-gateway` - API网关Docker镜像
- [ ] `Dockerfile.search-service` - 检索服务Docker镜像
- [ ] `Dockerfile.graph-service` - 图谱服务Docker镜像
- [ ] `Dockerfile.chat-service` - 对话服务Docker镜像

### 2. Docker Compose
- [ ] `docker-compose.yml` - 主编排文件
- [ ] `docker-compose.dev.yml` - 开发环境覆盖配置
- [ ] `docker-compose.prod.yml` - 生产环境覆盖配置

### 3. 环境配置
- [ ] `.env.example` - 环境变量模板
- [ ] `.env.dev` - 开发环境变量
- [ ] `.env.prod` - 生产环境变量

### 4. Nginx配置（可选）
- [ ] `nginx/nginx.conf` - Nginx配置
- [ ] `nginx/ssl/` - SSL证书目录

### 5. 数据库初始化
- [ ] `init-scripts/neo4j/` - Neo4j初始化脚本
- [ ] `init-scripts/postgres/` - PostgreSQL初始化脚本

## 文件结构
```
deploy/
├── docker/
│   ├── Dockerfile.frontend
│   ├── Dockerfile.api-gateway
│   ├── Dockerfile.search-service
│   ├── Dockerfile.graph-service
│   └── Dockerfile.chat-service
├── docker-compose.yml
├── docker-compose.dev.yml
├── docker-compose.prod.yml
├── .env.example
├── nginx/
│   └── nginx.conf
└── init-scripts/
    ├── neo4j/
    └── postgres/
```

## Docker Compose服务架构

```yaml
services:
  # 前端
  frontend:
    build: ./docker/Dockerfile.frontend
    ports: ["3000:3000"]
    depends_on: [api-gateway]

  # API网关
  api-gateway:
    build: ./docker/Dockerfile.api-gateway
    ports: ["8000:8000"]
    environment:
      - SEARCH_SERVICE_URL=http://search-service:8001
      - GRAPH_SERVICE_URL=http://graph-service:8002
      - CHAT_SERVICE_URL=http://chat-service:8003
    depends_on:
      - search-service
      - graph-service
      - chat-service

  # 检索服务
  search-service:
    build: ./docker/Dockerfile.search-service
    environment:
      - TAVILY_API_KEY=${TAVILY_API_KEY}
      - LLM_API_KEY=${LLM_API_KEY}
      - REDIS_URL=redis://redis:6379
    depends_on: [redis]

  # 图谱服务
  graph-service:
    build: ./docker/Dockerfile.graph-service
    environment:
      - NEO4J_URI=bolt://neo4j:7687
      - NEO4J_USER=${NEO4J_USER}
      - NEO4J_PASSWORD=${NEO4J_PASSWORD}
      - LLM_API_KEY=${LLM_API_KEY}
    depends_on: [neo4j]

  # 对话服务
  chat-service:
    build: ./docker/Dockerfile.chat-service
    environment:
      - NEO4J_URI=bolt://neo4j:7687
      - REDIS_URL=redis://redis:6379
      - LLM_API_KEY=${LLM_API_KEY}
    depends_on: [neo4j, redis]

  # Neo4j图数据库
  neo4j:
    image: neo4j:5-community
    ports:
      - "7474:7474"  # HTTP
      - "7687:7687"  # Bolt
    environment:
      - NEO4J_AUTH=${NEO4J_USER}/${NEO4J_PASSWORD}
    volumes:
      - neo4j_data:/data
      - ./init-scripts/neo4j:/docker-entrypoint-initdb.d

  # Redis缓存
  redis:
    image: redis:7-alpine
    ports: ["6379:6379"]
    volumes:
      - redis_data:/data

  # PostgreSQL (元数据存储)
  postgres:
    image: postgres:15-alpine
    environment:
      - POSTGRES_USER=${POSTGRES_USER}
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
      - POSTGRES_DB=${POSTGRES_DB}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init-scripts/postgres:/docker-entrypoint-initdb.d

volumes:
  neo4j_data:
  redis_data:
  postgres_data:
```

## 环境变量模板 (.env.example)

```bash
# LLM配置
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=your_anthropic_key
OPENAI_API_KEY=your_openai_key

# Tavily搜索
TAVILY_API_KEY=your_tavily_key

# Neo4j
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password

# PostgreSQL
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
POSTGRES_DB=knowledge_graph

# Redis
REDIS_URL=redis://redis:6379

# 服务端口
FRONTEND_PORT=3000
API_GATEWAY_PORT=8000
```
