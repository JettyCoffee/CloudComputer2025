# Tests - 测试目录

## 目录说明
本目录包含项目的所有测试代码。

## 需要完成的内容

### 1. 后端单元测试
- [ ] `backend/test_search_service.py` - 检索服务测试
- [ ] `backend/test_graph_service.py` - 图谱服务测试
- [ ] `backend/test_chat_service.py` - 对话服务测试
- [ ] `backend/test_api_gateway.py` - API网关测试

### 2. 后端集成测试
- [ ] `integration/test_search_to_graph.py` - 检索到图谱流程测试
- [ ] `integration/test_graph_to_chat.py` - 图谱到对话流程测试
- [ ] `integration/test_e2e.py` - 端到端测试

### 3. 前端测试
- [ ] `frontend/components/` - 组件测试
- [ ] `frontend/hooks/` - Hooks测试
- [ ] `frontend/api/` - API调用测试

### 4. 测试配置
- [ ] `conftest.py` - Pytest配置
- [ ] `fixtures/` - 测试数据
- [ ] `mocks/` - Mock对象

## 文件结构
```
tests/
├── backend/
│   ├── unit/
│   │   ├── test_search_service.py
│   │   ├── test_graph_service.py
│   │   └── test_chat_service.py
│   └── integration/
│       ├── test_search_to_graph.py
│       └── test_e2e.py
├── frontend/
│   ├── components/
│   └── hooks/
├── fixtures/
│   ├── sample_concept.json
│   ├── sample_graph.json
│   └── sample_chat.json
├── mocks/
│   ├── mock_llm.py
│   └── mock_tavily.py
└── conftest.py
```

## 测试规范

### 命名规范
- 测试文件: `test_<module_name>.py`
- 测试类: `Test<ClassName>`
- 测试函数: `test_<function_name>_<scenario>`

### 示例测试
```python
import pytest
from backend.search_service.agents.classifier import ClassifierAgent

class TestClassifierAgent:
    @pytest.fixture
    def classifier(self):
        return ClassifierAgent(llm_client=MockLLM())
    
    def test_classify_concept_returns_disciplines(self, classifier):
        result = classifier.classify("熵")
        assert "disciplines" in result
        assert len(result["disciplines"]) >= 3
    
    def test_classify_concept_includes_primary_discipline(self, classifier):
        result = classifier.classify("熵")
        assert "primary_discipline" in result
        assert result["primary_discipline"] is not None
```

### 测试覆盖率
目标覆盖率：
- 后端核心逻辑: >= 80%
- 前端组件: >= 70%
- 集成测试: 覆盖主要用户流程
