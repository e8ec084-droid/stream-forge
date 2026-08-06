import React from "react";

export default function PartitionPanel({ partitions = [] }) {
  return (
    <div className="panel">
      <div className="panel-title">Per-Partition Breakdown</div>
      <div className="list">
        {partitions.map((partition) => (
          <div key={partition.partition} className="list-item">
            <div>
              <strong>Partition {partition.partition}</strong>
              <div className="small-text">{partition.health}</div>
            </div>
            <span>{partition.eps} eps</span>
          </div>
        ))}
      </div>
    </div>
  );
}
