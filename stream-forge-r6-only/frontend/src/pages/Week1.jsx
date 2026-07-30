import React, { useEffect, useMemo, useState } from "react";
import { ReactFlow, Background, Controls, MiniMap } from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import { getWeek1Data } from "../api";
import TopologyNode from "../components/TopologyNode";

const nodeTypes = { topologyNode: TopologyNode };

function buildGraph(data) {
  const nodes = data.nodes.map((node, index) => ({
    id: node.id,
    type: "topologyNode",
    position: { x: 80 + index * 220, y: 140 },
    data: node
  }));

  const edges = data.edges.map(([source, target], index) => ({
    id: `edge-${index}`,
    source,
    target,
    style: { strokeWidth: 2 }
  }));

  return { nodes, edges };
}

export default function Week1() {
  const [data, setData] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    getWeek1Data().then(setData).catch((err) => setError(err.message));
  }, []);

  const graph = useMemo(() => {
    if (!data) return { nodes: [], edges: [] };
    return buildGraph(data);
  }, [data]);

  return (
    <section>
      <div className="section-header">
        <h2>Week 1 - Topology UI Scaffold</h2>
        <p>React Flow setup, topology canvas skeleton, placeholder DAG nodes, mock API integration, and baseline theme.</p>
      </div>

      {error && <div className="error-box">{error}</div>}

      <div className="flow-panel">
        <ReactFlow nodes={graph.nodes} edges={graph.edges} nodeTypes={nodeTypes} fitView>
          <MiniMap />
          <Controls />
          <Background gap={24} size={1} />
        </ReactFlow>
      </div>
    </section>
  );
}
