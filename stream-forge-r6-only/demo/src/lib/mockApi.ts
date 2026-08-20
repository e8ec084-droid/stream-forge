import type {
  TopologyData,
  MetricsData,
  AuditEvent,
} from "@/types/topology";

const workerNames = [
  "Worker-01",
  "Worker-02",
  "Worker-03",
  "Worker-04",
  "Worker-05",
  "Worker-06",
  "Worker-07",
  "Worker-08",
  "Worker-09",
  "Worker-10",
  "Worker-11",
  "Worker-12",
  "Worker-13",
  "Worker-14",
  "Worker-15",
  "Worker-16",
  "Worker-17",
  "Worker-18",
  "Worker-19",
  "Worker-20",
];

let nodeStatuses: Record<string, string> = {};
let nodeMetrics: Record<string, any> = {};
let auditEvents: AuditEvent[] = [];
let throughputHistory: { timestamp: string; value: number }[] = [];
let currentThroughput = 50000;

// Initialize mock data
workerNames.forEach((name, i) => {
  const id = `worker-${String(i + 1).padStart(2, "0")}`;
  nodeStatuses[id] = "healthy";
  nodeMetrics[id] = {
    cpu: 30 + Math.random() * 40,
    memory: 40 + Math.random() * 30,
    stateStore: 20 + Math.random() * 50,
    processingRate: 2000 + Math.random() * 3000,
    latency: 5 + Math.random() * 20,
    partitions: Math.floor(1 + Math.random() * 3),
  };
});

// Generate initial history
for (let i = 0; i < 20; i++) {
  const timestamp = new Date(Date.now() - (20 - i) * 2000).toLocaleTimeString();
  throughputHistory.push({
    timestamp,
    value: 40000 + Math.random() * 20000,
  });
}

// Simulate initial audit events
const initialEvents: AuditEvent[] = [
  {
    id: "evt-1",
    type: "info",
    title: "Cluster Initialized",
    description: "StreamForge cluster started with 20 worker nodes",
    timestamp: Date.now() - 5000,
  },
  {
    id: "evt-2",
    type: "info",
    title: "Partition Assignment",
    description: "50 partitions assigned across 20 workers",
    timestamp: Date.now() - 4000,
  },
  {
    id: "evt-3",
    type: "info",
    title: "State Store Ready",
    description: "RocksDB changelog initialized for all workers",
    timestamp: Date.now() - 3000,
  },
];

auditEvents = [...initialEvents];

export const mockApi = {
  async getTopology(): Promise<TopologyData> {
    await delay(500);

    const sourceNodes = [
      {
        id: "kafka-ingest",
        label: "Kafka Ingest",
        type: "source" as const,
        status: "healthy" as const,
        partitions: 50,
      },
    ];

    const processorNodes = workerNames.map((name, i) => {
      const id = `worker-${String(i + 1).padStart(2, "0")}`;
      return {
        id,
        label: name,
        type: "processor" as const,
        status: nodeStatuses[id] as "healthy" | "degraded" | "recovering",
        partitions: nodeMetrics[id].partitions,
      };
    });

    const sinkNodes = [
      {
        id: "aggregate-sink",
        label: "Aggregate Sink",
        type: "sink" as const,
        status: "healthy" as const,
        partitions: 1,
      },
    ];

    const edges = [
      ...processorNodes.map((node) => ({
        id: `edge-kafka-${node.id}`,
        source: "kafka-ingest",
        target: node.id,
        status: "healthy" as const,
        throughput: nodeMetrics[node.id].processingRate,
      })),
      ...processorNodes.map((node) => ({
        id: `edge-${node.id}-sink`,
        source: node.id,
        target: "aggregate-sink",
        status: "healthy" as const,
        throughput: nodeMetrics[node.id].processingRate,
      })),
    ];

    return {
      nodes: [...sourceNodes, ...processorNodes, ...sinkNodes],
      edges,
    };
  },

  async getMetrics(): Promise<MetricsData> {
    await delay(100);

    // Simulate throughput fluctuation
    currentThroughput = Math.max(
      30000,
      Math.min(80000, currentThroughput + (Math.random() - 0.5) * 10000)
    );

    const timestamp = new Date().toLocaleTimeString();
    throughputHistory = [
      ...throughputHistory.slice(-19),
      { timestamp, value: currentThroughput },
    ];

    // Update node metrics
    Object.keys(nodeMetrics).forEach((id) => {
      nodeMetrics[id] = {
        ...nodeMetrics[id],
        cpu: Math.max(5, Math.min(95, nodeMetrics[id].cpu + (Math.random() - 0.5) * 10)),
        memory: Math.max(10, Math.min(90, nodeMetrics[id].memory + (Math.random() - 0.5) * 5)),
        stateStore: Math.max(5, Math.min(95, nodeMetrics[id].stateStore + (Math.random() - 0.5) * 8)),
        processingRate: Math.max(500, nodeMetrics[id].processingRate + (Math.random() - 0.5) * 500),
        latency: Math.max(2, nodeMetrics[id].latency + (Math.random() - 0.5) * 4),
      };
    });

    return {
      throughput: Math.round(currentThroughput),
      history: throughputHistory,
      nodes: nodeMetrics,
    };
  },

  async getAuditEvents(): Promise<AuditEvent[]> {
    await delay(100);

    // Randomly generate events
    if (Math.random() < 0.3) {
      const eventTypes = ["info", "warning", "recovery", "error"];
      const type = eventTypes[Math.floor(Math.random() * eventTypes.length)];
      const workerId = `worker-${String(Math.floor(Math.random() * 20) + 1).padStart(2, "0")}`;

      const eventMap = {
        info: {
          title: "Checkpoint Completed",
          description: "State checkpoint persisted to RocksDB",
        },
        warning: {
          title: "High Latency Detected",
          description: "Processing latency exceeded threshold",
        },
        recovery: {
          title: "Worker Recovered",
          description: "State restored from changelog successfully",
        },
        error: {
          title: "Worker Degraded",
          description: "Worker experiencing resource pressure",
        },
      };

      const event: AuditEvent = {
        id: `evt-${Date.now()}`,
        type: type as AuditEvent["type"],
        title: eventMap[type as keyof typeof eventMap].title,
        description: eventMap[type as keyof typeof eventMap].description,
        timestamp: Date.now(),
        nodeId: workerId,
      };

      auditEvents = [...auditEvents, event];

      // Update node status based on event
      if (type === "error") {
        nodeStatuses[workerId] = "degraded";
      } else if (type === "recovery") {
        nodeStatuses[workerId] = "healthy";
      }
    }

    return auditEvents;
  },
};

function delay(ms: number) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}