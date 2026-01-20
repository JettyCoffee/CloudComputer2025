from pydantic import BaseModel
from typing import List, Optional

# ========== 输入模型 ==========
class DocItem(BaseModel):
    doc_id: str
    domain: str  # 学科领域
    content: str

class IngestRequest(BaseModel):
    task_id: str
    concept: str  # 核心概念
    documents: List[DocItem]

# ========== 输出模型 ==========
class NodeItem(BaseModel):
    id: str
    label: str
    description: str
    domains: List[str]  # 可能属于多个领域
    source_chunks: List[str]  # 来源 Chunk ID
    size: int = 15  # 节点大小(前端可用)

class EdgeItem(BaseModel):
    source: str
    target: str
    relation: str
    description: str = ""

class GraphResponse(BaseModel):
    concept: str
    nodes: List[NodeItem]
    edges: List[EdgeItem]
    total_nodes: int
    total_edges: int