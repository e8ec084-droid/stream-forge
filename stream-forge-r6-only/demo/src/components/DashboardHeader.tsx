import { Activity, Cpu, Database, Radio, Shield, Zap } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import type { TopologyData, MetricsData } from "@/types/topology";

interface DashboardHeaderProps {
  topology: TopologyData | null;
  metrics: MetricsData | null;
  selectedNode: string | null;
}

export function DashboardHeader({
  topology,
  metrics,
  selectedNode,
}: DashboardHeaderProps) {
  const healthyNodes = topology?.nodes.filter(
    (n) => n.status === "healthy"
  ).length;
  const totalNodes = topology?.nodes.length ?? 0;
  const selectedNodeData = topology?.nodes.find(
    (n) => n.id === selectedNode
  );

  return (
    <header className="border-b border-slate-800 bg-slate-900/50 backdrop-blur">
      <div className="flex items-center justify-between px-6 py-4">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-cyan-500 to-blue-600 shadow-lg shadow-cyan-500/20">
            <Zap className="h-5 w-5 text-white" />
          </div>
          <div>
            <h1 className="font-serif text-xl font-bold tracking-tight text-white">
              StreamForge
            </h1>
            <p className="text-xs text-slate-400">
              Distributed Python Event Processor
            </p>
          </div>
        </div>

        <div className="flex items-center gap-6">
          <div className="flex items-center gap-2">
            <Radio className="h-4 w-4 text-cyan-400" />
            <span className="text-sm font-medium text-slate-300">
              Kafka Cluster
            </span>
            <Badge
              variant="outline"
              className="border-cyan-500/30 bg-cyan-500/10 text-cyan-400"
            >
              Connected
            </Badge>
          </div>

          <div className="flex items-center gap-2">
            <Cpu className="h-4 w-4 text-emerald-400" />
            <span className="text-sm font-medium text-slate-300">
              Workers
            </span>
            <Badge
              variant="outline"
              className="border-emerald-500/30 bg-emerald-500/10 text-emerald-400"
            >
              {healthyNodes}/{totalNodes} Healthy
            </Badge>
          </div>

          <div className="flex items-center gap-2">
            <Database className="h-4 w-4 text-amber-400" />
            <span className="text-sm font-medium text-slate-300">
              Throughput
            </span>
            <span className="font-mono text-sm text-amber-400">
              {metrics?.throughput.toLocaleString() ?? "0"} msg/s
            </span>
          </div>

          <div className="flex items-center gap-2">
            <Shield className="h-4 w-4 text-rose-400" />
            <span className="text-sm font-medium text-slate-300">
              Exactly-Once
            </span>
            <Badge
              variant="outline"
              className="border-rose-500/30 bg-rose-500/10 text-rose-400"
            >
              Enabled
            </Badge>
          </div>

          {selectedNodeData && (
            <div className="flex items-center gap-2 rounded-lg border border-slate-700 bg-slate-800/50 px-3 py-1.5">
              <Activity className="h-4 w-4 text-cyan-400" />
              <span className="text-sm text-slate-300">
                {selectedNodeData.label}
              </span>
              <Badge
                variant="outline"
                className={
                  selectedNodeData.status === "healthy"
                    ? "border-emerald-500/30 bg-emerald-500/10 text-emerald-400"
                    : selectedNodeData.status === "degraded"
                    ? "border-amber-500/30 bg-amber-500/10 text-amber-400"
                    : "border-rose-500/30 bg-rose-500/10 text-rose-400"
                }
              >
                {selectedNodeData.status}
              </Badge>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}