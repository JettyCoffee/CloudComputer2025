from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from models import IngestRequest, GraphResponse
from core.rag_engine import rag_engine
from core.graph_processor import graph_processor
from core.storage import storage
import uuid
from lightrag import QueryParam

app = FastAPI(title="Knowledge Engine", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"])

# 任务状态跟踪
task_status = {}

@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "knowledge-engine"}

@app.post("/api/ingest")
async def ingest(request: IngestRequest, background_tasks: BackgroundTasks):
    """
    接收 Search Agent 的文档
    
    Search Agent 发送格式:
    {
      "concept": "熵",
      "chunks": [
        {
          "id": "chunk-abc123",
          "content": "...",
          "discipline": "物理学",
          "source": {"url": "...", "title": "..."},
          "relevance_score": 0.85,
          ...
        }
      ]
    }
    """
    # 生成任务 ID
    task_id = f"task-{uuid.uuid4().hex[:8]}"
    
    # 转换 chunks 为 documents 格式
    documents = []
    for chunk in request.chunks:
        documents.append({
            "doc_id": chunk.id,
            "domain": chunk.discipline,  # discipline -> domain
            "content": chunk.content,
            "source": chunk.source.model_dump(),
            "relevance_score": chunk.relevance_score,
            "academic_value": chunk.academic_value,
        })
    
    # 存储文档
    storage.save_documents(documents)
    
    # 后台构建图谱
    task_status[task_id] = "processing"
    background_tasks.add_task(process_task, task_id, request.concept, documents)
    
    return {
        "status": "accepted",
        "task_id": task_id,
        "message": f"Processing {len(documents)} documents for concept '{request.concept}'"
    }

async def process_task(task_id: str, concept: str, documents: list):
    """后台任务"""
    try:
        # 1. LightRAG 构建图谱
        working_dir, chunk_mapping = await rag_engine.build_graph(concept, documents)
        
        # 2. 解析图谱
        graph_data = graph_processor.process_lightrag_output(
            working_dir, 
            documents, 
            concept,
            chunk_mapping
        )
        
        # 3. 保存图谱 JSON
        storage.save_graph(concept, graph_data)
        
        task_status[task_id] = "completed"
        print(f'Task {task_id} completed')
    
    except Exception as e:
        task_status[task_id] = "failed"
        print(f"Task {task_id} failed: {e}")
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


@app.post("/api/qa")
async def answer_question(concept: str, source_node: str, target_node: str, question: str = None) -> dict:
    """
    知识问答接口：利用 LightRAG 推理两个节点之间的关系

    参数:
    - concept: 知识图谱的核心概念
    - source_node: 起始节点 ID
    - target_node: 目标节点 ID
    - question: 用户的自然语言问题（可选，如果不提供则使用默认问题）

    返回:
    - LightRAG 生成的答案
    """
    # 如果用户没有提供问题，生成默认问题
    if not question:
        question = f"请详细说明 '{source_node}' 和 '{target_node}' 之间的关系，并提供推理过程，100字左右。"
    else:
        # 在用户问题中添加节点信息
        question = f"在知识图谱中，关于 '{source_node}' 和 '{target_node}'：{question}"
    
    # 配置 QueryParam
    query_param = QueryParam(
        mode="hybrid",  # 使用混合检索模式
        user_prompt=f"""
你是一个知识图谱分析专家。请根据以下要求回答问题：

1. 核心概念：{concept}
2. 起始节点：{source_node}
3. 目标节点：{target_node}

请从知识图谱中检索相关信息，分析这两个节点之间的关系，并简要给出推理过程，100字左右。
"""
    )
    
    try:
        # 调用 LightRAG 的查询方法
        answer = await rag_engine.query(concept, question, param=query_param)
        
        print(f"QA Answer: {answer}")
        return {
            "concept": concept,
            "source_node": source_node,
            "target_node": target_node,
            "question": question,
            "answer": answer
        }
    
    except Exception as e:
        print(f"QA Error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")

 

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app", 
        host="0.0.0.0",  # 允许外部访问
        port=8002,        # 端口
        reload=True       # 开发模式自动重载
    )
