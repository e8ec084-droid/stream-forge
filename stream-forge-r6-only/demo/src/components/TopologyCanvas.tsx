import React, { useCallback, useMemo } from "react";
import { TopologyNode, TopologyEdge } from "../types/streamforge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { AlertTriangle, CheckCircle, XCircle, RefreshCw, Zap } from "lucide-react";

interface TopologyCanvasProps {
  nodes: TopologyNode[];
  edges: TopologyEdge[];
  onNodeClick: (nodeId: string) => void;
  onSimulateFailure: (nodeId: string) => void;
  onSimulateRecovery: (nodeId: string) => void;
}

export const TopologyCanvas: React.FC<TopologyCanvasProps> = ({
  nodes,
  edges,
  onNodeClick,
  onSimulateFailure,
  onSimulateRecovery,
}) => {
  const sources = nodes.filter(n => n.type === "source");
  const processors = nodes.filter(n => n.type === "processor");
  const sinks = nodes.filter(n => n.type === "sink");

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "healthy":
        return <CheckCircle className="w-4 h-4 text-green-500" />;
      case "degraded":
        return <AlertTriangle className="w-4 h-4 text-amber-500" />;
      case "recovering":
        return <RefreshCw className="w-4 h-4 text-blue-500 animate-spin" />;
      default:
        return <XCircle className="w-4 h-4 text-rose-500" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "healthy":
        return "border-green-500/50 bg-green-500/10";
      case "degraded":
        return "border-amber-500/50 bg-amber-500/10";
      case "recovering":
        return "border-blue-500/50 bg-blue-500/10";
      default:
        return "border-rose-500/50 bg-rose-500/10";
    }
  };

  const renderNode = (node: TopologyNode) => (
    <div
      key={node.id}
      className={`p-4 rounded-xl border cursor-pointer transition-all hover:scale-105 ${getStatusColor(node.status)} ${
        node.isBottleneck ? "ring-2 ring-amber-500" : ""
      }`}
      onClick={() => onNodeClick(node.id)}
    >
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-2">
          {getStatusIcon(node.status)}
          <span className="font-semibold text-sm">{node.label}</span>
        </div>
        {node.isBottleneck && <Zap className="w-4 h-4 text-amber-500" />}
      </div>
      <div className="text-xs text-slate-400">
        {node.partitions} partitions
      </div>
      {node.metrics && (
        <div className="mt-2 space-y-1">
          <div className="flex justify-between text-xs">
            <span className="text-slate-400">CPU</span>
            <span className={node.metrics.cpu > 80 ? "text-rose-400" : "text-slate-300"}>
              {node.metrics.cpu.toFixed(1)}%
            </span>
          </div>
          <div className="w-full h-1.5 bg-slate-700 rounded-full overflow-hidden">
            <div
              className={`h-full rounded-full ${
                node.metrics.cpu > 80 ? "bg-rose-500" : node.metrics.cpu > 60 ? "bg-amber-500" : "bg-green-500"
              }`}
              style={{ width: `${node.metrics.cpu}%` }}
            />
          </div>
          <div className="flex justify-between text-xs">
            <span className="text-slate-400">Rate</span>
            <span className="text-slate-300">{node.metrics.processingRate.toFixed(0)} msg/s</span>
          </div>
          <div className="flex justify-between text-xs">
            <span className="text-slate-400">Latency</span>
            <span className="text-slate-300">{node.metrics.latency.toFixed(1)}ms</span>
          </div>
        </div>
      )}
      {node.type === "processor" && (
        <div className="flex gap-2 mt-3">
          <Button
            size="sm"
            variant="destructive"
            className="flex-1"
            onClick={(e) => {
              e.stopPropagation();
              onSimulateFailure(node.id);
            }}
          >
            Fail
          </Button>
          <Button
            size="sm"
            variant="outline"
            className="flex-1"
            onClick={(e) => {
              e.stopPropagation();
              onSimulateRecovery(node.id);
            }}
          >
            Recover
          </Button>
        </div>
      )}
    </div>
  );

  return (
    <Card className="bg-slate-900 border-slate-800">
      <CardHeader>
        <CardTitle className="text-lg font-semibold text-white">DAG Topology</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-8">
          <div>
            <h3 className="text-sm font-medium text-slate-400 mb-3">Sources</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {sources.map(renderNode)}
            </div>
          </div>

          <div>
            <h3 className="text-sm font-medium text-slate-400 mb-3">Processors</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 xl:grid-cols-5 gap-4">
              {processors.map(renderNode)}
            </div>
          </div>

          <div>
            <h3 className="text-sm font-medium text-slate-400 mb-3">Sinks</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {sinks.map(renderNode)}
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};