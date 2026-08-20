import React from "react";
import { ClusterHealth } from "../types/streamforge";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { RefreshCw, Radio, Activity, ListTree, Database, Gauge } from "lucide-react";

interface HeaderProps {
  health: ClusterHealth;
  throughput: number;
  isSimulationMode: boolean;
  onRefresh: () => void;
  activeView: string;
  onViewChange: (view: "topology" | "metrics" | "audit" | "partitions" | "telemetry") => void;
}

export const Header: React.FC<HeaderProps> = ({
  health,
  throughput,
  isSimulationMode,
  onRefresh,
  activeView,
  onViewChange,
}) => {
  const views = [
    { id: "topology", label: "Topology", icon: Radio },
    { id: "metrics", label: "Metrics", icon: Activity },
    { id: "audit", label: "Audit", icon: ListTree },
    { id: "partitions", label: "Partitions", icon: Database },
    { id: "telemetry", label: "Telemetry", icon: Gauge },
  ] as const;

  return (
    <header className="bg-slate-900 border-b border-slate-800 px-6 py-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center">
            <Radio className="w-5 h-5 text-white" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-white">StreamForge Dashboard</h1>
            <p className="text-sm text-slate-400">Distributed Python Event Processor</p>
          </div>
          {isSimulationMode && (
            <Badge variant="secondary" className="bg-purple-500/20 text-purple-300 border-purple-500/30">
              Simulation Mode
            </Badge>
          )}
        </div>

        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-green-500" />
            <span className="text-sm text-slate-300">{health.healthy}/{health.total} Healthy</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-amber-500" />
            <span className="text-sm text-slate-300">{health.degraded} Degraded</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-rose-500" />
            <span className="text-sm text-slate-300">{health.failed} Failed</span>
          </div>
          <div className="px-4 py-2 bg-slate-800 rounded-lg">
            <span className="text-sm text-slate-400">Throughput: </span>
            <span className="text-lg font-bold text-cyan-400">{throughput.toLocaleString()}</span>
            <span className="text-sm text-slate-400"> msg/s</span>
          </div>
          <Button onClick={onRefresh} variant="outline" size="sm">
            <RefreshCw className="w-4 h-4 mr-2" />
            Refresh
          </Button>
        </div>
      </div>

      <nav className="flex gap-2 mt-4">
        {views.map((view) => {
          const Icon = view.icon;
          return (
            <Button
              key={view.id}
              variant={activeView === view.id ? "default" : "ghost"}
              size="sm"
              onClick={() => onViewChange(view.id)}
              className={activeView === view.id ? "bg-cyan-600 hover:bg-cyan-700" : ""}
            >
              <Icon className="w-4 h-4 mr-2" />
              {view.label}
            </Button>
          );
        })}
      </nav>
    </header>
  );
};