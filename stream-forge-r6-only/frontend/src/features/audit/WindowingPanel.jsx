import React from "react";

export default function WindowingPanel({ windowing }) {
  return (
    <div className="panel">
      <div className="panel-title">Windowing Correctness</div>
      <div className="audit-box">
        Rolling average: {windowing?.rolling_average_correct ? "Pass" : "Fail"}
      </div>
      <div className="audit-box" style={{ marginTop: "10px" }}>
        Late arrivals: {windowing?.late_arrivals_handled ? "Handled" : "Not handled"}
      </div>
      <div className="small-text" style={{ marginTop: "10px" }}>
        {windowing?.note}
      </div>
    </div>
  );
}
