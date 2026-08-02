import React from "react";

export default function Shell({ title, subtitle, children }) {
  return (
    <div className="app-shell">
      <header className="page-header">
        <h1>{title}</h1>
        <p>{subtitle}</p>
      </header>
      {children}
    </div>
  );
}
