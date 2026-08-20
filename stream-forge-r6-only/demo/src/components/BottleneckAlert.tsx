import React from "react";
import { TopologyNode } from "../types/streamforge";
import { AlertTriangle } from "lucide-react";

interface BottleneckAlertProps {
  bottlenecks: TopologyNode[];
}

export const BottleneckAlert: React.FC<BottleneckAlertProps> = ({ bottlenecks }) => {
  if (bottlenecks.length === 0) return null;

  return (
    <div className="p-4 rounded-xl border border-amber-500/30 bg-amber-500/10 flex items-center gap-3">
      <AlertTriangle className="w-6 h-6 text-amber-500" />
      <div>
        <p className="font-medium text-amber-300">
          Bottleneck Detected: {bottlenecks.map(n => n.label).join(", ")}
        </p>
        <p className="text-sm text-amber-200/70">
          These workers are experiencing high resource usage and may impact overall throughput
        </p>
      </div>
    </div>
  );
};