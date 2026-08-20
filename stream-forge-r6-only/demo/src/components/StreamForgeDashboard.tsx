import React, { useState } from "react";
import { useStreamForge } from "../context/StreamForgeContext";
import { TopologyCanvas } from "./TopologyCanvas";
import { MetricsPanel } from "./MetricsPanel";
import { AuditPanel } from "./AuditPanel";
import { PartitionPanel } from "./PartitionPanel";
import { TelemetryPanel } from "./TelemetryPanel";
import { Header } from "./Header";
import { BottleneckAlert } from "./BottleneckAlert";

export const StreamForgeDashboard: React.FC = () => {
  const { data, refresh, simulateFailure, simulateRecovery, isSimulationMode } = useStreamForge();
  const [activeView, setActiveView] = useState<"topology" | "metrics" | "audit" | "partitions" | "telemetry">("topology");

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      <Header 
        health={data.health}
        throughput={data.throughput}
        isSimulationMode={isSimulationMode}
        onRefresh={refresh}
        activeView={activeView}
        onViewChange={setActiveView}
      />
      
      <main className="p-6 space-y-6">
        <BottleneckAlert bottlenecks={data.bottlenecks} />
        
        {activeView === "topology" && (
          <TopologyCanvas 
            nodes={data.nodes}
            edges={data.edges}
            onNodeClick={(nodeId) => console.log(`Selected node: ${nodeId}`)}
            onSimulateFailure={simulateFailure}
            onSimulateRecovery={simulateRecovery}
          />
        )}
        
        {activeView === "metrics" && (
          <MetricsPanel 
            throughput={data.throughput}
            history={data.history}
            nodes={data.nodes}
          />
        )}
        
        {activeView === "audit" && (
          <AuditPanel events={data.auditEvents} />
        )}
        
        {activeView === "partitions" && (
          <PartitionPanel partitions={data.partitions} />
        )}
        
        {activeView === "telemetry" && (
          <TelemetryPanel nodes={data.nodes} />
        )}
      </main>
    </div>
  );
};