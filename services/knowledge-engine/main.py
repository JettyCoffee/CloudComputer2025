from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from models import IngestRequest, GraphResponse
from core.rag_engine import rag_engine
from core.graph_processor import graph_processor
from core.storage import storage
import asyncio

app = FastAPI(title="Knowledge Engine", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"])

# 任务状态跟踪（简化版）
task_status = {}

@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "knowledge-engine"}

@app.post("/api/ingest")
async def ingest(request: IngestRequest, background_tasks: BackgroundTasks):
    """
    接收 Search Agent 的文档
    
    示例请求:
    {
      "task_id": "uuid-123",
      "concept": "熵",
      "documents": [
        {"doc_id": "doc1", "domain": "物理学", "content": "..."},
        {"doc_id": "doc2", "domain": "信息论", "content": "..."}
      ]
    }
    """
    # 1. 存储文档
    docs_dict = [doc.dict() for doc in request.documents]
    storage.save_documents(docs_dict)
    
    # 2. 后台构建图谱
    task_status[request.task_id] = "processing"
    background_tasks.add_task(process_task, request.task_id, request.concept, docs_dict)
    
    return {
        "status": "accepted",
        "task_id": request.task_id,
        "message": f"Processing {len(request.documents)} documents for concept '{request.concept}'"
    }

async def process_task(task_id: str, concept: str, documents: list):
    """后台任务"""
    try:
        # 1. LightRAG 构建图谱（现在返回映射数据）
        working_dir, chunk_mapping = await rag_engine.build_graph(concept, documents)
        
        # 2. 解析图谱（传入映射数据）
        graph_data = graph_processor.process_lightrag_output(
            working_dir, 
            documents, 
            concept,
            chunk_mapping  # 新增参数
        )
        
        # 3. 保存图谱 JSON
        storage.save_graph(concept, graph_data)
        
        task_status[task_id] = "completed"
        print(f"✅ Task {task_id} completed for concept '{concept}'")
    
    except Exception as e:
        task_status[task_id] = "failed"
        print(f"❌ Task {task_id} failed: {e}")
        import traceback
        traceback.print_exc()

@app.get("/api/task/{task_id}")
async def get_task_status(task_id: str):
    """查询任务状态"""
    status = task_status.get(task_id, "not_found")
    return {"task_id": task_id, "status": status}

@app.get("/api/graph/{concept}", response_model=GraphResponse)
async def get_graph(concept: str):
    """
    前端调用: 获取图谱数据
    
    返回示例:
    {
      "concept": "熵",
      "nodes": [
        {
          "id": "熵",
          "label": "熵",
          "description": "系统无序程度的度量",
          "domains": ["物理学", "信息论"],
          "source_chunks": ["chunk_1", "chunk_2"],
          "size": 35
        }
      ],
      "edges": [
        {
          "source": "熵",
          "target": "热力学第二定律",
          "relation": "遵循",
          "description": "..."
        }
      ],
      "total_nodes": 15,
      "total_edges": 20
    }
    """
    graph_data = storage.get_graph(concept)
    
    if not graph_data:
        raise HTTPException(status_code=404, detail=f"Graph for concept '{concept}' not found")
    
    return GraphResponse(**graph_data)

@app.get("/api/concepts")
async def list_concepts():
    """列出所有已构建的概念"""
    import os
    graph_dir = "./data/graphs"
    
    if not os.path.exists(graph_dir):
        return {"concepts": []}
    
    concepts = [f.replace('.json', '') for f in os.listdir(graph_dir) if f.endswith('.json')]
    return {"concepts": concepts}

# ...existing code...

@app.get("/api/concepts")
async def list_concepts():
    """列出所有已构建的概念"""
    import os
    graph_dir = "./data/graphs"
    
    if not os.path.exists(graph_dir):
        return {"concepts": []}
    
    concepts = [f.replace('.json', '') for f in os.listdir(graph_dir) if f.endswith('.json')]
    return {"concepts": concepts}
 

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app", 
        host="0.0.0.0",  # 允许外部访问
        port=8002,        # 端口
        reload=True       # 开发模式自动重载
    )
