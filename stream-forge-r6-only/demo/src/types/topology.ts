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
}

export interface PartitionInfo {
  id: number;
  workerId: string;
  lag: number;
  status: "active" | "rebalancing" | "stalled";
}