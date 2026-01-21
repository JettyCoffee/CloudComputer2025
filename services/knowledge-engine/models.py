from pydantic import BaseModel, Field
from typing import List, Optional

# ========== 输入模型 ==========
class SourceInfo(BaseModel):
    url: str
    title: Optional[str] = None
    published_date: Optional[str] = None

class ValidationInfo(BaseModel):
    is_validated: bool = False
    confidence: float = Field(0.0, ge=0.0, le=1.0)
    notes: Optional[str] = None

class Chunk(BaseModel):
    """Search Agent 发送的 Chunk 格式"""
    id: str
    content: str
    discipline: str  # 对应 domain
    source: SourceInfo
    relevance_score: float = Field(0.0, ge=0.0, le=1.0)
    academic_value: float = Field(0.0, ge=0.0, le=1.0)
    validation: ValidationInfo = Field(default_factory=ValidationInfo)
    extracted_entities: list[str] = Field(default_factory=list)

class IngestRequest(BaseModel):
    """接收 Search Agent 的数据"""
    concept: str
    chunks: list[Chunk] 

class QARequest(BaseModel):
    """知识问答请求"""
    concept: str
    source_node: str
    target_node: str
    question: Optional[str] = None

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