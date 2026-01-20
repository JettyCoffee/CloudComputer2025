import os
import json
import numpy as np
from lightrag import LightRAG, QueryParam
from lightrag.utils import EmbeddingFunc
from sentence_transformers import SentenceTransformer
from openai import AsyncOpenAI
from dotenv import load_dotenv
from typing import Dict

load_dotenv()

class RAGEngine:
    def __init__(self):
        self.base_dir = "./lightrag_workdir"
        os.makedirs(self.base_dir, exist_ok=True)
        self.rag_instances: Dict[str, LightRAG] = {}  # 存储每个概念的 RAG 实例
        
        # 加载本地 Embedding 模型
        model_path = os.getenv("EMBEDDING_MODEL", "./bge-large-zh-v1.5")
        print(f"Loading Embedding Model: {model_path} ...")
        self.embedding_model = SentenceTransformer(model_path, device='cpu')
        print("【success】Embedding Model Loaded")
    
    def get_rag_instance(self, concept: str) -> LightRAG:
        """
        获取或创建指定概念的 LightRAG 实例
        
        如果该概念的 RAG 实例已存在于缓存中，直接返回；
        否则创建新实例（会自动加载 working_dir 中已有的数据）。
        
        参数:
        - concept: 核心概念名称
        
        返回: LightRAG 实例
        """
        if concept not in self.rag_instances:
            working_dir = os.path.join(self.base_dir, concept)
            os.makedirs(working_dir, exist_ok=True)
            
            print(f"正在初始化/加载概念 '{concept}' 的 LightRAG 实例...")
            
            # 创建 LightRAG 实例（如果 working_dir 中有数据会自动加载）
            self.rag_instances[concept] = LightRAG(
                working_dir=working_dir,
                llm_model_func=self._llm_wrapper,
                embedding_func=EmbeddingFunc(
                    embedding_dim=1024,
                    max_token_size=512,
                    func=self._embedding_wrapper
                )
            )

            #await self.rag_instances[concept].initialize_storages()
            
            print(f"✅ 概念 '{concept}' 的 RAG 实例已就绪")
        
        return self.rag_instances[concept]
    
    async def query(self, concept: str, question: str, param: QueryParam = None) -> str:
        """
        使用 LightRAG 进行查询
        
        参数:
        - concept: 核心概念（指定使用哪个知识图谱）
        - question: 用户问题
        - param: 查询参数
        
        返回: LLM 生成的答案
        """
        if param is None:
            param = QueryParam(mode="hybrid")
        
        # 获取对应概念的 RAG 实例（会自动加载已有数据）
        rag = self.get_rag_instance(concept)
        await rag.initialize_storages()
        # 调用 LightRAG 的查询方法
        return await rag.aquery(question, param=param)

    async def _llm_wrapper(self, prompt, system_prompt=None, history_messages=[], **kwargs):
        """LLM 调用"""
        kwargs.pop("hashing_kv", None)
        kwargs.pop("keyword_extraction", None)
        # 过滤掉所有 OpenAI API 不支持的参数
        allowed_params = {
            "temperature", "top_p", "n", "stream", "stop", 
            "max_tokens", "presence_penalty", "frequency_penalty",
            "logit_bias", "user", "response_format", "seed",
            "tools", "tool_choice", "functions", "function_call"
        }
        kwargs = {k: v for k, v in kwargs.items() if k in allowed_params}
    
        instruction = """
        【重要：实体提取控制与过滤规则】
        你是一个严谨的科学知识图谱构建者。请在提取实体时遵守以下标准：

        **保留（白名单）**：
        1. **核心概念**：如 "熵"、"热力学第二定律"、"耗散结构"。
        2. **关键人物**：如 "香农"、"薛定谔"、"玻尔兹曼"。
        3. **专有名词**：如 "最大熵原理"、"公式 S=k*lnW"。
        
        **丢弃（黑名单 - 绝对不要提取）**：
        1. **时间/日期**：不要提取 "1948年"、"20世纪"、"今天" 这样的时间词。
        2. **数量/度量**：不要提取 "一个"、"大量"、"均值" 这样的泛指数量词。
        3. **通用动词/形容词**：不要提取 "增加"、"减少"、"复杂的"、"美丽的" 这种非名词性实体。
        4. **文档元数据**：不要提取 "论文"、"书"、"章节" 这种载体词，除非是专有名词（如《生命是什么》）。
        
        ---------------------
        【必须遵守的规则】
        1. 忽略上文所有的英文示例 (Examples)。
        2. **必须使用简体中文**输出所有内容。
        3. 将英文术语翻译为中文（如 "Entropy" -> "熵"）。
        4. 保持 JSON 格式正确。
        ---------------------
        """
        prompt = prompt + instruction
        
        client = AsyncOpenAI(
            api_key=os.getenv("LLM_API_KEY"),
            base_url=os.getenv("LLM_BASE_URL")
        )
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.extend(history_messages)
        messages.append({"role": "user", "content": prompt})
        
        response = await client.chat.completions.create(
            model=os.getenv("LLM_MODEL", "gpt-4o-mini"),
            messages=messages,
            **kwargs
        )
        return response.choices[0].message.content
    
    async def _embedding_wrapper(self, texts: list) -> np.ndarray:
        return self.embedding_model.encode(texts, normalize_embeddings=True)
    
    async def build_graph(self, concept: str, documents: list) -> tuple[str, dict]:
        """
        为指定概念构建知识图谱
        
        参数:
        - concept: 核心概念
        - documents: [{doc_id, domain, content}, ...]
        
        返回: (工作目录路径, chunk映射字典)
        """
        # 获取该概念的 RAG 实例（如果已存在会直接返回）
        rag = self.get_rag_instance(concept)
        working_dir = os.path.join(self.base_dir, concept)
        
        # 初始化存储（如果是新建的实例）
        await rag.initialize_storages()
        
        # ========== 【关键修改】分别插入每个文档 ==========
        print(f"正在为概念 '{concept}' 构建图谱 ({len(documents)} 文档)...")
         
        
        for doc in documents:
            # 添加元数据标记
            text_with_metadata = f"[DOC_ID: {doc['doc_id']}]\n[领域: {doc['domain']}]\n{doc['content']}"
            
            # 单独插入每个文档
            await rag.ainsert(text_with_metadata)
            
            print(f"已插入: {doc['doc_id']} ({doc['domain']})")
        
        print(f"图谱构建完成: {working_dir}")
        
        # ========== 建立 Chunk 映射 ==========
        chunk_mapping = self._build_chunk_mapping(working_dir, documents)
        
        return working_dir, chunk_mapping
    
    def _build_chunk_mapping(self, working_dir: str, documents: list) -> dict:
        """
        读取 LightRAG 生成的 chunk,建立 chunk_id -> doc_id 映射
        
        策略: 通过 chunk 内容中的 [DOC_ID: xxx] 标记直接识别
        """
        chunk_json_path = os.path.join(working_dir, "kv_store_text_chunks.json")
        
        if not os.path.exists(chunk_json_path):
            print(f"未找到 chunk 文件: {chunk_json_path}")
            return {}
        
        with open(chunk_json_path, 'r', encoding='utf-8') as f:
            chunks = json.load(f)
        
        # 创建 doc_id -> domain 的快速查找表
        doc_domain_map = {doc['doc_id']: doc['domain'] for doc in documents}
        
        mapping = {}
        
        for chunk_id, chunk_data in chunks.items():
            chunk_content = chunk_data.get('content', '')
            
            # 提取 chunk 中包含的所有 DOC_ID 标记
            found_doc_ids = set()
            
            for doc_id in doc_domain_map.keys():
                if f"[DOC_ID: {doc_id}]" in chunk_content:
                    found_doc_ids.add(doc_id)
            
            # 如果没有找到标记,尝试内容匹配（降级策略）
            if not found_doc_ids:
                for doc in documents:
                    # 提取 chunk 的前 100 个字符（去除标记）
                    chunk_clean = chunk_content.replace('[DOC_ID:', '').replace('[领域:', '')
                    if chunk_clean[:100] in doc['content']:
                        found_doc_ids.add(doc['doc_id'])
                        break
            
            # 记录映射（支持多个文档）
            if found_doc_ids:
                domains = [doc_domain_map[doc_id] for doc_id in found_doc_ids]
                mapping[chunk_id] = {
                    'doc_ids': list(found_doc_ids),
                    'domains': list(set(domains))  # 去重
                }
            else:
                print(f"无法匹配 chunk: {chunk_id}")
        
        print(f"成功映射 {len(mapping)}/{len(chunks)} 个 chunks")
        
        # 调试信息：打印映射统计
        domain_stats = {}
        for chunk_id, info in mapping.items():
            for domain in info['domains']:
                domain_stats[domain] = domain_stats.get(domain, 0) + 1
        
        print(f"领域分布: {domain_stats}")
        
        return mapping

rag_engine = RAGEngine()