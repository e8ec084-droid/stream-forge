export type NodeStatus = "healthy" | "degraded" | "recovering" | "failed";
export type NodeType = "source" | "processor" | "sink";
export type EdgeStatus = "healthy" | "degraded" | "rebalancing";

export interface TopologyNode {
  id: string;
  label: string;
  type: NodeType;
  status: NodeStatus;
  partitions: number;
  isBottleneck?: boolean;
  metrics?: NodeMetrics;
}

export interface NodeMetrics {
  cpu: number;
  memory: number;
  stateStore: number;
  processingRate: number;
  latency: number;
  backlog: number;
  throughput: number;
}

export interface TopologyEdge {
  id: string;
  source: string;
  target: string;
  status: EdgeStatus;
  throughput: number;
  isBottleneck?: boolean;
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
  severity: "low" | "medium" | "high" | "critical";
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

export interface StreamForgeData {
  nodes: TopologyNode[];
  edges: TopologyEdge[];
  auditEvents: AuditEvent[];
  throughput: number;
  history: ThroughputPoint[];
  health: ClusterHealth;
  partitions: PartitionInfo[];
  bottlenecks: TopologyNode[];
  simulationMode: boolean;
}