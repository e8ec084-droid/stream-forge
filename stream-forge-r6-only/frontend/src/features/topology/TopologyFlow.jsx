import React, { useMemo } from "react";
import { Background, Controls, MiniMap, ReactFlow } from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import TopologyNode from "./TopologyNode";

const nodeTypes = { topologyNode: TopologyNode };

function buildGraph(nodes = [], edges = [], animated = false) {
  return {
    nodes: nodes.map((node, index) => ({
      id: node.id,
      type: "topologyNode",
      position: { x: 80 + index * 220, y: 120 },
      data: node
    })),
    edges: edges.map((edge, index) => ({
      id: `edge-${index}`,
      source: edge.source,
      target: edge.target,
      animated,
      style: {
        strokeWidth: 2,
        stroke: animated ? "#60a5fa" : "#64748b"
      }
    }))
  };
}

export default function TopologyFlow({ nodes, edges, animated = false }) {
  const graph = useMemo(() => buildGraph(nodes, edges, animated), [nodes, edges, animated]);

  return (
    <div className="flow-panel">
      <ReactFlow nodes={graph.nodes} edges={graph.edges} nodeTypes={nodeTypes} fitView>
        <MiniMap />
        <Controls />
        <Background gap={24} size={1} />
      </ReactFlow>
    </div>
  );
}
