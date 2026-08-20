import * as vscode from "vscode";

export interface TopologyNode {
  id: string;
  label: string;
  type: "source" | "processor" | "sink";
  status: "healthy" | "degraded" | "recovering" | "failed";
  partitions: number;
  metrics?: NodeMetrics;
  isBottleneck?: boolean;
}

export interface TopologyEdge {
  id: string;
  source: string;
  target: string;
  status: "healthy" | "degraded";
  throughput: number;
  isBottleneck?: boolean;
}

export interface NodeMetrics {
  cpu: number;
  memory: number;
  stateStore: number;
  processingRate: number;
  latency: number;
  partitions: number;
  backlog: number;
}

export interface ClusterHealth {
  healthy: number;
  degraded: number;
  failed: number;
  recovering: number;
  total: number;
}

export interface AuditEvent {
  id: string;
  type: "info" | "warning" | "error" | "recovery" | "rebalance";
  title: string;
  description: string;
  timestamp: number;
  nodeId?: string;
  severity?: "low" | "medium" | "high" | "critical";
}

export interface ThroughputPoint {
  timestamp: string;
  value: number;
  partition?: number;
}

export interface PartitionInfo {
  id: number;
  workerId: string;
  lag: number;
  status: "active" | "rebalancing" | "stalled";
}

export class StreamForgeClient {
  private _onDidChangeData = new vscode.EventEmitter<void>();
  readonly onDidChangeData = this._onDidChangeData.event;

  private _nodes: TopologyNode[] = [];
  private _edges: TopologyEdge[] = [];
  private _auditEvents: AuditEvent[] = [];
  private _throughputHistory: ThroughputPoint[] = [];
  private _partitionInfo: PartitionInfo[] = [];
  private _currentThroughput = 50000;
  private _connected = false;
  private _endpoint = "http://localhost:8000";
  private _refreshTimer: NodeJS.Timeout | undefined;
  private _simulationMode = true;

  constructor() {
    this.initializeMockData();
    this.startPolling();
  }

  private initializeMockData() {
    const workerNames = Array.from({ length: 20 }, (_, i) => 
      `Worker-${String(i + 1).padStart(2, "0")}`
    );

    // Create source node
    this._nodes = [
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
          partitions: 50,
          backlog: 0,
        },
      },
    ];

    // Create worker nodes
    workerNames.forEach((name, i) => {
      const id = `worker-${String(i + 1).padStart(2, "0")}`;
      const isBottleneck = i === 3 || i === 7; // Simulate bottlenecks
      this._nodes.push({
        id,
        label: name,
        type: "processor",
        status: "healthy",
        partitions: Math.floor(1 + Math.random() * 3),
        isBottleneck,
        metrics: {
          cpu: isBottleneck ? 85 + Math.random() * 10 : 30 + Math.random() * 40,
          memory: isBottleneck ? 80 + Math.random() * 10 : 40 + Math.random() * 30,
          stateStore: 20 + Math.random() * 50,
          processingRate: isBottleneck ? 1500 + Math.random() * 500 : 2000 + Math.random() * 3000,
          latency: isBottleneck ? 30 + Math.random() * 20 : 5 + Math.random() * 20,
          partitions: Math.floor(1 + Math.random() * 3),
          backlog: isBottleneck ? 5000 + Math.random() * 5000 : Math.random() * 1000,
        },
      });
    });

    // Create sink node
    this._nodes.push({
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
        partitions: 1,
        backlog: 0,
      },
    });

    // Create edges
    this._edges = this._nodes
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

    // Create partition info
    for (let i = 0; i < 50; i++) {
      const workerIndex = i % 20;
      this._partitionInfo.push({
        id: i,
        workerId: `worker-${String(workerIndex + 1).padStart(2, "0")}`,
        lag: Math.random() * 1000,
        status: "active",
      });
    }

    // Initialize audit events
    this._auditEvents = [
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
        type: "info",
        title: "State Store Ready",
        description: "RocksDB changelog initialized for all workers",
        timestamp: Date.now() - 3000,
        severity: "low",
      },
      {
        id: "evt-4",
        type: "warning",
        title: "Bottleneck Detected",
        description: "Worker-04 and Worker-08 showing high CPU usage",
        timestamp: Date.now() - 2000,
        nodeId: "worker-04",
        severity: "medium",
      },
    ];

    // Initialize throughput history
    for (let i = 0; i < 30; i++) {
      const timestamp = new Date(Date.now() - (30 - i) * 2000).toLocaleTimeString();
      this._throughputHistory.push({
        timestamp,
        value: 40000 + Math.random() * 20000,
      });
    }
  }

  private startPolling() {
    const config = vscode.workspace.getConfiguration("streamforge");
    const interval = config.get("refreshInterval", 2000);

    this._refreshTimer = setInterval(() => {
      this.updateMetrics();
      this._onDidChangeData.fire();
    }, interval);
  }

  private updateMetrics() {
    // Update throughput
    this._currentThroughput = Math.max(
      30000,
      Math.min(80000, this._currentThroughput + (Math.random() - 0.5) * 10000)
    );

    const timestamp = new Date().toLocaleTimeString();
    this._throughputHistory = [
      ...this._throughputHistory.slice(-29),
      { timestamp, value: this._currentThroughput },
    ];

    // Update node metrics
    this._nodes.forEach((node) => {
      if (node.metrics) {
        node.metrics = {
          ...node.metrics,
          cpu: Math.max(5, Math.min(95, node.metrics.cpu + (Math.random() - 0.5) * 10)),
          memory: Math.max(10, Math.min(90, node.metrics.memory + (Math.random() - 0.5) * 5)),
          stateStore: Math.max(5, Math.min(95, node.metrics.stateStore + (Math.random() - 0.5) * 8)),
          processingRate: Math.max(500, node.metrics.processingRate + (Math.random() - 0.5) * 500),
          latency: Math.max(2, node.metrics.latency + (Math.random() - 0.5) * 4),
          backlog: Math.max(0, node.metrics.backlog + (Math.random() - 0.5) * 100),
        };
      }
    });

    // Update partition info
    this._partitionInfo.forEach((partition) => {
      partition.lag = Math.max(0, partition.lag + (Math.random() - 0.5) * 100);
    });

    // Randomly generate events
    if (Math.random() < 0.15) {
      this.generateRandomEvent();
    }
  }

  private generateRandomEvent() {
    const eventTypes: Array<AuditEvent["type"]> = ["info", "warning", "recovery", "error", "rebalance"];
    const type = eventTypes[Math.floor(Math.random() * eventTypes.length)];
    const workerId = `worker-${String(Math.floor(Math.random() * 20) + 1).padStart(2, "0")}`;

    const eventMap: Record<string, { title: string; description: string; severity: AuditEvent["severity"] }> = {
      info: {
        title: "Checkpoint Completed",
        description: "State checkpoint persisted to RocksDB",
        severity: "low",
      },
      warning: {
        title: "High Latency Detected",
        description: "Processing latency exceeded threshold",
        severity: "medium",
      },
      recovery: {
        title: "Worker Recovered",
        description: "State restored from changelog successfully",
        severity: "low",
      },
      error: {
        title: "Worker Degraded",
        description: "Worker experiencing resource pressure",
        severity: "high",
      },
      rebalance: {
        title: "Partition Rebalance",
        description: "Partitions redistributed across workers",
        severity: "medium",
      },
    };

    this._auditEvents = [
      ...this._auditEvents,
      {
        id: `evt-${Date.now()}`,
        type,
        title: eventMap[type].title,
        description: eventMap[type].description,
        timestamp: Date.now(),
        nodeId: workerId,
        severity: eventMap[type].severity,
      },
    ];

    // Update node status based on event
    const node = this._nodes.find((n) => n.id === workerId);
    if (node) {
      if (type === "error") {
        node.status = "degraded";
      } else if (type === "recovery") {
        node.status = "healthy";
      } else if (type === "rebalance") {
        node.status = "recovering";
        setTimeout(() => {
          node.status = "healthy";
        }, 3000);
      }
    }
  }

  connect(endpoint: string) {
    this._endpoint = endpoint;
    this._connected = true;
    this._simulationMode = false;
    this._onDidChangeData.fire();
  }

  refresh() {
    this.updateMetrics();
    this._onDidChangeData.fire();
  }

  async simulateFailure(nodeId: string) {
    const node = this._nodes.find((n) => n.id === nodeId);
    if (node) {
      node.status = "failed";
      node.metrics = {
        ...node.metrics!,
        cpu: 0,
        memory: 0,
        processingRate: 0,
        latency: 0,
      };

      // Rebalance partitions
      this._partitionInfo.forEach((partition) => {
        if (partition.workerId === nodeId) {
          partition.status = "rebalancing";
          const newWorker = this._nodes.find(
            (n) => n.type === "processor" && n.status === "healthy"
          );
          if (newWorker) {
            setTimeout(() => {
              partition.workerId = newWorker.id;
              partition.status = "active";
            }, 2000);
          }
        }
      });

      this._auditEvents = [
        ...this._auditEvents,
        {
          id: `evt-${Date.now()}`,
          type: "error",
          title: "Worker Failure",
          description: `${node.label} has crashed, initiating partition rebalance`,
          timestamp: Date.now(),
          nodeId: node.id,
          severity: "critical",
        },
      ];
      this._onDidChangeData.fire();
    }
  }

  async simulateRecovery(nodeId: string) {
    const node = this._nodes.find((n) => n.id === nodeId);
    if (node) {
      node.status = "recovering";
      this._auditEvents = [
        ...this._auditEvents,
        {
          id: `evt-${Date.now()}`,
          type: "recovery",
          title: "Worker Recovery Started",
          description: `${node.label} is recovering from changelog`,
          timestamp: Date.now(),
          nodeId: node.id,
          severity: "medium",
        },
      ];
      this._onDidChangeData.fire();

      // Simulate recovery completion
      setTimeout(() => {
        node.status = "healthy";
        node.metrics = {
          ...node.metrics!,
          cpu: 30 + Math.random() * 20,
          memory: 40 + Math.random() * 20,
          processingRate: 2000 + Math.random() * 1000,
          latency: 5 + Math.random() * 10,
        };
        this._auditEvents = [
          ...this._auditEvents,
          {
            id: `evt-${Date.now()}`,
            type: "info",
            title: "Worker Recovered",
            description: `${node.label} has fully recovered and rejoined the cluster`,
            timestamp: Date.now(),
            nodeId: node.id,
            severity: "low",
          },
        ];
        this._onDidChangeData.fire();
      }, 3000);
    }
  }

  getNodes(): TopologyNode[] {
    return this._nodes;
  }

  getEdges(): TopologyEdge[] {
    return this._edges;
  }

  getAuditEvents(): AuditEvent[] {
    return this._auditEvents;
  }

  getThroughputHistory(): ThroughputPoint[] {
    return this._throughputHistory;
  }

  getCurrentThroughput(): number {
    return Math.round(this._currentThroughput);
  }

  getPartitionInfo(): PartitionInfo[] {
    return this._partitionInfo;
  }

  getClusterHealth(): ClusterHealth {
    const healthy = this._nodes.filter((n) => n.status === "healthy").length;
    const degraded = this._nodes.filter((n) => n.status === "degraded").length;
    const failed = this._nodes.filter((n) => n.status === "failed").length;
    const recovering = this._nodes.filter((n) => n.status === "recovering").length;
    return { healthy, degraded, failed, recovering, total: this._nodes.length };
  }

  getBottlenecks(): TopologyNode[] {
    return this._nodes.filter((n) => n.isBottleneck || (n.metrics && n.metrics.cpu > 80));
  }

  isSimulationMode(): boolean {
    return this._simulationMode;
  }

  dispose() {
    if (this._refreshTimer) {
      clearInterval(this._refreshTimer);
    }
  }
}