<template>
  <div ref="container" class="graph-container">
    <div v-if="graphStore.loading" class="loading-overlay">
      <div class="spinner"></div>
      <p>正在构建知识图谱...</p>
    </div>

    <!-- Controls -->
    <div class="graph-controls" v-if="graphStore.nodes.length > 0">
      <button @click="resetZoom" class="control-btn" title="重置视图">
        <span>⤢</span>
      </button>
    </div>

    <svg ref="svgRef"></svg>
    
    <NodeDetail />

    <!-- Legend -->
    <div class="legend" v-if="graphStore.disciplines.length > 0">
      <div class="legend-title">学科分布 (点击筛选)</div>
      <div 
        v-for="disc in graphStore.disciplines" 
        :key="disc" 
        class="legend-item"
        :class="{ inactive: hiddenGroups.has(disc) }"
        @click="toggleGroup(disc)"
      >
        <span class="dot" :style="{ backgroundColor: colorScale(disc) }"></span>
        <span>{{ disc }}</span>
      </div>
    </div>

    <div class="graph-hint" v-if="!graphStore.loading && graphStore.nodes.length > 0">
      悬停高亮 | 拖拽固定 | 点击节点/连线询问AI
    </div>
  </div>
</template>


<script setup>
import { onMounted, ref, watch, onUnmounted } from 'vue';
import * as d3 from 'd3';
import { useGraphStore } from '../stores/graphStore';
import { useChatStore } from '../stores/chatStore';
import NodeDetail from './NodeDetail.vue';

const graphStore = useGraphStore();
const chatStore = useChatStore();
const container = ref(null);
const svgRef = ref(null);

// Interactive state
const hiddenGroups = ref(new Set());
const hoverNode = ref(null);
let zoomBehavior = null;
let svgSelection = null; // Store d3 selection

let simulation = null;
let width = 0;
let height = 0;

// Google/Gemini inspired palette
const colors = [
  "#4285F4", // Blue
  "#34A853", // Green
  "#EA4335", // Red
  "#FBBC05", // Yellow
  "#AB47BC", // Purple
  "#00ACC1", // Cyan
  "#FF7043", // Orange
  "#9E9D24"  // Olive
];

const colorScale = d3.scaleOrdinal(colors);

function toggleGroup(group) {
  if (hiddenGroups.value.has(group)) {
    hiddenGroups.value.delete(group);
  } else {
    hiddenGroups.value.add(group);
  }
  updateGraphVisibility();
}

function resetZoom() {
  if (svgSelection && zoomBehavior) {
    svgSelection.transition().duration(750).call(zoomBehavior.transform, d3.zoomIdentity);
  }
}

onMounted(() => {
  // Initial size
  updateDimensions();
  window.addEventListener('resize', handleResize);
  
  if (graphStore.nodes.length > 0) {
    initGraph();
  }
});

onUnmounted(() => {
  window.removeEventListener('resize', handleResize);
  if (simulation) simulation.stop();
});

watch(() => graphStore.nodes, (newNodes) => {
  if (newNodes.length > 0) {
    initGraph();
  }
}, { deep: true });

function updateDimensions() {
  if (container.value) {
    width = container.value.clientWidth;
    height = container.value.clientHeight;
  }
}

function handleResize() {
  updateDimensions();
  if (svgRef.value) {
    d3.select(svgRef.value)
      .attr("width", width)
      .attr("height", height);
    
    if (simulation) {
      simulation.force("center", d3.forceCenter(width / 2, height / 2));
      simulation.alpha(1).restart();
    }
  }
}

function initGraph() {
  if (!svgRef.value) return;
  
  // Clear previous
  const svg = d3.select(svgRef.value);
  svg.selectAll("*").remove();
  svgSelection = svg; // Store for resetZoom
  
  svg.attr("width", width).attr("height", height);
  
  // Add zoom group
  const g = svg.append("g");
  
  zoomBehavior = d3.zoom()
      .extent([[0, 0], [width, height]])
      .scaleExtent([0.1, 8])
      .on("zoom", ({transform}) => {
        g.attr("transform", transform);
      });
      
  svg.call(zoomBehavior);

  const nodes = graphStore.nodes.map(d => ({...d}));
  const links = graphStore.links.map(d => ({...d}));

  // Neighbor index for fast lookup
  const linkedByIndex = {};
  links.forEach(d => {
    // Note: before simulation, source/target are just ids if we used map above? 
    // Wait, d3 force will mutate these. 
    // We can rely on id strings if structure matches
    linkedByIndex[`${d.source},${d.target}`] = 1;
    linkedByIndex[`${d.target},${d.source}`] = 1;
  });

  function isConnected(a, b) {
    return linkedByIndex[`${a.id},${b.id}`] || linkedByIndex[`${b.id},${a.id}`] || a.id === b.id;
  }

  simulation = d3.forceSimulation(nodes)
    .force("link", d3.forceLink(links).id(d => d.id).distance(100)) // Reduced distance for tighter clusters
    .force("charge", d3.forceManyBody().strength(-300))
    .force("center", d3.forceCenter(width / 2, height / 2))
    .force("collide", d3.forceCollide().radius(d => d.val * 1.5 + 5).iterations(2));

  // Arrow marker
  svg.append("defs").selectAll("marker")
    .data(["end"])
    .enter().append("marker")
    .attr("id", "arrow")
    .attr("viewBox", "0 -5 10 10")
    .attr("refX", 15) // Adjust based on node size logic if needed
    .attr("refY", 0)
    .attr("markerWidth", 6)
    .attr("markerHeight", 6)
    .attr("orient", "auto")
    .append("path")
    .attr("d", "M0,-5L10,0L0,5")
    .attr("fill", "#999");

  // Edges
  const link = g.append("g")
    .attr("class", "links")
    .selectAll("line")
    .data(links)
    .join("line")
    .attr("stroke", "#dadce0")
    .attr("stroke-width", 2)
    .attr("stroke-opacity", 0.6)
    .attr("class", "link")
    .style("cursor", "pointer")
    .on("click", (event, d) => {
      // 点击边，选择并询问关系
      graphStore.selectEdge(d);
      chatStore.askAboutEdge(d);
      event.stopPropagation();
    })
    .on("mouseover", function(event, d) {
      d3.select(this)
        .attr("stroke", "#4285F4")
        .attr("stroke-width", 4);
    })
    .on("mouseout", function(event, d) {
      d3.select(this)
        .attr("stroke", "#dadce0")
        .attr("stroke-width", 2);
    });

  // Nodes
  const node = g.append("g")
    .attr("class", "nodes")
    .selectAll("g") // Use group for circle+text
    .data(nodes)
    .join("g")
    .attr("class", "node")
    .call(d3.drag()
        .on("start", dragstarted)
        .on("drag", dragged)
        .on("end", dragended));

  // Circle
  node.append("circle")
    .attr("r", d => d.val * 1.2 + 5)
    .attr("fill", d => colorScale(d.group))
    .attr("stroke", "#fff")
    .attr("stroke-width", 2)
    .style("cursor", "pointer")
    .on("click", (event, d) => {
      // Don't trigger if dragging
      graphStore.selectNode(d);
      chatStore.askAboutNode(d);
      event.stopPropagation();
    })
    .on("mouseover", (event, d) => {
      hoverNode.value = d;
      updateGraphVisibility();
    })
    .on("mouseout", () => {
      hoverNode.value = null;
      updateGraphVisibility();
    });

  // Labels
  node.append("text")
    .text(d => d.id)
    .attr("font-size", d => Math.max(10, d.val) + "px")
    .attr("fill", "#202124")
    .attr("dx", d => d.val + 12)
    .attr("dy", 4)
    .style("pointer-events", "none")
    .style("text-shadow", "0 1px 2px rgba(255,255,255,0.8)")
    .style("font-weight", "500");

  simulation.on("tick", () => {
    link
        .attr("x1", d => d.source.x)
        .attr("y1", d => d.source.y)
        .attr("x2", d => d.target.x)
        .attr("y2", d => d.target.y);

    node
        .attr("transform", d => `translate(${d.x},${d.y})`);
  });

  function dragstarted(event, d) {
    if (!event.active) simulation.alphaTarget(0.3).restart();
    d.fx = d.x;
    d.fy = d.y;
  }

  function dragged(event, d) {
    d.fx = event.x;
    d.fy = event.y;
  }

  function dragended(event, d) {
    if (!event.active) simulation.alphaTarget(0);
    // d.fx = null; // Comment out to allow "sticky" nodes - one of the interactive features
    // d.fy = null;
    
    // Check if user wants to release? Maybe single click releases?
    // For now keep sticky behavior as it's useful for organizing
  }

  // Update function for visibility
  window.updateGraphVisibility = () => {
    const isHovering = hoverNode.value !== null;
    const hidden = hiddenGroups.value;

    node.transition().duration(200).style('opacity', d => {
      if (hidden.has(d.group)) return 0.1;
      if (isHovering && !isConnected(d, hoverNode.value)) return 0.1;
      return 1;
    });

    link.transition().duration(200).style('stroke-opacity', d => {
       const sourceHidden = hidden.has(d.source.group);
       const targetHidden = hidden.has(d.target.group);
       if (sourceHidden || targetHidden) return 0.05;

       if (isHovering) {
         return (d.source.id === hoverNode.value.id || d.target.id === hoverNode.value.id) ? 0.8 : 0.05;
       }
       return 0.6;
    });
    
    node.selectAll("circle")
      .attr("stroke", d => (isHovering && d.id === hoverNode.value.id) ? "#000" : "#fff")
      .attr("stroke-width", d => (isHovering && d.id === hoverNode.value.id) ? 3 : 2);
  };
}

// Helper access for the updateGraphVisibility which needs to be called from toggleGroup & watchers
function updateGraphVisibility() {
  if (window.updateGraphVisibility) window.updateGraphVisibility();
}
</script>

<style scoped>
.graph-container {
  width: 100%;
  height: 100%;
  position: relative;
  background: var(--color-surface);
  border-radius: var(--radius-lg);
  overflow: hidden;
  box-shadow: inset 0 0 20px rgba(0,0,0,0.02);
}

.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255,255,255,0.8);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  z-index: 10;
  backdrop-filter: blur(4px);
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid var(--color-primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 16px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.legend {
  position: absolute;
  bottom: 20px;
  left: 20px;
  background: rgba(255, 255, 255, 0.9);
  padding: 12px;
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-sm);
  backdrop-filter: blur(4px);
  border: 1px solid var(--color-border);
  max-height: 200px;
  overflow-y: auto;
}

.legend-title {
  font-size: 11px;
  font-weight: 600;
  color: var(--color-text-tertiary);
  margin-bottom: 8px;
  text-transform: uppercase;
}

.legend-item {
  display: flex;
  align-items: center;
  margin-bottom: 6px;
  font-size: 13px;
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: opacity 0.2s;
  user-select: none;
}

.legend-item:hover {
  opacity: 0.8;
}

.legend-item.inactive {
  opacity: 0.4;
  text-decoration: line-through;
}

.graph-controls {
  position: absolute;
  top: 20px;
  left: 20px;
  z-index: 5;
  display: flex;
  gap: 8px;
}

.control-btn {
  background: white;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  box-shadow: var(--shadow-sm);
  transition: all 0.2s;
}

.control-btn:hover {
  background: var(--color-bg-secondary);
  transform: translateY(-1px);
}

.control-btn span {
  font-size: 18px;
  line-height: 1;
}

.graph-hint {
  position: absolute;
  bottom: 20px;
  right: 20px;
  font-size: 12px;
  color: var(--color-text-tertiary);
  background: rgba(255,255,255,0.8);
  padding: 4px 8px;
  border-radius: 4px;
  pointer-events: none;
}

.dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  margin-right: 8px;
}
</style>
