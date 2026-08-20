import React, { createContext, useContext, useState, useEffect, useCallback } from "react";
import { StreamForgeData, TopologyNode, TopologyEdge, AuditEvent, ThroughputPoint, PartitionInfo, ClusterHealth } from "../types/streamforge";

interface StreamForgeContextType {
  data: StreamForgeData;
  refresh: () => void;
  simulateFailure: (nodeId: string) => void;
  simulateRecovery: (nodeId: string) => void;
  isSimulationMode: boolean;
}

const StreamForgeContext = createContext<StreamForgeContextType | undefined>(undefined);

export const useStreamForge = () => {
  const context = useContext(StreamForgeContext);
  if (!context) {
    throw new Error("useStreamForge must be used within StreamForgeProvider");
  }
  return context;
};

export const StreamForgeProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [data, setData] = useState<StreamForgeData>(() => initializeMockData());
  const [isSimulationMode, setIsSimulationMode] = useState(true);

  useEffect(() => {
    const interval = setInterval(() => {
      setData(prev => updateMetrics(prev));
    }, 2000);
    return () => clearInterval(interval);
  }, []);

  const refresh = useCallback(() => {
    setData(prev => updateMetrics(prev));
  }, []);

  const simulateFailure = useCallback((nodeId: string) => {
    setData(prev => {
      const nodes = prev.nodes.map(node => 
        node.id === nodeId ? { ...node, status: "failed" as const } : node
      );
      const auditEvents = [
        ...prev.auditEvents,
        {
          id: `evt-${Date.now()}`,
          type: "error" as const,
          title: "Worker Failure",
          description: `Worker ${nodeId} has crashed, initiating partition rebalance`,
          timestamp: Date.now(),
          nodeId,
          severity: "critical" as const,
        },
      ];
      return { ...prev, nodes, auditEvents };
    });
  }, []);

  const simulateRecovery = useCallback((nodeId: string) => {
    setData(prev => {
      const nodes = prev.nodes.map(node => 
        node.id === nodeId ? { ...node, status: "recovering" as const } : node
      );
      const auditEvents = [
        ...prev.auditEvents,
        {
          id: `evt-${Date.now()}`,
          type: "recovery" as const,
          title: "Worker Recovery Started",
          description: `Worker ${nodeId} is recovering from changelog`,
          timestamp: Date.now(),
          nodeId,
          severity: "medium" as const,
        },
      ];
      return { ...prev, nodes, auditEvents };
    });

    setTimeout(() => {
      setData(prev => {
        const nodes = prev.nodes.map(node => 
          node.id === nodeId ? { ...node, status: "healthy" as const } : node
        );
        const auditEvents = [
          ...prev.auditEvents,
          {
            id: `evt-${Date.now()}`,
            type: "info" as const,
            title: "Worker Recovered",
            description: `Worker ${nodeId} has fully recovered`,
            timestamp: Date.now(),
            nodeId,
            severity: "low" as const,
          },
        ];
        return { ...prev, nodes, auditEvents };
      });
    }, 3000);
  }, []);

  return (
    <StreamForgeContext.Provider value={{ data, refresh, simulateFailure, simulateRecovery, isSimulationMode }}>
      {children}
    </StreamForgeContext.Provider>
  );
};

function initializeMockData(): StreamForgeData {
  const workerNames = Array.from({ length: 20 }, (_, i) => 
    `Worker-${String(i + 1).padStart(2, "0")}`
  );

  const nodes: TopologyNode[] = [
    {
      id: "kafka-ingest",
      label: "Kafka Ingest",
      type: "source",
      status: "healthy",
      partitions: 50,
      metrics: {
        cpu: 45,
        memory: 60,
        stateStore: 30,
        processingRate: 50000,
        latency: 2,
        backlog: 0,
        throughput: 50000,
      },
    },
    ...workerNames.map((name, i) => ({
      id: `worker-${String(i + 1).padStart(2, "0")}`,
      label: name,
      type: "processor" as const,
      status: "healthy" as const,
      partitions: Math.floor(1 + Math.random() * 3),
      isBottleneck: i === 3 || i === 7,
      metrics: {
        cpu: (i === 3 || i === 7) ? 85 + Math.random() * 10 : 30 + Math.random() * 40,
        memory: (i === 3 || i === 7) ? 80 + Math.random() * 10 : 40 + Math.random() * 30,
        stateStore: 20 + Math.random() * 50,
        processingRate: (i === 3 || i === 7) ? 1500 + Math.random() * 500 : 2000 + Math.random() * 3000,
        latency: (i === 3 || i === 7) ? 30 + Math.random() * 20 : 5 + Math.random() * 20,
        backlog: (i === 3 || i === 7) ? 5000 + Math.random() * 5000 : Math.random() * 1000,
        throughput: 2000 + Math.random() * 3000,
      },
    })),
    {
      id: "aggregate-sink",
      label: "Aggregate Sink",
      type: "sink",
      status: "healthy",
      partitions: 1,
      metrics: {
        cpu: 20,
        memory: 30,
        stateStore: 10,
        processingRate: 50000,
        latency: 1,
        backlog: 0,
        throughput: 50000,
      },
    },
  ];

  const edges: TopologyEdge[] = nodes
    .filter((n) => n.type === "processor")
    .flatMap((node) => [
      {
        id: `edge-kafka-${node.id}`,
        source: "kafka-ingest",
        target: node.id,
        status: "healthy" as const,
        throughput: node.metrics?.processingRate ?? 2000,
        isBottleneck: node.isBottleneck,
      },
      {
        id: `edge-${node.id}-sink`,
        source: node.id,
        target: "aggregate-sink",
        status: "healthy" as const,
        throughput: node.metrics?.processingRate ?? 2000,
        isBottleneck: node.isBottleneck,
      },
    ]);

  const partitions: PartitionInfo[] = Array.from({ length: 50 }, (_, i) => ({
    id: i,
    workerId: `worker-${String((i % 20) + 1).padStart(2, "0")}`,
    lag: Math.random() * 1000,
    status: "active" as const,
  }));

  const auditEvents: AuditEvent[] = [
    {
      id: "evt-1",
      type: "info",
      title: "Cluster Initialized",
      description: "StreamForge cluster started with 20 worker nodes",
      timestamp: Date.now() - 5000,
      severity: "low",
    },
    {
      id: "evt-2",
      type: "info",
      title: "Partition Assignment",
      description: "50 partitions assigned across 20 workers",
      timestamp: Date.now() - 4000,
      severity: "low",
    },
    {
      id: "evt-3",
      type: "warning",
      title: "Bottleneck Detected",
      description: "Worker-04 and Worker-08 showing high CPU usage",
      timestamp: Date.now() - 2000,
      nodeId: "worker-04",
      severity: "medium",
    },
  ];

  const history: ThroughputPoint[] = Array.from({ length: 30 }, (_, i) => ({
    timestamp: new Date(Date.now() - (30 - i) * 2000).toLocaleTimeString(),
    value: 40000 + Math.random() * 20000,
  }));

  return {
    nodes,
    edges,
    auditEvents,
    throughput: 50000,
    history,
    health: {
      healthy: 20,
      degraded: 0,
      failed: 0,
      recovering: 0,
      total: 22,
    },
    partitions,
    bottlenecks: nodes.filter(n => n.isBottleneck),
    simulationMode: true,
  };
}

function updateMetrics(prev: StreamForgeData): StreamForgeData {
  const throughput = Math.max(30000, Math.min(80000, prev.throughput + (Math.random() - 0.5) * 10000));
  const timestamp = new Date().toLocaleTimeString();
  const history = [...prev.history.slice(-29), { timestamp, value: throughput }];

  const nodes = prev.nodes.map(node => {
    if (!node.metrics) return node;
    return {
      ...node,
      metrics: {
        ...node.metrics,
        cpu: Math.max(5, Math.min(95, node.metrics.cpu + (Math.random() - 0.5) * 10)),
        memory: Math.max(10, Math.min(90, node.metrics.memory + (Math.random() - 0.5) * 5)),
        stateStore: Math.max(5, Math.min(95, node.metrics.stateStore + (Math.random() - 0.5) * 8)),
        processingRate: Math.max(500, node.metrics.processingRate + (Math.random() - 0.5) * 500),
        latency: Math.max(2, node.metrics.latency + (Math.random() - 0.5) * 4),
        backlog: Math.max(0, node.metrics.backlog + (Math.random() - 0.5) * 100),
        throughput: Math.max(500, node.metrics.throughput + (Math.random() - 0.5) * 500),
      },
    };
  });

  const partitions = prev.partitions.map(partition => ({
    ...partition,
    lag: Math.max(0, partition.lag + (Math.random() - 0.5) * 100),
  }));

  const health: ClusterHealth = {
    healthy: nodes.filter(n => n.status === "healthy").length,
    degraded: nodes.filter(n => n.status === "degraded").length,
    failed: nodes.filter(n => n.status === "failed").length,
    recovering: nodes.filter(n => n.status === "recovering").length,
    total: nodes.length,
  };

  return {
    ...prev,
    nodes,
    partitions,
    history,
    throughput,
    health,
    bottlenecks: nodes.filter(n => n.isBottleneck || (n.metrics && n.metrics.cpu > 80)),
  };
}