import React from "react";

export default function MetricCard({ title, value }) {
  return (
    <div className="metric-card">
      <h3>{title}</h3>
      <p className="metric-value">{value}</p>
    </div>
  );
}
