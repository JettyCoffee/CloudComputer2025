import os
import json
from typing import Dict, List

DATA_DIR = "./data"
GRAPH_DIR = os.path.join(DATA_DIR, "graphs")

class JSONStorage:
    def __init__(self):
        os.makedirs(DATA_DIR, exist_ok=True)
        os.makedirs(GRAPH_DIR, exist_ok=True)
        
        self.docs_file = os.path.join(DATA_DIR, "documents.json")
        self.chunk_map_file = os.path.join(DATA_DIR, "chunk_mapping.json")
        
        # 初始化文件
        if not os.path.exists(self.docs_file):
            self._save_json(self.docs_file, {})
        if not os.path.exists(self.chunk_map_file):
            self._save_json(self.chunk_map_file, {})
    
    def _load_json(self, path: str) -> dict:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _save_json(self, path: str, data: dict):
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    # ========== 文档管理 ==========
    def save_documents(self, docs: List[dict]):
        """存储原始文档"""
        all_docs = self._load_json(self.docs_file)
        
        for doc in docs:
            all_docs[doc['doc_id']] = {
                'domain': doc['domain'],
                'content': doc['content']
            }
        
        self._save_json(self.docs_file, all_docs)
    
    def get_document(self, doc_id: str) -> dict:
        all_docs = self._load_json(self.docs_file)
        return all_docs.get(doc_id)
    
    def get_all_documents(self) -> dict:
        return self._load_json(self.docs_file)
    
    # ========== Chunk 映射管理 ==========
    def save_chunk_mapping(self, chunk_id: str, doc_id: str):
        """记录 Chunk 属于哪个文档"""
        mapping = self._load_json(self.chunk_map_file)
        mapping[chunk_id] = doc_id
        self._save_json(self.chunk_map_file, mapping)
    
    def get_domain_by_chunk(self, chunk_id: str) -> str:
        """通过 Chunk ID 反查领域"""
        mapping = self._load_json(self.chunk_map_file)
        doc_id = mapping.get(chunk_id)
        
        if not doc_id:
            return "未知"
        
        doc = self.get_document(doc_id)
        return doc.get('domain', '未知') if doc else '未知'
    
    # ========== 图谱管理 ==========
    def save_graph(self, concept: str, graph_data: dict):
        """存储图谱 JSON"""
        graph_file = os.path.join(GRAPH_DIR, f"{concept}.json")
        self._save_json(graph_file, graph_data)
    
    def get_graph(self, concept: str) -> dict:
        """读取图谱 JSON"""
        graph_file = os.path.join(GRAPH_DIR, f"{concept}.json")
        
        if not os.path.exists(graph_file):
            return None
        
        return self._load_json(graph_file)

storage = JSONStorage()