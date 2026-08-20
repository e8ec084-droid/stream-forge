import React from "react";
import { TopologyNode, ThroughputPoint } from "../types/streamforge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Activity, Cpu, MemoryStick, Timer, Database, ArrowUpDown } from "lucide-react";

interface MetricsPanelProps {
  throughput: number;
  history: ThroughputPoint[];
  nodes: TopologyNode[];
}

export const MetricsPanel: React.FC<MetricsPanelProps> = ({ throughput, history, nodes }) => {
  const avgLatency = nodes
    .filter(n => n.metrics)
    .reduce((sum, n) => sum + (n.metrics?.latency || 0), 0) / 
    nodes.filter(n => n.metrics).length;

  const totalBacklog = nodes
    .filter(n => n.metrics)
    .reduce((sum, n) => sum + (n.metrics?.backlog || 0), 0);

  const avgCpu = nodes
    .filter(n => n.metrics)
    .reduce((sum, n) => sum + (n.metrics?.cpu || 0), 0) / 
    nodes.filter(n => n.metrics).length;

  const max = Math.max(...history.map(h => h.value));
  const min = Math.min(...history.map(h => h.value));
  const range = max - min || 1;

  const metrics = [
    {
      label: "Throughput",
      value: throughput.toLocaleString(),
      unit: "msg/s",
      icon: Activity,
      color: "text-cyan-400",
      bg: "bg-cyan-500/10",
    },
    {
      label: "Avg Latency",
      value: avgLatency.toFixed(1),
      unit: "ms",
      icon: Timer,
      color: "text-green-400",
      bg: "bg-green-500/10",
    },
    {
      label: "Avg CPU",
      value: avgCpu.toFixed(1),
      unit: "%",
      icon: Cpu,
      color: "text-amber-400",
      bg: "bg-amber-500/10",
    },
    {
      label: "Total Backlog",
      value: Math.round(totalBacklog).toLocaleString(),
      unit: "msgs",
      icon: Database,
      color: "text-rose-400",
      bg: "bg-rose-500/10",
    },
  ];

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {metrics.map((metric) => {
          const Icon = metric.icon;
          return (
            <Card key={metric.label} className="bg-slate-900 border-slate-800">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-slate-400">{metric.label}</p>
                    <p className={`text-3xl font-bold mt-2 ${metric.color}`}>
                      {metric.value}
                      <span className="text-sm font-normal text-slate-400 ml-1">{metric.unit}</span>
                    </p>
                  </div>
                  <div className={`w-12 h-12 rounded-xl ${metric.bg} flex items-center justify-center`}>
                    <Icon className={`w-6 h-6 ${metric.color}`} />
                  </div>
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>

      <Card className="bg-slate-900 border-slate-800">
        <CardHeader>
          <CardTitle className="text-lg font-semibold text-white flex items-center gap-2">
            <ArrowUpDown className="w-5 h-5 text-cyan-400" />
            Throughput History
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-end h-48 gap-1">
            {history.map((point, i) => {
              const height = ((point.value - min) / range) * 100;
              const color = point.value > max * 0.8 ? "bg-rose-500" : 
                           point.value > max * 0.6 ? "bg-amber-500" : "bg-cyan-500";
              return (
                <div
                  key={i}
                  className={`flex-1 rounded-t ${color} transition-all duration-500`}
                  style={{ height: `${height}%` }}
                  title={`${point.timestamp}: ${point.value} msg/s`}
                />
              );
            })}
          </div>
          <div className="flex justify-between mt-2 text-xs text-slate-500">
            <span>{history[0]?.timestamp}</span>
            <span>{history[history.length - 1]?.timestamp}</span>
          </div>
        </CardContent>
      </Card>

      <Card className="bg-slate-900 border-slate-800">
        <CardHeader>
          <CardTitle className="text-lg font-semibold text-white">Worker Metrics</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {nodes.filter(n => n.metrics).map((node) => (
              <div key={node.id} className="p-4 bg-slate-800/50 rounded-lg">
                <div className="flex items-center justify-between mb-3">
                  <span className="font-medium text-sm">{node.label}</span>
                  <Badge variant={node.status === "healthy" ? "default" : "destructive"}>
                    {node.status}
                  </Badge>
                </div>
                <div className="space-y-2">
                  <div>
                    <div className="flex justify-between text-xs mb-1">
                      <span className="text-slate-400">CPU</span>
                      <span>{node.metrics?.cpu.toFixed(1)}%</span>
                    </div>
                    <div className="w-full h-1.5 bg-slate-700 rounded-full overflow-hidden">
                      <div
                        className={`h-full rounded-full ${
                          (node.metrics?.cpu || 0) > 80 ? "bg-rose-500" : 
                          (node.metrics?.cpu || 0) > 60 ? "bg-amber-500" : "bg-green-500"
                        }`}
                        style={{ width: `${node.metrics?.cpu}%` }}
                      />
                    </div>
                  </div>
                  <div>
                    <div className="flex justify-between text-xs mb-1">
                      <span className="text-slate-400">Memory</span>
                      <span>{node.metrics?.memory.toFixed(1)}%</span>
                    </div>
                    <div className="w-full h-1.5 bg-slate-700 rounded-full overflow-hidden">
                      <div
                        className={`h-full rounded-full ${
                          (node.metrics?.memory || 0) > 80 ? "bg-rose-500" : 
                          (node.metrics?.memory || 0) > 60 ? "bg-amber-500" : "bg-green-500"
                        }`}
                        style={{ width: `${node.metrics?.memory}%` }}
                      />
                    </div>
                  </div>
                  <div className="flex justify-between text-xs">
                    <span className="text-slate-400">Rate</span>
                    <span>{node.metrics?.processingRate.toFixed(0)} msg/s</span>
                  </div>
                  <div className="flex justify-between text-xs">
                    <span className="text-slate-400">Latency</span>
                    <span>{node.metrics?.latency.toFixed(1)}ms</span>
                  </div>
                  <div className="flex justify-between text-xs">
                    <span className="text-slate-400">Backlog</span>
                    <span>{Math.round(node.metrics?.backlog || 0)}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};