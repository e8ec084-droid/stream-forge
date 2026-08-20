import React, { useState, useEffect, useCallback } from "react";
import { StreamForgeDashboard } from "./components/StreamForgeDashboard";
import { StreamForgeProvider } from "./context/StreamForgeContext";

export default function App() {
  return (
    <StreamForgeProvider>
      <div className="min-h-screen bg-slate-950 text-slate-100">
        <StreamForgeDashboard />
      </div>
    </StreamForgeProvider>
  );
}