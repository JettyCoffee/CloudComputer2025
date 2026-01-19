// Mock Data Generator

// Helper to simulate delay
const delay = (ms) => new Promise(resolve => setTimeout(resolve, ms));

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

export const api = {
  // Simulate network delay for searching
  classifyConcept: async (concept) => {
    await delay(800);
    return {
      concept,
      disciplines: ["物理学", "计算机科学", "统计学", "生物学"]
    };
  },

  // Get graph data
  getGraph: async (concept) => {
    await delay(1500);
    return mockGraphData[concept] || mockGraphData["默认"];
  },

  // Mock streaming response for chat
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
