import React, { useState } from "react";
import Week1 from "./pages/Week1";
import Week2 from "./pages/Week2";
import MidReview from "./pages/MidReview";

export default function App() {
  const [activeTab, setActiveTab] = useState("week1");

  return (
    <div className="app-shell">
      <header className="topbar">
        <h1>Stream Forge - R6 React Flow Dashboard Developer</h1>
        <p>Week 1, Week 2, and Mid-Project Review coding deliverables</p>
      </header>

      <div className="tabs">
        <button className={activeTab === "week1" ? "active" : ""} onClick={() => setActiveTab("week1")}>Week 1</button>
        <button className={activeTab === "week2" ? "active" : ""} onClick={() => setActiveTab("week2")}>Week 2</button>
        <button className={activeTab === "mid" ? "active" : ""} onClick={() => setActiveTab("mid")}>Mid-Review</button>
      </div>

      {activeTab === "week1" && <Week1 />}
      {activeTab === "week2" && <Week2 />}
      {activeTab === "mid" && <MidReview />}
    </div>
  );
}
