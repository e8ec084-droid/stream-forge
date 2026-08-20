# StreamForge Dashboard for VS Code

Real-time distributed stream processing dashboard for StreamForge, a pure-Python event processor built on Kafka and Faust.

## Features

### Week 1: Scaffold & Baseline
- ✅ VS Code extension scaffold with TypeScript
- ✅ Custom activity bar view container
- ✅ Topology tree view with source/processor/sink groups
- ✅ Mock API client with simulated data
- ✅ Dark/light theme support
- ✅ Status bar integration

### Week 2: DAG Visualization
- ✅ Live topology visualization with node status indicators
- ✅ Real-time metrics polling (2s interval)
- ✅ Node health badges (healthy/degraded/failed/recovering)
- ✅ Throughput chart with historical data
- ✅ Edge animations and status highlighting
- ✅ Bottleneck node detection

### Mid-Project: Audit & Monitoring
- ✅ Live audit trail panel with event types
- ✅ Real-time throughput numbers
- ✅ Per-partition breakdown view
- ✅ Window correctness status indicators
- ✅ Worker health summary
- ✅ Partition distribution visualization

### Week 3: Telemetry & Rebalancing
- ✅ Per-stream metrics (CPU, memory, state store)
- ✅ Worker health monitoring
- ✅ Partition rebalancing visualization
- ✅ Worker crash/recovery simulation
- ✅ Real-time metrics feed
- ✅ Backlog monitoring

### Week 4: Production Polish
- ✅ Prometheus metrics integration ready
- ✅ Bottleneck node highlighting
- ✅ Cross-browser compatible webviews
- ✅ Performance optimizations
- ✅ Final demo walkthrough
- ✅ Enterprise-grade error handling

## Installation

1. Clone the repository
2. Run `npm install`
3. Press `F5` to launch the extension in debug mode

## Usage

### Commands
- `StreamForge: Refresh Dashboard` - Refresh all dashboard views
- `StreamForge: Connect to Cluster` - Set API endpoint
- `StreamForge: Simulate Worker Failure` - Test failure handling
- `StreamForge: Simulate Worker Recovery` - Test recovery flow
- `StreamForge: Show Topology` - Open topology view
- `StreamForge: Show Metrics` - Open metrics view
- `StreamForge: Show Audit Trail` - Open audit view

### Views
- **Topology** - Visual DAG of Kafka → Workers → Sink
- **Metrics** - Real-time throughput, latency, and resource usage
- **Audit Trail** - Event log with recovery/error tracking

## Configuration
