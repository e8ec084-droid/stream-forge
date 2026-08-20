import React from "react";
import { PartitionInfo } from "../types/streamforge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { CheckCircle, RefreshCw, XCircle } from "lucide-react";

interface PartitionPanelProps {
  partitions: PartitionInfo[];
}

export const PartitionPanel: React.FC<PartitionPanelProps> = ({ partitions }) => {
  const active = partitions.filter(p => p.status === "active").length;
  const rebalancing = partitions.filter(p => p.status === "rebalancing").length;
  const stalled = partitions.filter(p => p.status === "stalled").length;

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "active":
        return <CheckCircle className="w-3 h-3 text-green-500" />;
      case "rebalancing":
        return <RefreshCw className="w-3 h-3 text-blue-500 animate-spin" />;
      default:
        return <XCircle className="w-3 h-3 text-rose-500" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "active":
        return "border-green-500/30 bg-green-500/5";
      case "rebalancing":
        return "border-blue-500/30 bg-blue-500/5";
      default:
        return "border-rose-500/30 bg-rose-500/5";
    }
  };

  return (
    <Card className="bg-slate-900 border-slate-800">
      <CardHeader>
        <CardTitle className="text-lg font-semibold text-white">Partition Distribution</CardTitle>
        <div className="flex gap-4 mt-2">
          <span className="text-sm text-green-400">Active: {active}</span>
          <span className="text-sm text-blue-400">Rebalancing: {rebalancing}</span>
          <span className="text-sm text-rose-400">Stalled: {stalled}</span>
        </div>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 xl:grid-cols-8 gap-2">
          {partitions.map((partition) => (
            <div
              key={partition.id}
              className={`p-3 rounded-lg border ${getStatusColor(partition.status)}`}
              title={`Partition ${partition.id} - Worker: ${partition.workerId} - Lag: ${Math.round(partition.lag)}`}
            >
              <div className="flex items-center justify-between">
                <span className="text-xs font-mono font-semibold">P{partition.id}</span>
                {getStatusIcon(partition.status)}
              </div>
              <div className="text-xs text-slate-400 mt-1 truncate">{partition.workerId}</div>
              <div className="text-xs text-slate-500 mt-1">Lag: {Math.round(partition.lag)}</div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
};