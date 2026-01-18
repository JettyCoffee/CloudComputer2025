# Scripts - 脚本工具

## 目录说明
本目录包含项目开发和部署所需的脚本工具。

## 需要完成的内容

### 1. 开发脚本
- [ ] `setup-dev.sh` - 开发环境初始化脚本
- [ ] `start-dev.sh` - 启动开发环境
- [ ] `stop-dev.sh` - 停止开发环境

### 2. 部署脚本
- [ ] `deploy.sh` - 一键部署脚本
- [ ] `build.sh` - 构建所有镜像
- [ ] `push-images.sh` - 推送镜像到仓库

### 3. 数据库脚本
- [ ] `init-db.sh` - 初始化数据库
- [ ] `backup-db.sh` - 数据库备份
- [ ] `restore-db.sh` - 数据库恢复

### 4. 测试脚本
- [ ] `run-tests.sh` - 运行所有测试
- [ ] `lint.sh` - 代码检查

### 5. 工具脚本
- [ ] `generate-api-docs.sh` - 生成API文档
- [ ] `clean.sh` - 清理临时文件和构建产物

## 文件结构
```
scripts/
├── dev/
│   ├── setup-dev.sh
│   ├── start-dev.sh
│   └── stop-dev.sh
├── deploy/
│   ├── deploy.sh
│   ├── build.sh
│   └── push-images.sh
├── db/
│   ├── init-db.sh
│   ├── backup-db.sh
│   └── restore-db.sh
├── test/
│   ├── run-tests.sh
│   └── lint.sh
└── utils/
    ├── generate-api-docs.sh
    └── clean.sh
```

## 脚本示例

### setup-dev.sh
```bash
#!/bin/bash
set -e

echo "Setting up development environment..."

# 创建.env文件
if [ ! -f .env ]; then
    cp deploy/.env.example .env
    echo "Created .env file from template"
fi

# 安装前端依赖
cd frontend && npm install && cd ..

# 安装后端依赖
cd backend && pip install -r requirements.txt && cd ..

# 启动数据库容器
docker-compose -f deploy/docker-compose.yml up -d neo4j redis postgres

echo "Development environment is ready!"
```

### start-dev.sh
```bash
#!/bin/bash

# 启动后端服务
cd backend/api-gateway && uvicorn main:app --reload --port 8000 &
cd backend/search-service && uvicorn main:app --reload --port 8001 &
cd backend/graph-service && uvicorn main:app --reload --port 8002 &
cd backend/chat-service && uvicorn main:app --reload --port 8003 &

# 启动前端
cd frontend && npm run dev
```
