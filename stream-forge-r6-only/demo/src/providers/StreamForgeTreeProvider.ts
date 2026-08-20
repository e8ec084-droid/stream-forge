import * as vscode from "vscode";
import { StreamForgeClient, TopologyNode } from "../client/StreamForgeClient";

export class StreamForgeTreeProvider implements vscode.TreeDataProvider<TopologyTreeItem> {
  private _onDidChangeTreeData = new vscode.EventEmitter<TopologyTreeItem | undefined | null | void>();
  readonly onDidChangeTreeData = this._onDidChangeTreeData.event;

  constructor(private client: StreamForgeClient) {
    client.onDidChangeData(() => this._onDidChangeTreeData.fire());
  }

  refresh(): void {
    this._onDidChangeTreeData.fire();
  }

  getTreeItem(element: TopologyTreeItem): vscode.TreeItem {
    return element;
  }

  getChildren(element?: TopologyTreeItem): Thenable<TopologyTreeItem[]> {
    if (!element) {
      return Promise.resolve(this.getTopLevelItems());
    }
    return Promise.resolve(this.getChildrenForNode(element));
  }

  private getTopLevelItems(): TopologyTreeItem[] {
    const nodes = this.client.getNodes();
    const health = this.client.getClusterHealth();

    const groups = [
      { 
        id: "sources", 
        label: `Sources (${nodes.filter((n) => n.type === "source").length})`, 
        nodes: nodes.filter((n) => n.type === "source") 
      },
      { 
        id: "processors", 
        label: `Processors (${nodes.filter((n) => n.type === "processor").length})`, 
        nodes: nodes.filter((n) => n.type === "processor") 
      },
      { 
        id: "sinks", 
        label: `Sinks (${nodes.filter((n) => n.type === "sink").length})`, 
        nodes: nodes.filter((n) => n.type === "sink") 
      },
    ];

    return groups
      .filter((g) => g.nodes.length > 0)
      .map((group) => {
        const item = new TopologyTreeItem(
          group.label,
          vscode.TreeItemCollapsibleState.Expanded,
          "group"
        );
        item.contextValue = "group";
        item.iconPath = new vscode.ThemeIcon(
          group.id === "sources" ? "arrow-up" : 
          group.id === "processors" ? "gear" : "arrow-down"
        );
        item.children = group.nodes;
        item.description = group.id === "processors" 
          ? `${health.healthy}/${health.total} healthy` 
          : undefined;
        return item;
      });
  }

  private getChildrenForNode(element: TopologyTreeItem): TopologyTreeItem[] {
    if (element.contextValue === "group" && element.children) {
      return element.children.map((node) => {
        const item = new TopologyTreeItem(
          node.label,
          vscode.TreeItemCollapsibleState.None,
          "worker"
        );
        item.contextValue = "worker";
        item.id = node.id;
        item.description = `${node.status} • ${node.partitions} partitions`;
        item.iconPath = this.getStatusIcon(node.status);
        item.tooltip = this.getNodeTooltip(node);
        
        if (node.isBottleneck) {
          item.description += " • ⚠️ Bottleneck";
        }
        
        return item;
      });
    }
    return [];
  }

  private getStatusIcon(status: string): vscode.ThemeIcon {
    switch (status) {
      case "healthy":
        return new vscode.ThemeIcon("check", new vscode.ThemeColor("charts.green"));
      case "degraded":
        return new vscode.ThemeIcon("warning", new vscode.ThemeColor("charts.yellow"));
      case "recovering":
        return new vscode.ThemeIcon("sync", new vscode.ThemeColor("charts.blue"));
      default:
        return new vscode.ThemeIcon("error", new vscode.ThemeColor("charts.red"));
    }
  }

  private getNodeTooltip(node: TopologyNode): vscode.MarkdownString {
    const tooltip = new vscode.MarkdownString();
    tooltip.appendMarkdown(`**${node.label}**\n\n`);
    tooltip.appendMarkdown(`ID: \`${node.id}\`\n\n`);
    tooltip.appendMarkdown(`Status: **${node.status}**\n\n`);
    tooltip.appendMarkdown(`Partitions: ${node.partitions}\n\n`);
    
    if (node.isBottleneck) {
      tooltip.appendMarkdown(`⚠️ **Bottleneck Node**\n\n`);
    }
    
    if (node.metrics) {
      tooltip.appendMarkdown(`---\n\n`);
      tooltip.appendMarkdown(`CPU: ${node.metrics.cpu.toFixed(1)}%\n\n`);
      tooltip.appendMarkdown(`Memory: ${node.metrics.memory.toFixed(1)}%\n\n`);
      tooltip.appendMarkdown(`Processing Rate: ${node.metrics.processingRate.toFixed(0)} msg/s\n\n`);
      tooltip.appendMarkdown(`Latency: ${node.metrics.latency.toFixed(1)}ms\n\n`);
      tooltip.appendMarkdown(`Backlog: ${node.metrics.backlog.toFixed(0)} messages\n\n`);
    }
    
    return tooltip;
  }
}

export class TopologyTreeItem extends vscode.TreeItem {
  children?: TopologyNode[];

  constructor(
    public readonly label: string,
    public readonly collapsibleState: vscode.TreeItemCollapsibleState,
    public readonly contextValue: string
  ) {
    super(label, collapsibleState);
  }
}