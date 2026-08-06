import React, { useEffect, useState } from "react";
import { getMidReviewData } from "../api";
import MetricCard from "../components/MetricCard";
import PartitionPanel from "../components/PartitionPanel";
import WindowingPanel from "../components/WindowingPanel";
import WorkerPanel from "../components/WorkerPanel";

export default function MidReview() {
  const [data, setData] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    getMidReviewData().then(setData).catch((err) => setError(err.message));
  }, []);

  return (
    <section>
      <div className="section-header">
        <h2>Mid-Project Review - Audit Dashboard</h2>
        <p>Live audit visualization for throughput, partition-level breakdown, and windowing-correctness validation.</p>
      </div>

      {error && <div className="error-box">{error}</div>}

      <div className="summary-grid">
        <MetricCard title="Current Throughput" value={`${data?.throughput?.current ?? "--"} eps`} />
        <MetricCard title="Target Throughput" value={`${data?.throughput?.target ?? "--"} eps`} />
        <MetricCard title="Audit Status" value={data?.throughput?.status ?? "--"} />
      </div>

      <div className="audit-grid">
        <PartitionPanel partitions={data?.partitions || []} />
        <WindowingPanel windowing={data?.windowing} />
        <WorkerPanel workers={data?.workers || []} />
      </div>
    </section>
  );
}
