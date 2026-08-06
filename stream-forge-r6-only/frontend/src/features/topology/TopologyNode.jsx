import React from "react";
import { Handle, Position } from "@xyflow/react";

const statusColorMap = {
  healthy: "#22c55e",
  warning: "#f59e0b",
  critical: "#ef4444"
};

export default function TopologyNode({ data }) {
  return (
    <div className="node-card">
      <Handle type="target" position={Position.Left} />
      <div className="node-title">
        <span
          className="status-dot"
          style={{ backgroundColor: statusColorMap[data.status] || "#94a3b8" }}
        />
        <strong>{data.label}</strong>
      </div>
      <div className="node-meta">Status: {data.status}</div>
      <div className="node-meta">Type: {data.type}</div>
      <Handle type="source" position={Position.Right} />
    </div>
  );
}
