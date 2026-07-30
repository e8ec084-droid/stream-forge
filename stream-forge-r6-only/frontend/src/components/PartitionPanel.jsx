import React from "react";

export default function PartitionPanel({ partitions = [] }) {
  return (
    <div className="panel">
      <div className="panel-title">Per-Partition Breakdown</div>
      <div className="list">
        {partitions.map((item) => (
          <div key={item.partition} className="list-item">
            <div>
              <strong>Partition {item.partition}</strong>
              <div className="small-text">{item.health}</div>
            </div>
            <span>{item.eps} eps</span>
          </div>
        ))}
      </div>
    </div>
  );
}
