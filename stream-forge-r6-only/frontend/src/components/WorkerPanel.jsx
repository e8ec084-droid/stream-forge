import React from "react";

export default function WorkerPanel({ workers = [] }) {
  return (
    <div className="panel">
      <div className="panel-title">Worker Health</div>
      <div className="list">
        {workers.map((worker) => (
          <div key={worker.id} className="list-item">
            <div>
              <strong>{worker.id}</strong>
              {worker.lag !== undefined && <div className="small-text">Lag: {worker.lag}</div>}
            </div>
            <span className={`badge ${worker.health}`}>{worker.health}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
