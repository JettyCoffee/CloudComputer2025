<template>
  <div ref="container" class="graph-container">
    <div v-if="graphStore.loading" class="loading-overlay">
      <div class="spinner"></div>
      <p>正在构建知识图谱...</p>
    </div>
    <svg ref="svgRef"></svg>
    
    <NodeDetail />

    <!-- Legend -->
    <div class="legend" v-if="graphStore.disciplines.length > 0">
      <div v-for="disc in graphStore.disciplines" :key="disc" class="legend-item">
        <span class="dot" :style="{ backgroundColor: colorScale(disc) }"></span>
        <span>{{ disc }}</span>
      </div>
    </div>
  </div>
</template>


<script setup>
import { onMounted, ref, watch, onUnmounted } from 'vue';
import * as d3 from 'd3';
import { useGraphStore } from '../stores/graphStore';
import NodeDetail from './NodeDetail.vue';

const graphStore = useGraphStore();
const container = ref(null);
const svgRef = ref(null);

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
  
  svg.attr("width", width).attr("height", height);
  
  // Add zoom group
  const g = svg.append("g");
  
  svg.call(d3.zoom()
      .extent([[0, 0], [width, height]])
      .scaleExtent([0.1, 4])
      .on("zoom", ({transform}) => {
        g.attr("transform", transform);
      }));

  const nodes = graphStore.nodes.map(d => ({...d}));
  const links = graphStore.links.map(d => ({...d}));

  simulation = d3.forceSimulation(nodes)
    .force("link", d3.forceLink(links).id(d => d.id).distance(120))
    .force("charge", d3.forceManyBody().strength(-400))
    .force("center", d3.forceCenter(width / 2, height / 2))
    .force("collide", d3.forceCollide().radius(d => d.val * 1.5 + 5));

  // Edges
  const link = g.append("g")
    .attr("class", "links")
    .selectAll("line")
    .data(links)
    .join("line")
    .attr("stroke", "#dadce0")
    .attr("stroke-width", 1.5)
    .attr("stroke-opacity", 0.6);

  // Nodes
  const node = g.append("g")
    .attr("class", "nodes")
    .selectAll("circle")
    .data(nodes)
    .join("circle")
    .attr("r", d => d.val * 1.2 + 5)
    .attr("fill", d => colorScale(d.group))
    .attr("stroke", "#fff")
    .attr("stroke-width", 2)
    .style("cursor", "pointer")
    .on("click", (event, d) => {
      graphStore.selectNode(d);
      // Optional: trigger chat if needed
    })
    .call(d3.drag()
        .on("start", dragstarted)
        .on("drag", dragged)
        .on("end", dragended));

  // Labels
  const label = g.append("g")
    .attr("class", "labels")
    .selectAll("text")
    .data(nodes)
    .join("text")
    .text(d => d.id)
    .attr("font-size", d => Math.max(10, d.val) + "px")
    .attr("fill", "#202124")
    .attr("dx", d => d.val + 8)
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
        .attr("cx", d => d.x)
        .attr("cy", d => d.y);
        
    label
        .attr("x", d => d.x)
        .attr("y", d => d.y);
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
    d.fx = null;
    d.fy = null;
  }
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
}

.legend-item {
  display: flex;
  align-items: center;
  margin-bottom: 4px;
  font-size: 12px;
  color: var(--color-text-secondary);
}

.legend-item:last-child {
  margin-bottom: 0;
}

.dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  margin-right: 8px;
}
</style>
