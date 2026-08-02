import React from "react";

export default function LoadingState({ label = "Loading dashboard..." }) {
  return <div className="feedback-box">{label}</div>;
}
