import * as vscode from "vscode";
import { StreamForgeClient } from "../client/StreamForgeClient";

export class StreamForgeStatusBar {
  private _statusBarItem: vscode.StatusBarItem;
  private _client: StreamForgeClient;
  private _timer: NodeJS.Timeout | undefined;

  constructor(client: StreamForgeClient) {
    this._client = client;
    this._statusBarItem = vscode.window.createStatusBarItem(
      vscode.StatusBarAlignment.Right,
      100
    );
    this._statusBarItem.command = "streamforge.showTopology";
    this._statusBarItem.show();
    this.update();

    // Update every 2 seconds
    this._timer = setInterval(() => this.update(), 2000);
  }

  private update() {
    const health = this._client.getClusterHealth();
    const throughput = this._client.getCurrentThroughput();
    const bottlenecks = this._client.getBottlenecks();

    if (health.total === 0) {
      this._statusBarItem.text = "$(radio-tower) StreamForge: Connecting...";
      this._statusBarItem.color = "#94a3b8";
      return;
    }

    const healthy = health.healthy === health.total;
    const hasBottlenecks = bottlenecks.length > 0;

    this._statusBarItem.text = `$(radio-tower) StreamForge: ${health.healthy}/${health.total} workers | $(dashboard) ${throughput.toLocaleString()} msg/s${hasBottlenecks ? ' | $(warning) Bottleneck' : ''}`;

    if (health.failed > 0) {
      this._statusBarItem.color = "#f43f5e";
      this._statusBarItem.tooltip = `${health.failed} workers failed`;
    } else if (health.degraded > 0 || hasBottlenecks) {
      this._statusBarItem.color = "#f59e0b";
      this._statusBarItem.tooltip = hasBottlenecks 
        ? `Bottleneck detected: ${bottlenecks.map(n => n.label).join(', ')}`
        : `${health.degraded} workers degraded`;
    } else {
      this._statusBarItem.color = "#10b981";
      this._statusBarItem.tooltip = "All systems operational";
    }
  }

  dispose() {
    if (this._timer) {
      clearInterval(this._timer);
    }
    this._statusBarItem.dispose();
  }
}