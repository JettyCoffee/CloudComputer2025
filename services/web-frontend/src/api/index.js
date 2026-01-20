// Search Agent & Knowledge Engine API Client

// API Base URLs - uses Vite proxy in development
const API_BASE = '/api';
const KG_API_BASE = '/kg-api';  // Knowledge Engine API

// Helper to simulate delay (for mock data fallback)
const delay = (ms) => new Promise(resolve => setTimeout(resolve, ms));

// Mock Graph Data (保留用于图谱展示，后续可接入knowledge-engine)
export const mockGraphData = {
  "熵": {
    nodes: [
      { id: "熵", group: "核心", val: 20 },
      { id: "热力学", group: "物理学", val: 15 },
      { id: "统计力学", group: "物理学", val: 12 },
      { id: "信息论", group: "计算机科学", val: 15 },
      { id: "香农熵", group: "计算机科学", val: 10 },
      { id: "玻尔兹曼熵", group: "物理学", val: 10 },
      { id: "最大熵原理", group: "统计学", val: 8 },
      { id: "生命与熵", group: "生物学", val: 10 },
      { id: "耗散结构", group: "化学", val: 8 },
      { id: "麦克斯韦妖", group: "物理学", val: 8 },
      { id: "数据压缩", group: "计算机科学", val: 6 },
    ],
    links: [
      { source: "熵", target: "热力学" },
      { source: "熵", target: "信息论" },
      { source: "熵", target: "统计力学" },
      { source: "热力学", target: "玻尔兹曼熵" },
      { source: "信息论", target: "香农熵" },
      { source: "统计力学", target: "玻尔兹曼熵" },
      { source: "信息论", target: "数据压缩" },
      { source: "统计力学", target: "最大熵原理" },
      { source: "热力学", target: "麦克斯韦妖" },
      { source: "熵", target: "生命与熵" },
      { source: "热力学", target: "耗散结构" },
      { source: "生命与熵", target: "耗散结构" }
    ]
  },
  "默认": {
    nodes: [
      { id: "查询词", group: "核心", val: 20 },
      { id: "概念A", group: "领域1", val: 10 },
      { id: "概念B", group: "领域2", val: 10 },
      { id: "概念C", group: "领域3", val: 10 },
    ],
    links: [
      { source: "查询词", target: "概念A" },
      { source: "查询词", target: "概念B" },
      { source: "查询词", target: "概念C" },
      { source: "概念A", target: "概念B" }
    ]
  }
};

/**
 * 统一请求处理函数
 */
async function request(endpoint, options = {}) {
  const url = `${API_BASE}${endpoint}`;
  const config = {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  };

  const response = await fetch(url, config);
  
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `HTTP ${response.status}`);
  }

  return response.json();
}

/**
 * Knowledge Engine 请求处理函数
 */
async function kgRequest(endpoint, options = {}) {
  const url = `${KG_API_BASE}${endpoint}`;
  const config = {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  };

  const response = await fetch(url, config);
  
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `HTTP ${response.status}`);
  }

  return response.json();
}

export const api = {
  /**
   * 健康检查
   */
  health: async () => {
    const res = await request('/health');
    return res.data;
  },

  /**
   * 概念分类 - 获取概念相关的学科领域
   * @param {string} concept - 要分类的概念
   * @param {number} maxDisciplines - 最大返回学科数
   * @param {number} minRelevance - 最小相关度阈值
   * @returns {Promise<{concept, primary_discipline, disciplines, suggested_additions}>}
   */
  classifyConcept: async (concept, maxDisciplines = 5, minRelevance = 0.3) => {
    const res = await request('/search/classify', {
      method: 'POST',
      body: JSON.stringify({
        concept,
        max_disciplines: maxDisciplines,
        min_relevance: minRelevance,
      }),
    });
    return res.data;
  },

  /**
   * 开始搜索任务
   * @param {string} concept - 搜索的概念
   * @param {Array<{name: string, search_keywords: string[]}>} disciplines - 学科列表
   * @param {Object} searchConfig - 搜索配置
   * @returns {Promise<{task_id, status, created_at, estimated_duration_seconds}>}
   */
  startSearch: async (concept, disciplines, searchConfig = {}) => {
    const res = await request('/search/start', {
      method: 'POST',
      body: JSON.stringify({
        concept,
        disciplines: disciplines.map(d => 
          typeof d === 'string' 
            ? { name: d, search_keywords: [] } 
            : d
        ),
        search_config: {
          depth: searchConfig.depth || 'medium',
          max_results_per_discipline: searchConfig.maxResultsPerDiscipline || 10,
          enable_validation: searchConfig.enableValidation !== false,
        },
      }),
    });
    return res.data;
  },

  /**
   * 获取搜索任务状态
   * @param {string} taskId - 任务ID
   * @returns {Promise<{task_id, status, progress, partial_results, started_at, updated_at}>}
   */
  getSearchStatus: async (taskId) => {
    const res = await request(`/search/status/${taskId}`);
    return res.data;
  },

  /**
   * 获取搜索结果
   * @param {string} taskId - 任务ID
   * @param {Object} options - 分页和过滤选项
   * @returns {Promise<{task_id, concept, summary, chunks, pagination}>}
   */
  getSearchResults: async (taskId, options = {}) => {
    const params = new URLSearchParams();
    if (options.page) params.set('page', options.page);
    if (options.pageSize) params.set('page_size', options.pageSize);
    if (options.discipline) params.set('discipline', options.discipline);
    if (options.minRelevance !== undefined) params.set('min_relevance', options.minRelevance);

    const queryString = params.toString();
    const endpoint = `/search/results/${taskId}${queryString ? `?${queryString}` : ''}`;
    const res = await request(endpoint);
    return res.data;
  },

  /**
   * 取消搜索任务
   * @param {string} taskId - 任务ID
   * @returns {Promise<{task_id, status}>}
   */
  cancelSearch: async (taskId) => {
    const res = await request(`/search/tasks/${taskId}`, {
      method: 'DELETE',
    });
    return res.data;
  },

  /**
   * 轮询搜索状态直到完成
   * @param {string} taskId - 任务ID
   * @param {Function} onProgress - 进度回调
   * @param {number} interval - 轮询间隔(ms)
   * @returns {Promise<{task_id, concept, summary, chunks, pagination}>}
   */
  pollSearchUntilComplete: async (taskId, onProgress, interval = 2000) => {
    while (true) {
      const status = await api.getSearchStatus(taskId);
      
      if (onProgress) {
        onProgress(status);
      }

      if (status.status === 'completed') {
        return api.getSearchResults(taskId);
      }

      if (status.status === 'failed') {
        throw new Error('搜索任务失败');
      }

      if (status.status === 'cancelled') {
        throw new Error('搜索任务已取消');
      }

      await delay(interval);
    }
  },

  // ============ 图谱相关 (接入knowledge-engine) ============
  
  /**
   * 获取已有概念列表
   * @returns {Promise<{concepts: string[]}>}
   */
  listConcepts: async () => {
    try {
      return await kgRequest('/concepts');
    } catch (error) {
      console.error('获取概念列表失败:', error);
      return { concepts: [] };
    }
  },

  /**
   * 获取知识图谱数据 (从 knowledge-engine 获取)
   * @param {string} concept - 概念名称
   * @returns {Promise<{concept, nodes, edges, total_nodes, total_edges}>}
   */
  getGraph: async (concept) => {
    try {
      const data = await kgRequest(`/graph/${encodeURIComponent(concept)}`);
      
      // 转换为前端需要的格式
      return {
        nodes: data.nodes.map(n => ({
          id: n.id,
          label: n.label,
          description: n.description,
          group: n.domains?.[0] || '未知',
          domains: n.domains || [],
          val: n.size || 15,
          sourceChunks: n.source_chunks || []
        })),
        links: data.edges.map(e => ({
          source: e.source,
          target: e.target,
          relation: e.relation,
          description: e.description || ''
        })),
        totalNodes: data.total_nodes,
        totalEdges: data.total_edges
      };
    } catch (error) {
      console.warn('从knowledge-engine获取图谱失败,使用mock数据:', error.message);
      // Fallback to mock data
      return mockGraphData[concept] || mockGraphData["默认"];
    }
  },

  /**
   * 获取图谱构建任务状态
   * @param {string} taskId - 任务ID
   * @returns {Promise<{task_id, status}>}
   */
  getGraphTaskStatus: async (taskId) => {
    return await kgRequest(`/task/${taskId}`);
  },

  // ============ 知识问答相关 (接入knowledge-engine的LightRAG) ============
  
  /**
   * 知识问答 - 查询节点之间的关系
   * @param {string} concept - 核心概念
   * @param {string} sourceNode - 源节点ID
   * @param {string} targetNode - 目标节点ID
   * @param {string} question - 用户问题（可选）
   * @returns {Promise<{concept, source_node, target_node, question, answer}>}
   */
  queryNodeRelation: async (concept, sourceNode, targetNode, question = null) => {
    const params = new URLSearchParams();
    params.set('concept', concept);
    params.set('source_node', sourceNode);
    params.set('target_node', targetNode);
    if (question) {
      params.set('question', question);
    }
    
    return await kgRequest(`/qa?${params.toString()}`, {
      method: 'POST'
    });
  },

  /**
   * 通用知识问答
   * @param {string} concept - 核心概念
   * @param {string} question - 用户问题
   * @returns {Promise<{answer: string}>}
   */
  askQuestion: async (concept, question) => {
    const params = new URLSearchParams();
    params.set('concept', concept);
    params.set('source_node', concept);  // 使用concept作为source
    params.set('target_node', concept);  // 使用concept作为target
    params.set('question', question);
    
    return await kgRequest(`/qa?${params.toString()}`, {
      method: 'POST'
    });
  },

  // ============ 聊天相关 (接入knowledge-engine的QA) ============
  
  /**
   * 流式回答 (目前knowledge-engine不支持流式，模拟流式输出)
   * @param {string} question - 用户问题
   * @param {string} concept - 当前概念
   * @param {string} sourceNode - 源节点（可选）
   * @param {string} targetNode - 目标节点（可选）
   */
  async *streamAnswer(question, concept = null, sourceNode = null, targetNode = null) {
    try {
      let answer;
      
      if (sourceNode && targetNode && sourceNode !== targetNode) {
        // 查询节点关系
        const result = await api.queryNodeRelation(concept, sourceNode, targetNode, question);
        answer = result.answer;
      } else if (concept) {
        // 通用问答
        const result = await api.askQuestion(concept, question);
        answer = result.answer;
      } else {
        // 没有概念时使用mock
        answer = "请先选择一个概念进行探索，或者开始搜索来构建知识图谱。";
      }
      
      // 模拟流式输出
      const chunks = answer.split(/(?<=[。！？\n])/);
      for (const chunk of chunks) {
        if (chunk.trim()) {
          await delay(100 + Math.random() * 200);
          yield chunk;
        }
      }
    } catch (error) {
      console.error('问答失败:', error);
      yield `抱歉，查询失败: ${error.message}`;
    }
  }
};
