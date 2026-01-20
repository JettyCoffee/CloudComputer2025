// Search Agent API Client

// API Base URL - uses Vite proxy in development
const API_BASE = '/api';

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

  // ============ 图谱相关 (暂用Mock数据，后续接入knowledge-engine) ============
  
  /**
   * 获取知识图谱数据
   */
  getGraph: async (concept) => {
    await delay(500);
    return mockGraphData[concept] || mockGraphData["默认"];
  },

  // ============ 聊天相关 (Mock实现，后续接入) ============
  
  /**
   * 流式回答
   */
  async *streamAnswer(question) {
    const responses = [
      "根据**知识图谱**的关联分析，这个概念横跨了多个学科。",
      "在**热力学**中，它代表系统的无序程度（S = k ln Ω）。",
      "而在**信息论**中，它度量的是信息的不确定性（H = -Σ p(x) log p(x)）。",
      "有趣的是，这两个定义在数学形式上是惊人一致的。",
      "这种跨学科的联系暗示了物理世界与信息世界深层的统一性。"
    ];

    for (const chunk of responses) {
      await delay(600);
      yield chunk + " ";
    }
  }
};
