import React from "react";
import { AuditEvent } from "../types/streamforge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { CheckCircle, AlertTriangle, XCircle, RefreshCw, ArrowLeftRight, Info } from "lucide-react";

interface AuditPanelProps {
  events: AuditEvent[];
}

export const AuditPanel: React.FC<AuditPanelProps> = ({ events }) => {
  const getEventIcon = (type: string) => {
    switch (type) {
      case "error":
        return <XCircle className="w-4 h-4 text-rose-500" />;
      case "warning":
        return <AlertTriangle className="w-4 h-4 text-amber-500" />;
      case "recovery":
        return <RefreshCw className="w-4 h-4 text-green-500" />;
      case "rebalance":
        return <ArrowLeftRight className="w-4 h-4 text-blue-500" />;
      default:
        return <Info className="w-4 h-4 text-cyan-500" />;
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case "critical":
        return "bg-rose-500/20 text-rose-300 border-rose-500/30";
      case "high":
        return "bg-rose-500/10 text-rose-300 border-rose-500/20";
      case "medium":
        return "bg-amber-500/10 text-amber-300 border-amber-500/20";
      default:
        return "bg-green-500/10 text-green-300 border-green-500/20";
    }
  };

  return (
    <Card className="bg-slate-900 border-slate-800">
      <CardHeader>
        <CardTitle className="text-lg font-semibold text-white">Audit Trail</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {events.slice(-20).reverse().map((event) => (
            <div
              key={event.id}
              className={`p-4 rounded-lg border ${
                event.type === "error" ? "border-rose-500/30 bg-rose-500/5" :
                event.type === "warning" ? "border-amber-500/30 bg-amber-500/5" :
                event.type === "recovery" ? "border-green-500/30 bg-green-500/5" :
                event.type === "rebalance" ? "border-blue-500/30 bg-blue-500/5" :
                "border-slate-700 bg-slate-800/50"
              }`}
            >
              <div className="flex items-start justify-between">
                <div className="flex items-start gap-3">
                  {getEventIcon(event.type)}
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="font-medium text-sm">{event.title}</span>
                      <Badge className={getSeverityColor(event.severity)}>
                        {event.severity}
                      </Badge>
                    </div>
                    <p className="text-sm text-slate-400 mt-1">{event.description}</p>
                    {event.nodeId && (
                      <p className="text-xs text-cyan-400 mt-1">Node: {event.nodeId}</p>
                    )}
                  </div>
                </div>
                <span className="text-xs text-slate-500 font-mono">
                  {new Date(event.timestamp).toLocaleTimeString()}
                </span>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
};