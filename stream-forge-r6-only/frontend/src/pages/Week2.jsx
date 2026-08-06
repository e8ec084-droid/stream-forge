import React, { useEffect, useMemo, useState } from "react";
import { ReactFlow, Background, Controls, MiniMap } from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import { getWeek2Data } from "../api";
import TopologyNode from "../components/TopologyNode";
import MetricCard from "../components/MetricCard";
import WorkerPanel from "../components/WorkerPanel";

const nodeTypes = { topologyNode: TopologyNode };

function buildGraph(data) {
  const nodes = data.nodes.map((node, index) => ({
    id: node.id,
    type: "topologyNode",
    position: { x: 80 + index * 220, y: 120 },
    data: node
  }));

  const edges = data.edges.map(([source, target], index) => ({
    id: `edge-${index}`,
    source,
    target,
    animated: true,
    style: { strokeWidth: 2, stroke: "#60a5fa" }
  }));

  return { nodes, edges };
}

export default function Week2() {
  const [data, setData] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    getWeek2Data().then(setData).catch((err) => setError(err.message));
  }, []);

  const graph = useMemo(() => {
    if (!data) return { nodes: [], edges: [] };
    return buildGraph(data);
  }, [data]);

  return (
    <section>
      <div className="section-header">
        <h2>Week 2 - Live DAG Visualization</h2>
        <p>Live topology binding, node status indicators, FastAPI metrics stub, polished DAG edges, and dashboard usability improvements.</p>
      </div>

      {error && <div className="error-box">{error}</div>}

      <div className="summary-grid">
        <MetricCard title="Throughput" value={`${data?.metrics?.throughput ?? "--"} eps`} />
        <MetricCard title="Target" value={`${data?.metrics?.target ?? "--"} eps`} />
        <MetricCard title="Active Partitions" value={data?.metrics?.active_partitions ?? "--"} />
      </div>

      <div className="content-grid">
        <div className="flow-panel">
          <ReactFlow nodes={graph.nodes} edges={graph.edges} nodeTypes={nodeTypes} fitView>
            <MiniMap />
            <Controls />
            <Background gap={24} size={1} />
          </ReactFlow>
        </div>
        <WorkerPanel workers={data?.workers || []} />
      </div>
    </section>
  );
}
