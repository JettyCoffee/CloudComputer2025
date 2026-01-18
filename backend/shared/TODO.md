# Shared - 共享模块

## 目录说明
本目录包含所有后端服务共享的代码，包括工具类、模型定义、常量等。

## 需要完成的内容

### 1. 通用模型
- [ ] 基础响应模型 (`BaseResponse`)
- [ ] 分页模型 (`Pagination`)
- [ ] 错误模型 (`ErrorDetail`)

### 2. 工具类
- [ ] 日志工具 (`logger.py`)
- [ ] 配置加载器 (`config_loader.py`)
- [ ] ID生成器 (`id_generator.py`)
- [ ] 时间工具 (`datetime_utils.py`)

### 3. LLM相关
- [ ] 统一LLM客户端接口
- [ ] Prompt模板基类
- [ ] Token计数工具
- [ ] 调用重试装饰器

### 4. 数据库相关
- [ ] 数据库连接基类
- [ ] Redis工具类
- [ ] Neo4j工具类

### 5. 常量定义
- [ ] 学科类型枚举
- [ ] 实体类型枚举
- [ ] 关系类型枚举
- [ ] 错误码定义

## 文件结构
```
shared/
├── __init__.py
├── models/
│   ├── base.py              # 基础模型
│   ├── pagination.py        # 分页
│   └── error.py             # 错误
├── utils/
│   ├── logger.py            # 日志
│   ├── config.py            # 配置
│   ├── id_gen.py            # ID生成
│   └── datetime.py          # 时间
├── llm/
│   ├── client.py            # LLM客户端
│   ├── prompt_base.py       # Prompt基类
│   └── retry.py             # 重试机制
├── db/
│   ├── redis.py             # Redis工具
│   └── neo4j.py             # Neo4j工具
├── constants/
│   ├── disciplines.py       # 学科常量
│   ├── entity_types.py      # 实体类型
│   ├── relation_types.py    # 关系类型
│   └── error_codes.py       # 错误码
└── exceptions/
    └── custom.py            # 自定义异常
```

## 示例代码

### 基础响应模型
```python
from pydantic import BaseModel
from typing import Generic, TypeVar, Optional

T = TypeVar('T')

class BaseResponse(BaseModel, Generic[T]):
    code: int = 200
    message: str = "success"
    data: Optional[T] = None
```

### LLM客户端接口
```python
from abc import ABC, abstractmethod

class LLMClient(ABC):
    @abstractmethod
    async def chat(self, messages: list, **kwargs) -> str:
        pass
    
    @abstractmethod
    async def stream_chat(self, messages: list, **kwargs):
        pass
```
