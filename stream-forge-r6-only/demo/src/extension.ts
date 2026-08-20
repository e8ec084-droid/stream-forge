import * as vscode from "vscode";
import { StreamForgePanel } from "./panels/StreamForgePanel";
import { StreamForgeClient } from "./client/StreamForgeClient";
import { StreamForgeTreeProvider } from "./providers/StreamForgeTreeProvider";
import { StreamForgeStatusBar } from "./statusBar/StreamForgeStatusBar";

export function activate(context: vscode.ExtensionContext) {
  console.log("StreamForge Dashboard extension is now active!");

  // Initialize client
  const client = new StreamForgeClient();

  // Register tree view provider
  const treeProvider = new StreamForgeTreeProvider(client);
  const treeView = vscode.window.createTreeView("streamforgeTopology", {
    treeDataProvider: treeProvider,
    showCollapseAll: true,
  });

  // Create webview panels
  const topologyPanel = StreamForgePanel.createOrShow(
    context.extensionUri,
    "streamforgeTopology",
    "StreamForge Topology",
    client
  );

  const metricsPanel = StreamForgePanel.createOrShow(
    context.extensionUri,
    "streamforgeMetrics",
    "StreamForge Metrics",
    client
  );

  const auditPanel = StreamForgePanel.createOrShow(
    context.extensionUri,
    "streamforgeAudit",
    "StreamForge Audit Trail",
    client
  );

  // Create status bar
  const statusBar = new StreamForgeStatusBar(client);

  // Register commands
  const refreshCommand = vscode.commands.registerCommand("streamforge.refresh", () => {
    client.refresh();
    treeProvider.refresh();
    vscode.window.showInformationMessage("StreamForge dashboard refreshed");
  });

  const connectCommand = vscode.commands.registerCommand("streamforge.connect", async () => {
    const config = vscode.workspace.getConfiguration("streamforge");
    const endpoint = await vscode.window.showInputBox({
      prompt: "Enter StreamForge API endpoint",
      value: config.get("apiEndpoint", "http://localhost:8000"),
      placeHolder: "http://localhost:8000",
    });

    if (endpoint) {
      await config.update("apiEndpoint", endpoint, vscode.ConfigurationTarget.Global);
      client.connect(endpoint);
      vscode.window.showInformationMessage(`Connected to StreamForge at ${endpoint}`);
    }
  });

  const simulateFailureCommand = vscode.commands.registerCommand(
    "streamforge.simulateFailure",
    async (node: any) => {
      if (node) {
        await client.simulateFailure(node.id);
        vscode.window.showWarningMessage(`Simulated failure on ${node.label}`);
      } else {
        const nodeId = await vscode.window.showInputBox({
          prompt: "Enter worker ID (e.g., worker-04)",
          placeHolder: "worker-04",
        });
        if (nodeId) {
          await client.simulateFailure(nodeId);
          vscode.window.showWarningMessage(`Simulated failure on ${nodeId}`);
        }
      }
    }
  );

  const simulateRecoveryCommand = vscode.commands.registerCommand(
    "streamforge.simulateRecovery",
    async (node: any) => {
      if (node) {
        await client.simulateRecovery(node.id);
        vscode.window.showInformationMessage(`Simulated recovery on ${node.label}`);
      } else {
        const nodeId = await vscode.window.showInputBox({
          prompt: "Enter worker ID (e.g., worker-04)",
          placeHolder: "worker-04",
        });
        if (nodeId) {
          await client.simulateRecovery(nodeId);
          vscode.window.showInformationMessage(`Simulated recovery on ${nodeId}`);
        }
      }
    }
  );

  const showTopologyCommand = vscode.commands.registerCommand("streamforge.showTopology", () => {
    topologyPanel.reveal();
  });

  const showMetricsCommand = vscode.commands.registerCommand("streamforge.showMetrics", () => {
    metricsPanel.reveal();
  });

  const showAuditCommand = vscode.commands.registerCommand("streamforge.showAudit", () => {
    auditPanel.reveal();
  });

  // Register all disposables
  context.subscriptions.push(
    treeView,
    topologyPanel,
    metricsPanel,
    auditPanel,
    statusBar,
    refreshCommand,
    connectCommand,
    simulateFailureCommand,
    simulateRecoveryCommand,
    showTopologyCommand,
    showMetricsCommand,
    showAuditCommand
  );
}

export function deactivate() {}