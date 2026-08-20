import * as vscode from "vscode";
import { StreamForgeClient } from "../client/StreamForgeClient";

export class StreamForgePanel {
  public static currentPanel: StreamForgePanel | undefined;
  private readonly _panel: vscode.WebviewPanel;
  private _disposables: vscode.Disposable[] = [];
  private _client: StreamForgeClient;
  private _updateTimer: NodeJS.Timeout | undefined;
  private _viewType: string;

  public static createOrShow(
    extensionUri: vscode.Uri,
    viewId: string,
    title: string,
    client: StreamForgeClient
  ): StreamForgePanel {
    const column = vscode.window.activeTextEditor
      ? vscode.window.activeTextEditor.viewColumn
      : undefined;

    const panel = vscode.window.createWebviewPanel(
      viewId,
      title,
      column ?? vscode.ViewColumn.One,
      {
        enableScripts: true,
        retainContextWhenHidden: true,
        localResourceRoots: [vscode.Uri.joinPath(extensionUri, "media")],
      }
    );

    const streamForgePanel = new StreamForgePanel(panel, extensionUri, client, viewId);
    return streamForgePanel;
  }

  private constructor(
    panel: vscode.WebviewPanel,
    extensionUri: vscode.Uri,
    client: StreamForgeClient,
    viewType: string
  ) {
    this._panel = panel;
    this._client = client;
    this._viewType = viewType;

    this._update();
    this._panel.webview.html = this._getHtmlForWebview();

    this._panel.onDidDispose(() => this.dispose(), null, this._disposables);

    this._panel.webview.onDidReceiveMessage(
      (message) => this._handleMessage(message),
      null,
      this._disposables
    );

    // Update panel on data changes
    this._client.onDidChangeData(() => this._update());

    // Set up periodic updates
    const config = vscode.workspace.getConfiguration("streamforge");
    const interval = config.get("refreshInterval", 2000);
    this._updateTimer = setInterval(() => this._update(), interval);
  }

  public reveal() {
    this._panel.reveal();
  }

  private _handleMessage(message: any) {
    switch (message.command) {
      case "refresh":
        this._client.refresh();
        break;
      case "selectNode":
        vscode.window.showInformationMessage(`Selected node: ${message.nodeId}`);
        break;
      case "simulateFailure":
        this._client.simulateFailure(message.nodeId);
        break;
      case "simulateRecovery":
        this._client.simulateRecovery(message.nodeId);
        break;
      case "openSettings":
        vscode.commands.executeCommand("workbench.action.openSettings", "streamforge");
        break;
    }
  }

  private _update() {
    if (this._panel.visible) {
      const data = {
        nodes: this._client.getNodes(),
        edges: this._client.getEdges(),
        auditEvents: this._client.getAuditEvents(),
        throughput: this._client.getCurrentThroughput(),
        history: this._client.getThroughputHistory(),
        health: this._client.getClusterHealth(),
        partitions: this._client.getPartitionInfo(),
        bottlenecks: this._client.getBottlenecks(),
        simulationMode: this._client.isSimulationMode(),
      };
      this._panel.webview.postMessage({ type: "update", data });
    }
  }

  private _getHtmlForWebview(): string {
    const config = vscode.workspace.getConfiguration("streamforge");
    const theme = config.get("theme", "dark");

    return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>StreamForge Dashboard</title>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      background: ${theme === "dark" ? "#0f172a" : "#f8fafc"};
      color: ${theme === "dark" ? "#e2e8f0" : "#1e293b"};
      padding: 16px;
      min-height: 100vh;
    }
    .header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 20px;
      padding: 16px 20px;
      background: ${theme === "dark" ? "#1e293b" : "#ffffff"};
      border-radius: 12px;
      border: 1px solid ${theme === "dark" ? "#334155" : "#e2e8f0"};
      box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    .title {
      font-size: 20px;
      font-weight: 700;
      display: flex;
      align-items: center;
      gap: 10px;
    }
    .title-icon {
      width: 36px;
      height: 36px;
      display: flex;
      align-items: center;
      justify-content: center;
      background: linear-gradient(135deg, #06b6d4, #3b82f6);
      border-radius: 10px;
      font-size: 18px;
    }
    .status-badge {
      padding: 6px 12px;
      border-radius: 6px;
      font-size: 12px;
      font-weight: 600;
      letter-spacing: 0.5px;
    }
    .status-healthy { background: #dcfce7; color: #166534; }
    .status-degraded { background: #fef3c7; color: #92400e; }
    .status-failed { background: #fee2e2; color: #991b1b; }
    .status-recovering { background: #dbeafe; color: #1e40af; }
    .simulation-badge {
      background: #f3e8ff;
      color: #6b21a8;
      padding: 4px 8px;
      border-radius: 4px;
      font-size: 10px;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }
    .metrics-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 12px;
      margin-bottom: 20px;
    }
    .metric-card {
      padding: 16px;
      background: ${theme === "dark" ? "#1e293b" : "#ffffff"};
      border-radius: 12px;
      border: 1px solid ${theme === "dark" ? "#334155" : "#e2e8f0"};
      box-shadow: 0 2px 4px -1px rgba(0, 0, 0, 0.1);
      transition: transform 0.2s;
    }
    .metric-card:hover {
      transform: translateY(-2px);
    }
    .metric-label {
      font-size: 12px;
      color: ${theme === "dark" ? "#94a3b8" : "#64748b"};
      margin-bottom: 6px;
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }
    .metric-value {
      font-size: 28px;
      font-weight: 700;
      font-family: 'SF Mono', 'Fira Code', monospace;
    }
    .metric-value.cyan { color: #06b6d4; }
    .metric-value.green { color: #10b981; }
    .metric-value.amber { color: #f59e0b; }
    .metric-value.rose { color: #f43f5e; }
    .metric-sub { font-size: 12px; color: ${theme === "dark" ? "#64748b" : "#94a3b8"}; }
    .chart-container {
      background: ${theme === "dark" ? "#1e293b" : "#ffffff"};
      border-radius: 12px;
      border: 1px solid ${theme === "dark" ? "#334155" : "#e2e8f0"};
      padding: 20px;
      margin-bottom: 20px;
      box-shadow: 0 2px 4px -1px rgba(0, 0, 0, 0.1);
    }
    .chart-title {
      font-size: 16px;
      font-weight: 600;
      margin-bottom: 16px;
      display: flex;
      align-items: center;
      gap: 8px;
    }
    .node-list {
      display: flex;
      flex-direction: column;
      gap: 8px;
    }
    .node-item {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 12px 16px;
      background: ${theme === "dark" ? "#1e293b" : "#ffffff"};
      border-radius: 8px;
      border: 1px solid ${theme === "dark" ? "#334155" : "#e2e8f0"};
      cursor: pointer;
      transition: all 0.2s;
    }
    .node-item:hover {
      border-color: #06b6d4;
      transform: translateX(4px);
      box-shadow: 0 2px 8px rgba(6, 182, 212, 0.1);
    }
    .node-item.bottleneck {
      border-color: #f59e0b;
      background: ${theme === "dark" ? "#451a03" : "#fffbeb"};
    }
    .node-name {
      font-size: 14px;
      font-weight: 600;
    }
    .node-meta {
      font-size: 12px;
      color: ${theme === "dark" ? "#94a3b8" : "#64748b"};
      margin-top: 2px;
    }
    .node-metrics {
      display: flex;
      gap: 16px;
      margin-top: 8px;
    }
    .node-metric {
      font-size: 11px;
      color: ${theme === "dark" ? "#94a3b8" : "#64748b"};
    }
    .node-metric strong {
      color: ${theme === "dark" ? "#e2e8f0" : "#1e293b"};
      font-family: monospace;
    }
    .audit-list {
      display: flex;
      flex-direction: column;
      gap: 8px;
    }
    .audit-item {
      padding: 12px 16px;
      background: ${theme === "dark" ? "#1e293b" : "#ffffff"};
      border-radius: 8px;
      border: 1px solid ${theme === "dark" ? "#334155" : "#e2e8f0"};
      transition: all 0.2s;
    }
    .audit-item:hover {
      border-color: #06b6d4;
    }
    .audit-item.error { border-left: 3px solid #f43f5e; }
    .audit-item.warning { border-left: 3px solid #f59e0b; }
    .audit-item.recovery { border-left: 3px solid #10b981; }
    .audit-item.rebalance { border-left: 3px solid #06b6d4; }
    .audit-title {
      font-size: 14px;
      font-weight: 600;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    .audit-desc {
      font-size: 12px;
      color: ${theme === "dark" ? "#94a3b8" : "#64748b"};
      margin-top: 4px;
    }
    .audit-time {
      font-size: 11px;
      color: ${theme === "dark" ? "#64748b" : "#94a3b8"};
      font-family: monospace;
    }
    .section-title {
      font-size: 16px;
      font-weight: 600;
      margin-bottom: 12px;
      color: ${theme === "dark" ? "#e2e8f0" : "#1e293b"};
      display: flex;
      align-items: center;
      gap: 8px;
    }
    .progress-bar {
      width: 100%;
      height: 6px;
      background: ${theme === "dark" ? "#334155" : "#e2e8f0"};
      border-radius: 3px;
      overflow: hidden;
      margin-top: 4px;
    }
    .progress-fill {
      height: 100%;
      border-radius: 3px;
      transition: width 0.3s ease;
    }
    .progress-green { background: #10b981; }
    .progress-amber { background: #f59e0b; }
    .progress-rose { background: #f43f5e; }
    .progress-cyan { background: #06b6d4; }
    .action-button {
      padding: 8px 16px;
      border-radius: 8px;
      border: 1px solid ${theme === "dark" ? "#334155" : "#e2e8f0"};
      background: ${theme === "dark" ? "#334155" : "#f1f5f9"};
      color: ${theme === "dark" ? "#e2e8f0" : "#1e293b"};
      cursor: pointer;
      font-size: 13px;
      font-weight: 500;
      transition: all 0.2s;
      display: inline-flex;
      align-items: center;
      gap: 6px;
    }
    .action-button:hover {
      background: #06b6d4;
      color: white;
      border-color: #06b6d4;
      transform: translateY(-1px);
      box-shadow: 0 4px 12px rgba(6, 182, 212, 0.2);
    }
    .action-button.danger:hover {
      background: #f43f5e;
      border-color: #f43f5e;
      box-shadow: 0 4px 12px rgba(244, 63, 94, 0.2);
    }
    .action-button.success:hover {
      background: #10b981;
      border-color: #10b981;
      box-shadow: 0 4px 12px rgba(16, 185, 129, 0.2);
    }
    .toolbar {
      display: flex;
      gap: 8px;
      margin-bottom: 16px;
      flex-wrap: wrap;
    }
    .health-summary {
      display: flex;
      gap: 20px;
      margin-bottom: 16px;
      padding: 12px 16px;
      background: ${theme === "dark" ? "#1e293b" : "#ffffff"};
      border-radius: 8px;
      border: 1px solid ${theme === "dark" ? "#334155" : "#e2e8f0"};
    }
    .health-item {
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 13px;
    }
    .health-dot {
      width: 10px;
      height: 10px;
      border-radius: 50%;
    }
    .dot-green { background: #10b981; }
    .dot-amber { background: #f59e0b; }
    .dot-rose { background: #f43f5e; }
    .dot-blue { background: #06b6d4; }
    .empty-state {
      text-align: center;
      padding: 40px;
      color: ${theme === "dark" ? "#64748b" : "#94a3b8"};
    }
    .empty-state-icon {
      font-size: 48px;
      margin-bottom: 12px;
    }
    .empty-state-text {
      font-size: 14px;
    }
    .partition-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
      gap: 8px;
      margin-bottom: 20px;
    }
    .partition-item {
      padding: 8px;
      background: ${theme === "dark" ? "#1e293b" : "#ffffff"};
      border-radius: 6px;
      border: 1px solid ${theme === "dark" ? "#334155" : "#e2e8f0"};
      text-align: center;
    }
    .partition-item.active { border-color: #10b981; }
    .partition-item.rebalancing { border-color: #06b6d4; }
    .partition-item.stalled { border-color: #f43f5e; }
    .partition-id {
      font-size: 12px;
      font-weight: 600;
      font-family: monospace;
    }
    .partition-worker {
      font-size: 10px;
      color: ${theme === "dark" ? "#94a3b8" : "#64748b"};
      margin-top: 4px;
    }
    .partition-lag {
      font-size: 10px;
      color: ${theme === "dark" ? "#64748b" : "#94a3b8"};
      margin-top: 2px;
    }
    .bottleneck-alert {
      padding: 12px 16px;
      background: ${theme === "dark" ? "#451a03" : "#fffbeb"};
      border: 1px solid #f59e0b;
      border-radius: 8px;
      margin-bottom: 16px;
      display: flex;
      align-items: center;
      gap: 12px;
    }
    .bottleneck-alert-icon {
      font-size: 24px;
    }
    .bottleneck-alert-text {
      font-size: 13px;
      color: ${theme === "dark" ? "#fbbf24" : "#92400e"};
    }
    .bottleneck-alert-text strong {
      font-weight: 600;
    }
  </style>
</head>
<body>
  <div id="app">
    <div class="header">
      <div class="title">
        <div class="title-icon">⚡</div>
        <div>
          <div>StreamForge Dashboard</div>
          <div style="font-size: 12px; color: ${theme === "dark" ? "#94a3b8" : "#64748b"}; font-weight: 400;">
            Distributed Python Event Processor
          </div>
        </div>
      </div>
      <div style="display: flex; align-items: center; gap: 12px;">
        <span id="simulationBadge" class="simulation-badge" style="display: none;">Simulation</span>
        <div id="healthBadge" class="status-badge status-healthy">Loading...</div>
      </div>
    </div>
    <div class="toolbar">
      <button class="action-button" onclick="refresh()">🔄 Refresh</button>
      <button class="action-button danger" onclick="simulateFailure()">💥 Simulate Failure</button>
      <button class="action-button success" onclick="simulateRecovery()">🔧 Simulate Recovery</button>
      <button class="action-button" onclick="openSettings()">⚙️ Settings</button>
    </div>
    <div id="bottleneckAlert"></div>
    <div class="health-summary" id="healthSummary"></div>
    <div class="metrics-grid" id="metricsGrid"></div>
    <div class="chart-container">
      <div class="chart-title">📈 Throughput (msg/s)</div>
      <div id="throughputChart"></div>
    </div>
    <div class="section-title">🔗 Topology Nodes</div>
    <div class="node-list" id="nodeList"></div>
    <div class="section-title" style="margin-top: 20px;">📊 Partition Distribution</div>
    <div class="partition-grid" id="partitionGrid"></div>
    <div class="section-title" style="margin-top: 20px;">📋 Audit Trail</div>
    <div class="audit-list" id="auditList"></div>
  </div>

  <script>
    const vscode = acquireVsCodeApi();
    let currentData = null;

    function refresh() {
      vscode.postMessage({ command: 'refresh' });
    }

    function simulateFailure() {
      const nodeId = prompt('Enter worker ID (e.g., worker-04):');
      if (nodeId) {
        vscode.postMessage({ command: 'simulateFailure', nodeId });
      }
    }

    function simulateRecovery() {
      const nodeId = prompt('Enter worker ID (e.g., worker-04):');
      if (nodeId) {
        vscode.postMessage({ command: 'simulateRecovery', nodeId });
      }
    }

    function openSettings() {
      vscode.postMessage({ command: 'openSettings' });
    }

    function selectNode(nodeId) {
      vscode.postMessage({ command: 'selectNode', nodeId });
    }

    function renderHealth(data) {
      const health = data.health;
      const badge = document.getElementById('healthBadge');
      badge.textContent = \`\${health.healthy}/\${health.total} Healthy\`;
      badge.className = 'status-badge ' + 
        (health.healthy === health.total ? 'status-healthy' : 
         health.failed > 0 ? 'status-failed' :
         health.degraded > 0 ? 'status-degraded' : 'status-recovering');

      const summary = document.getElementById('healthSummary');
      summary.innerHTML = \`
        <div class="health-item"><span class="health-dot dot-green"></span> Healthy: \${health.healthy}</div>
        <div class="health-item"><span class="health-dot dot-amber"></span> Degraded: \${health.degraded}</div>
        <div class="health-item"><span class="health-dot dot-rose"></span> Failed: \${health.failed}</div>
        <div class="health-item"><span class="health-dot dot-blue"></span> Recovering: \${health.recovering}</div>
      \`;

      const simBadge = document.getElementById('simulationBadge');
      simBadge.style.display = data.simulationMode ? 'inline-block' : 'none';
    }

    function renderBottlenecks(data) {
      const container = document.getElementById('bottleneckAlert');
      if (data.bottlenecks.length > 0) {
        const names = data.bottlenecks.map(n => n.label).join(', ');
        container.innerHTML = \`
          <div class="bottleneck-alert">
            <div class="bottleneck-alert-icon">⚠️</div>
            <div class="bottleneck-alert-text">
              <strong>Bottleneck Detected:</strong> \${names} showing high resource usage
            </div>
          </div>
        \`;
      } else {
        container.innerHTML = '';
      }
    }

    function renderMetrics(data) {
      const grid = document.getElementById('metricsGrid');
      const throughput = data.throughput;
      const avgLatency = data.nodes
        .filter(n => n.metrics)
        .reduce((sum, n) => sum + n.metrics.latency, 0) / 
        data.nodes.filter(n => n.metrics).length;
      const totalBacklog = data.nodes
        .filter(n => n.metrics)
        .reduce((sum, n) => sum + n.metrics.backlog, 0);

      grid.innerHTML = \`
        <div class="metric-card">
          <div class="metric-label">Throughput</div>
          <div class="metric-value cyan">\${throughput.toLocaleString()}</div>
          <div class="metric-sub">messages per second</div>
        </div>
        <div class="metric-card">
          <div class="metric-label">Avg Latency</div>
          <div class="metric-value green">\${avgLatency.toFixed(1)}ms</div>
          <div class="metric-sub">processing time</div>
        </div>
        <div class="metric-card">
          <div class="metric-label">Total Partitions</div>
          <div class="metric-value amber">\${data.partitions.length}</div>
          <div class="metric-sub">across all workers</div>
        </div>
        <div class="metric-card">
          <div class="metric-label">Backlog</div>
          <div class="metric-value rose">\${Math.round(totalBacklog).toLocaleString()}</div>
          <div class="metric-sub">messages waiting</div>
        </div>
      \`;
    }

    function renderChart(data) {
      const chart = document.getElementById('throughputChart');
      const history = data.history;
      const max = Math.max(...history.map(h => h.value));
      const min = Math.min(...history.map(h => h.value));
      const range = max - min || 1;

      const chartHeight = 120;
      const barWidth = 6;
      const gap = 1;

      let bars = '';
      history.forEach((point, i) => {
        const height = ((point.value - min) / range) * chartHeight;
        const color = point.value > max * 0.8 ? '#f43f5e' : 
                     point.value > max * 0.6 ? '#f59e0b' : '#06b6d4';
        bars += \`<div style="width:\${barWidth}px;height:\${height}px;background:\${color};border-radius:2px;display:inline-block;margin-right:\${gap}px;vertical-align:bottom;" title="\${point.timestamp}: \${point.value} msg/s"></div>\`;
      });

      chart.innerHTML = \`
        <div style="display:flex;align-items:flex-end;height:\${chartHeight + 20}px;padding:10px 0;">
          \${bars}
        </div>
        <div style="display:flex;justify-content:space-between;font-size:10px;color:#64748b;margin-top:4px;">
          <span>\${history[0]?.timestamp || ''}</span>
          <span>\${history[history.length - 1]?.timestamp || ''}</span>
        </div>
      \`;
    }

    function renderNodes(data) {
      const list = document.getElementById('nodeList');
      const nodes = data.nodes;

      list.innerHTML = nodes.map(node => {
        const statusClass = node.status === 'healthy' ? 'status-healthy' : 
                           node.status === 'degraded' ? 'status-degraded' : 
                           node.status === 'recovering' ? 'status-recovering' : 'status-failed';
        const statusText = node.status.toUpperCase();
        const bottleneckClass = node.isBottleneck ? 'bottleneck' : '';
        const metrics = node.metrics ? \`
          <div style="margin-top:8px;">
            <div style="display:flex;justify-content:space-between;font-size:10px;color:#64748b;">
              <span>CPU</span><span>\${node.metrics.cpu.toFixed(1)}%</span>
            </div>
            <div class="progress-bar">
              <div class="progress-fill \${node.metrics.cpu > 80 ? 'progress-rose' : node.metrics.cpu > 60 ? 'progress-amber' : 'progress-green'}" style="width:\${node.metrics.cpu}%"></div>
            </div>
            <div style="display:flex;justify-content:space-between;font-size:10px;color:#64748b;margin-top:4px;">
              <span>Memory</span><span>\${node.metrics.memory.toFixed(1)}%</span>
            </div>
            <div class="progress-bar">
              <div class="progress-fill \${node.metrics.memory > 80 ? 'progress-rose' : node.metrics.memory > 60 ? 'progress-amber' : 'progress-green'}" style="width:\${node.metrics.memory}%"></div>
            </div>
            <div class="node-metrics">
              <div class="node-metric">Rate: <strong>\${node.metrics.processingRate.toFixed(0)}</strong> msg/s</div>
              <div class="node-metric">Latency: <strong>\${node.metrics.latency.toFixed(1)}</strong>ms</div>
              <div class="node-metric">Backlog: <strong>\${Math.round(node.metrics.backlog)}</strong></div>
            </div>
          </div>
        \` : '';

        return \`
          <div class="node-item \${bottleneckClass}" onclick="selectNode('\${node.id}')">
            <div>
              <div class="node-name">\${node.isBottleneck ? '⚠️ ' : ''}\${node.label}</div>
              <div class="node-meta">\${node.id} • \${node.partitions} partitions</div>
              \${metrics}
            </div>
            <span class="status-badge \${statusClass}">\${statusText}</span>
          </div>
        \`;
      }).join('');
    }

    function renderPartitions(data) {
      const grid = document.getElementById('partitionGrid');
      const partitions = data.partitions;

      grid.innerHTML = partitions.map(partition => {
        const statusClass = partition.status === 'active' ? 'active' : 
                           partition.status === 'rebalancing' ? 'rebalancing' : 'stalled';
        const statusIcon = partition.status === 'active' ? '✅' : 
                          partition.status === 'rebalancing' ? '🔄' : '❌';
        return \`
          <div class="partition-item \${statusClass}" title="Partition \${partition.id} - Worker: \${partition.workerId} - Lag: \${Math.round(partition.lag)}">
            <div class="partition-id">\${statusIcon} P\${partition.id}</div>
            <div class="partition-worker">\${partition.workerId}</div>
            <div class="partition-lag">Lag: \${Math.round(partition.lag)}</div>
          </div>
        \`;
      }).join('');
    }

    function renderAudit(data) {
      const list = document.getElementById('auditList');
      const events = data.auditEvents.slice(-20).reverse();

      if (events.length === 0) {
        list.innerHTML = \`
          <div class="empty-state">
            <div class="empty-state-icon">📋</div>
            <div class="empty-state-text">No audit events yet</div>
          </div>
        \`;
        return;
      }

      list.innerHTML = events.map(event => {
        const icon = event.type === 'error' ? '❌' : 
                    event.type === 'warning' ? '⚠️' : 
                    event.type === 'recovery' ? '🔧' : 
                    event.type === 'rebalance' ? '🔄' : '✅';
        const time = new Date(event.timestamp).toLocaleTimeString();
        const severityClass = event.severity === 'critical' ? 'error' : 
                             event.severity === 'high' ? 'error' : 
                             event.severity === 'medium' ? 'warning' : '';
        return \`
          <div class="audit-item \${severityClass}">
            <div class="audit-title">
              <span>\${icon} \${event.title}</span>
              <span class="audit-time">\${time}</span>
            </div>
            <div class="audit-desc">\${event.description}</div>
            \${event.nodeId ? \`<div class="audit-desc" style="margin-top:4px;color:#06b6d4;">Node: \${event.nodeId}</div>\` : ''}
          </div>
        \`;
      }).join('');
    }

    window.addEventListener('message', event => {
      const message = event.data;
      if (message.type === 'update') {
        currentData = message.data;
        renderHealth(message.data);
        renderBottlenecks(message.data);
        renderMetrics(message.data);
        renderChart(message.data);
        renderNodes(message.data);
        renderPartitions(message.data);
        renderAudit(message.data);
      }
    });

    // Initial render
    document.addEventListener('DOMContentLoaded', () => {
      const emptyState = \`
        <div class="empty-state">
          <div class="empty-state-icon">⚡</div>
          <div class="empty-state-text">Waiting for data...</div>
        </div>
      \`;
      document.getElementById('metricsGrid').innerHTML = emptyState;
      document.getElementById('nodeList').innerHTML = emptyState;
      document.getElementById('auditList').innerHTML = emptyState;
      document.getElementById('partitionGrid').innerHTML = emptyState;
    });
  </script>
</body>
</html>`;
  }

  public dispose() {
    StreamForgePanel.currentPanel = undefined;
    if (this._updateTimer) {
      clearInterval(this._updateTimer);
    }
    this._panel.dispose();
    while (this._disposables.length) {
      const x = this._disposables.pop();
      if (x) {
        x.dispose();
      }
    }
  }
}