import React from "react";
import { TopologyNode } from "../types/streamforge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Cpu, MemoryStick, Database, Activity, Timer, AlertTriangle } from "lucide-react";

interface TelemetryPanelProps {
  nodes: TopologyNode[];
}

export const TelemetryPanel: React.FC<TelemetryPanelProps> = ({ nodes }) => {
  const workers = nodes.filter(n => n.type === "processor");

  return (
    <div className="space-y-6">
      <Card className="bg-slate-900 border-slate-800">
        <CardHeader>
          <CardTitle className="text-lg font-semibold text-white">Worker Health</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
            {workers.map((worker) => (
              <div
                key={worker.id}
                className={`p-4 rounded-lg border ${
                  worker.status === "healthy" ? "border-green-500/30 bg-green-500/5" :
                  worker.status === "degraded" ? "border-amber-500/30 bg-amber-500/5" :
                  worker.status === "recovering" ? "border-blue-500/30 bg-blue-500/5" :
                  "border-rose-500/30 bg-rose-500/5"
                }`}
              >
                <div className="flex items-center justify-between mb-3">
                  <div>
                    <span className="font-medium text-sm">{worker.label}</span>
                    {worker.isBottleneck && (
                      <AlertTriangle className="w-4 h-4 text-amber-500 inline ml-2" />
                    )}
                  </div>
                  <Badge variant={worker.status === "healthy" ? "default" : "destructive"}>
                    {worker.status}
                  </Badge>
                </div>
                {worker.metrics && (
                  <div className="space-y-3">
                    <div>
                      <div className="flex items-center justify-between text-xs mb-1">
                        <span className="flex items-center gap-1 text-slate-400">
                          <Cpu className="w-3 h-3" /> CPU
                        </span>
                        <span className={worker.metrics.cpu > 80 ? "text-rose-400" : "text-slate-300"}>
                          {worker.metrics.cpu.toFixed(1)}%
                        </span>
                      </div>
                      <div className="w-full h-2 bg-slate-700 rounded-full overflow-hidden">
                        <div
                          className={`h-full rounded-full transition-all duration-500 ${
                            worker.metrics.cpu > 80 ? "bg-rose-500" :
                            worker.metrics.cpu > 60 ? "bg-amber-500" : "bg-green-500"
                          }`}
                          style={{ width: `${worker.metrics.cpu}%` }}
                        />
                      </div>
                    </div>
                    <div>
                      <div className="flex items-center justify-between text-xs mb-1">
                        <span className="flex items-center gap-1 text-slate-400">
                          <MemoryStick className="w-3 h-3" /> Memory
                        </span>
                        <span className={worker.metrics.memory > 80 ? "text-rose-400" : "text-slate-300"}>
                          {worker.metrics.memory.toFixed(1)}%
                        </span>
                      </div>
                      <div className="w-full h-2 bg-slate-700 rounded-full overflow-hidden">
                        <div
                          className={`h-full rounded-full transition-all duration-500 ${
                            worker.metrics.memory > 80 ? "bg-rose-500" :
                            worker.metrics.memory > 60 ? "bg-amber-500" : "bg-green-500"
                          }`}
                          style={{ width: `${worker.metrics.memory}%` }}
                        />
                      </div>
                    </div>
                    <div className="grid grid-cols-2 gap-2 text-xs">
                      <div className="flex items-center gap-1 text-slate-400">
                        <Activity className="w-3 h-3" />
                        <span>{worker.metrics.processingRate.toFixed(0)} msg/s</span>
                      </div>
                      <div className="flex items-center gap-1 text-slate-400">
                        <Timer className="w-3 h-3" />
                        <span>{worker.metrics.latency.toFixed(1)}ms</span>
                      </div>
                      <div className="flex items-center gap-1 text-slate-400">
                        <Database className="w-3 h-3" />
                        <span>{Math.round(worker.metrics.backlog)} backlog</span>
                      </div>
                      <div className="text-slate-400">
                        {worker.partitions} partitions
                      </div>
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};